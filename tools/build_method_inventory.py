#!/usr/bin/env python3
"""
Deterministic IL2CPP method/body inventory for Block Strike 6.5.1 (build 2492).

Ground truth: lib/armeabi-v7a/libil2cpp.so + global-metadata.dat from
original/apk/com.rexetstudio.blockstrike_6.5.1_2492.apk (Unity 2019.2.3f1,
metadata v24.2, 61,617 methods across 61 images).

For every Assembly-CSharp / Assembly-CSharp-firstpass method the tool records:
  - metadata identity (declaring type, name, token, parameter count)
  - binary body evidence (RVA, estimated size, trivial-body classification
    decoded from the actual ARMv7 machine code)
  - exported C# body classification from client/Assets (stub vs real body)
  - static reachability from APK-confirmed entry points (scene/prefab
    MonoBehaviour roots, Unity/NGUI/Photon message names, UnityEvent
    m_MethodName persistent calls, AnimationEvent functionName calls)

Reachability edges (all decoded from the binary, no guessing):
  - direct BL / conditional BL call instructions
  - cross-method unconditional B tail calls
  - raw function-pointer words in code literal pools (delegate targets)
  - Il2Cpp metadata-usage MethodRef slot references (ldftn/delegate metadata)
  - RTA-style closure: when game code references a game type's TypeInfo
    (newobj / static access / cast), that type's vtable-slot methods plus
    .ctor/.cctor become virtually reachable (covers coroutine MoveNext,
    interface dispatch and overrides)
  - string-literal name references that exactly match a game method name
    (SendMessage / Invoke / StartCoroutine("...") style dispatch)

Known over/under-approximations are documented in docs/method-inventory.md.

Outputs (all deterministic, sorted, no timestamps):
  tools/method-inventory/inventory.json   full per-method inventory
  tools/method-inventory/priorities.json  ranked lost-implementation worklist
  docs/method-inventory.md                human-readable report

Usage:
  python3 tools/build_method_inventory.py
"""

import bisect
import json
import re
import struct
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from il2cpp_inspect import Il2CppInspector  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CLIENT = ROOT / "client"
OUT_DIR = ROOT / "tools" / "method-inventory"
GAME_IMAGES = ("Assembly-CSharp.dll", "Assembly-CSharp-firstpass.dll")

# Unity runtime magic methods (invoked by the engine by name).
UNITY_MAGIC = {
    "Awake", "Start", "Update", "FixedUpdate", "LateUpdate",
    "OnEnable", "OnDisable", "OnDestroy",
    "OnApplicationFocus", "OnApplicationPause", "OnApplicationQuit",
    "OnLevelWasLoaded", "OnGUI",
    "OnTriggerEnter", "OnTriggerExit", "OnTriggerStay",
    "OnTriggerEnter2D", "OnTriggerExit2D", "OnTriggerStay2D",
    "OnCollisionEnter", "OnCollisionExit", "OnCollisionStay",
    "OnCollisionEnter2D", "OnCollisionExit2D", "OnCollisionStay2D",
    "OnControllerColliderHit", "OnParticleCollision", "OnJointBreak",
    "OnBecameVisible", "OnBecameInvisible", "OnWillRenderObject",
    "OnPreCull", "OnPreRender", "OnPostRender", "OnRenderObject",
    "OnRenderImage", "OnAnimatorIK", "OnAnimatorMove", "OnAudioFilterRead",
    "OnTransformChildrenChanged", "OnTransformParentChanged",
    "OnMouseDown", "OnMouseUp", "OnMouseEnter", "OnMouseExit",
    "OnMouseOver", "OnMouseDrag", "OnMouseUpAsButton",
}

# NGUI UICamera dispatches these via SendMessage (ground-truth NGUI behavior,
# confirmed by UICamera string literals in the 6.5.1 binary).
NGUI_MESSAGES = {
    "OnHover", "OnPress", "OnSelect", "OnClick", "OnDoubleClick",
    "OnDragStart", "OnDrag", "OnDragOver", "OnDragOut", "OnDragEnd",
    "OnDrop", "OnInput", "OnTooltip", "OnScroll", "OnKey", "OnNavigate",
    "OnPan", "OnSubmit",
}

# PUN 1.x NetworkingPeer.SendMonoMessage callback names.
PHOTON_MESSAGES = {
    "OnConnectedToPhoton", "OnLeftRoom", "OnMasterClientSwitched",
    "OnPhotonCreateRoomFailed", "OnPhotonJoinRoomFailed", "OnCreatedRoom",
    "OnJoinedLobby", "OnLeftLobby", "OnFailedToConnectToPhoton",
    "OnConnectionFail", "OnDisconnectedFromPhoton", "OnPhotonInstantiate",
    "OnReceivedRoomListUpdate", "OnJoinedRoom", "OnPhotonPlayerConnected",
    "OnPhotonPlayerDisconnected", "OnPhotonRandomJoinFailed",
    "OnConnectedToMaster", "OnPhotonSerializeView",
    "OnPhotonCustomRoomPropertiesChanged", "OnPhotonPlayerPropertiesChanged",
    "OnUpdatedFriendList", "OnCustomAuthenticationFailed",
    "OnCustomAuthenticationResponse", "OnWebRpcResponse",
    "OnOwnershipRequest", "OnLobbyStatisticsUpdate",
    "OnPhotonPlayerActivityChanged", "OnOwnershipTransfered",
}

MESSAGE_NAMES = UNITY_MAGIC | NGUI_MESSAGES | PHOTON_MESSAGES

CS_KEYWORDS = {
    "if", "else", "for", "foreach", "while", "do", "switch", "try", "catch",
    "finally", "lock", "using", "fixed", "checked", "unchecked", "unsafe",
    "return", "throw", "new", "base", "this", "typeof", "sizeof", "default",
    "delegate", "get", "set", "add", "remove",
}

BX_LR = 0xE12FFF1E


# --------------------------------------------------------------------------
# ELF helpers
# --------------------------------------------------------------------------

def code_segment_end(so: bytes) -> int:
    """File-size of the first (executable) PT_LOAD segment of libil2cpp.so."""
    e_phoff = struct.unpack_from("<I", so, 0x1C)[0]
    e_phentsize, e_phnum = struct.unpack_from("<HH", so, 0x2A)
    for i in range(e_phnum):
        p_type, p_offset, _va, _pa, p_filesz, _msz, p_flags, _al = struct.unpack_from(
            "<8I", so, e_phoff + i * e_phentsize
        )
        if p_type == 1 and p_flags & 1:  # PT_LOAD, executable
            return p_offset + p_filesz
    raise ValueError("No executable PT_LOAD segment found")


# --------------------------------------------------------------------------
# Binary-side inventory
# --------------------------------------------------------------------------

def classify_binary_body(so: bytes, rva: int, size: int) -> str:
    """Classify the actual ARMv7 machine code of a method body."""
    if rva == 0:
        return "no_code"
    if size >= 4:
        w0 = struct.unpack_from("<I", so, rva)[0]
        if w0 == BX_LR:
            return "empty"
        if size >= 8:
            w1 = struct.unpack_from("<I", so, rva + 4)[0]
            if w1 == BX_LR and (w0 & 0xFFFFF000) == 0xE3A00000:
                imm = w0 & 0xFF
                return f"ret_const_{imm}"
    if size <= 16:
        return "tiny"
    return "substantive"


def code_registration_pointers(insp, code_end: int):
    """All function pointers from Il2CppCodeRegistration side tables
    (generic method instantiations, invokers, custom-attribute generators,
    reverse-pinvoke wrappers, unresolved-virtual-call thunks). They are not
    metadata methods but they bound method sizes inside the code segment.
    The struct is located via its known codeGenModules table (61 @ 0x023C50A8)."""
    so = insp.so
    needle = struct.pack("<II", 61, 0x023C50A8)
    pos = so.find(needle)
    if pos < 0:
        return []
    base = pos - 56  # codeGenModulesCount is field 14 of Il2CppCodeRegistration
    fields = struct.unpack_from("<16I", so, base)
    ptrs = set()
    for cnt_i, ptr_i in ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9)):
        count, table_va = fields[cnt_i], fields[ptr_i]
        if not count or not table_va:
            continue
        off = insp.v2o(table_va)
        for p in struct.unpack_from(f"<{count}I", so, off):
            p &= ~1
            if 0 < p < code_end:
                ptrs.add(p)
    return sorted(ptrs)


def build_binary_tables(insp: Il2CppInspector):
    """Per-method identity + RVA/size/binary-body classification."""
    so = insp.so
    code_end = code_segment_end(so)
    total_methods = insp.methodsSize // 32

    starts = sorted({rva & ~1 for rva in insp.method_rvas.values() if rva})
    start_arr = starts
    extra = code_registration_pointers(insp, code_end)
    bounds = sorted(set(starts) | set(extra))
    nxt_of = {}
    for i, b in enumerate(bounds):
        nxt_of[b] = bounds[i + 1] if i + 1 < len(bounds) else code_end
    sizes = {s: nxt_of[s] - s for s in starts}

    # method index -> declaring type / name / token / param count
    num_images = insp.imagesSize // 40
    mi_image = {}
    for img_idx in range(num_images):
        im = struct.unpack_from("<10i", insp.meta, insp.imagesOffset + img_idx * 40)
        img_name = insp.get_str(im[0])
        t_start, t_count = im[2], im[3]
        for t_idx in range(t_start, t_start + t_count):
            m_start, m_count = insp.type_methods[t_idx]
            for mi in range(m_start, m_start + m_count):
                mi_image[mi] = (img_name, t_idx)

    methods = []
    for mi in range(total_methods):
        mf = struct.unpack_from("<6i4H", insp.meta, insp.methodsOffset + mi * 32)
        name = insp.get_str(mf[0])
        decl_type = mf[1]
        token = struct.unpack_from("<I", insp.meta, insp.methodsOffset + mi * 32 + 20)[0]
        params = mf[9]
        rva = insp.method_rvas.get(mi, 0) & ~1
        size = sizes.get(rva, 0) if rva else 0
        img_name, t_idx = mi_image.get(mi, ("?", decl_type))
        methods.append({
            "mi": mi,
            "image": img_name,
            "type_idx": t_idx,
            "type": insp.type_names[t_idx] if t_idx < len(insp.type_names) else f"Type{t_idx}",
            "name": name,
            "token": token,
            "params": params,
            "rva": rva,
            "size": size,
            "bin": classify_binary_body(so, rva, size),
        })
    return methods, start_arr, sizes, code_end


# --------------------------------------------------------------------------
# Call graph + literal references (numpy word scan over the code segment)
# --------------------------------------------------------------------------

def scan_code_references(insp, methods, start_arr, sizes, code_end):
    import numpy as np

    so = insp.so
    buf = np.frombuffer(so[: code_end & ~3], dtype="<u4")
    addrs = np.arange(len(buf), dtype=np.int64) * 4

    rva_to_mi = {}
    for m in methods:
        if m["rva"]:
            rva_to_mi.setdefault(m["rva"], m["mi"])

    def owner(addr: int):
        """Method start containing file offset addr, or None."""
        i = bisect.bisect_right(start_arr, addr) - 1
        if i < 0:
            return None
        s = start_arr[i]
        return s if addr < s + sizes.get(s, 0) else None

    cond = buf >> 28
    top = (buf >> 24) & 0x0F

    call_edges = defaultdict(set)   # src method rva -> {dst method rva}
    for opc in (0x0B, 0x0A):  # BL, B (tail call)
        mask = (top == opc) & (cond != 0xF)
        idx = np.nonzero(mask)[0]
        imm = (buf[idx] & 0xFFFFFF).astype(np.int64)
        imm = np.where(imm & 0x800000, imm - 0x1000000, imm)
        tgts = addrs[idx] + 8 + imm * 4
        for a, t in zip(addrs[idx].tolist(), tgts.tolist()):
            if t in rva_to_mi:
                src = owner(a)
                if src is not None and (opc == 0x0B or t != src):
                    call_edges[src].add(t)

    typeinfo_refs = defaultdict(set)  # src method rva -> {typedef_idx}
    name_literals = set()             # string literals that look like identifiers
    starts_set = set(start_arr)
    so_len = len(so)

    def consume_va(src: int, va: int) -> None:
        """A method at `src` computed/loaded address `va`: classify it."""
        va &= 0xFFFFFFFF
        if va in insp.bss_usage:
            kind, idx = insp.bss_usage[va]
            if kind == 3:  # MethodRef (ldftn / delegate metadata)
                mrva = insp.method_rvas.get(idx, 0) & ~1
                if mrva:
                    call_edges[src].add(mrva)
            elif kind in (1, 2):  # TypeInfo / Il2CppType -> typedef via types table
                td = insp.type_ref_to_typedef(idx)
                if td >= 0:
                    typeinfo_refs[src].add(td)
            elif kind == 5:  # StringLiteral
                lit = insp.get_lit(idx)
                if lit and len(lit) < 64 and re.fullmatch(r"[A-Za-z_]\w*", lit):
                    name_literals.add(lit)
        elif va in starts_set and va != src:
            call_edges[src].add(va)

    # 1) Absolute literal words (pool entries holding raw addresses).
    vals = buf.astype(np.int64)
    interesting = np.array(sorted(starts_set | set(insp.bss_usage)), dtype=np.int64)
    a_mask = np.isin(vals, interesting)
    for a, v in zip(addrs[a_mask].tolist(), vals[a_mask].tolist()):
        src = owner(a)
        if src is not None:
            consume_va(src, v)

    # 2) PC-relative metadata access, the dominant 2019.2 ARMv7 codegen pattern:
    #       ldr rd, [pc, #imm]      ; rd = delta word from the literal pool
    #       add rx, pc, rd          ; rx = VA            (init flag / usage slot)
    #    or ldr rx, [pc, rd]        ; rx = *(pc + delta) (indirect pointer cell)
    ldr_pc_imm = np.nonzero((buf & 0x0FFF0000) == 0x059F0000)[0]
    for i in ldr_pc_imm.tolist():
        w = int(buf[i])
        rd = (w >> 12) & 0xF
        pool = i * 4 + 8 + (w & 0xFFF)
        if pool % 4 or pool + 4 > code_end:
            continue
        delta = int(buf[pool // 4])
        src = owner(i * 4)
        if src is None:
            continue
        # search the next few instructions for the consumer of rd
        for j in range(i + 1, min(i + 8, len(buf))):
            w2 = int(buf[j])
            if (w2 & 0x0FFF0FF0) == 0x008F0000 and (w2 & 0xF) == rd:
                consume_va(src, j * 4 + 8 + delta)      # add rx, pc, rd
                break
            if (w2 & 0x0FFF0FF0) == 0x079F0000 and (w2 & 0xF) == rd:
                cell = (j * 4 + 8 + delta) & 0xFFFFFFFF  # ldr rx, [pc, rd]
                off = insp.v2o(cell)
                if 0 <= off <= so_len - 4:
                    consume_va(src, struct.unpack_from("<I", so, off)[0])
                break
            if (w2 & 0x0C000000) == 0 and ((w2 >> 12) & 0xF) == rd:
                break  # rd overwritten by a data-processing instruction
    return call_edges, typeinfo_refs, name_literals


# --------------------------------------------------------------------------
# Metadata vtables / nested types
# --------------------------------------------------------------------------

def parse_vtables(insp):
    hdr = struct.unpack_from("<2I62i", insp.meta, 0)
    vtable_methods_off = hdr[36]
    total_methods = insp.methodsSize // 32
    vtables = {}
    for t_idx in range(insp.num_types):
        tf = struct.unpack_from("<23i", insp.meta, insp.typeDefinitionsOffset + t_idx * 92)
        vt_start = tf[15]
        vt_count = (tf[19] >> 16) & 0xFFFF
        if vt_start < 0 or not vt_count:
            continue
        slots = []
        for k in range(vt_count):
            enc = struct.unpack_from("<I", insp.meta, vtable_methods_off + (vt_start + k) * 4)[0]
            kind, idx = (enc >> 29) & 7, enc & 0x1FFFFFFF
            if kind == 3 and idx < total_methods:
                slots.append(idx)
        if slots:
            vtables[t_idx] = sorted(set(slots))
    return vtables


# --------------------------------------------------------------------------
# Scene / prefab usage (ground truth: serialized client assets)
# --------------------------------------------------------------------------

def rg_capture(pattern: str, paths, replace: str) -> list:
    cmd = ["rg", "-o", "--no-filename", "-N", pattern, "-r", replace] + [str(p) for p in paths]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(CLIENT / "Assets"))
    return res.stdout.splitlines()


def scan_scene_usage():
    """GUIDs of MonoBehaviour scripts referenced by serialized scenes/prefabs,
    plus UnityEvent m_MethodName and AnimationEvent functionName targets."""
    asset_dirs = [
        d.name for d in sorted((CLIENT / "Assets").iterdir())
        if d.is_dir() and d.name not in ("Scripts", "Plugins", "RecoveredGeometry", "Editor")
    ]
    used_guids = set(rg_capture(
        r"m_Script: \{fileID: 11500000, guid: ([0-9a-f]{32})", asset_dirs, "$1"))
    event_names = set(rg_capture(r"m_MethodName: (\w+)", asset_dirs, "$1"))
    anim_names = set(rg_capture(r"functionName: (\w+)", asset_dirs, "$1"))

    guid_to_class = {}
    for src_dir in (CLIENT / "Assets" / "Scripts", CLIENT / "Assets" / "Plugins"):
        for meta in sorted(src_dir.rglob("*.cs.meta")):
            m = re.search(r"guid: ([0-9a-f]{32})", meta.read_text(encoding="utf-8"))
            if m:
                guid_to_class[m.group(1)] = meta.name[: -len(".cs.meta")]
    used_classes = {guid_to_class[g] for g in used_guids if g in guid_to_class}
    return used_classes, event_names, anim_names


# --------------------------------------------------------------------------
# Exported C# source classification
# --------------------------------------------------------------------------

STUB_BODIES = {
    "": "empty",
    "return false;": "ret_false",
    "return true;": "ret_true",
    "return null;": "ret_null",
    "return default;": "ret_default",
    "return 0;": "ret_zero",
    "return 0f;": "ret_zero",
    "return 0.0;": "ret_zero",
    "return 0L;": "ret_zero",
    "return default(Color);": "ret_default",
    "return default(Vector2);": "ret_default",
    "return default(Vector3);": "ret_default",
    "return default(Vector4);": "ret_default",
    "return default(Quaternion);": "ret_default",
    "return default(Rect);": "ret_default",
}

TYPE_DECL_RE = re.compile(r"\b(class|struct|interface|enum)\s+([A-Za-z_]\w*)")
METHOD_NAME_RE = re.compile(r"([A-Za-z_][\w.]*)(?:<[^()]*>)?\s*\($")
PROP_RE = re.compile(r"^[\w\[\],<>.?\s]+\s([A-Za-z_][\w.]*)$")
EXPR_BODY_RE = re.compile(r"^.*?\s([A-Za-z_][\w.]*)(\([^)]*\))?\s*=>\s*(.*);$")


def classify_body(body_lines) -> str:
    text = " ".join(l.strip() for l in body_lines if l.strip())
    text = re.sub(r"//ILSpy[^;]*", "", text).strip()
    return STUB_BODIES.get(text, "body")


def parse_cs_file(path: Path):
    """Yield (type_name, method_name, kind) for every method/accessor body."""
    out = []
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    stack = []  # (block_kind, name)
    header: list = []
    body_start = None
    body_depth = 0
    depth = 0

    def cur_type():
        for kind, name in reversed(stack):
            if kind == "type":
                return name
        return None

    def cur_prop():
        for kind, name in reversed(stack):
            if kind == "prop":
                return name
        return None

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        line = raw.split("//")[0].rstrip() if "//" in raw and '"' not in raw else raw.rstrip()
        stripped = line.strip()
        i += 1
        if not stripped or stripped.startswith(("[", "#", "//")):
            continue

        # expression-bodied member at type level: classify directly
        m = EXPR_BODY_RE.match(stripped)
        if m and stripped.endswith(";") and "{" not in stripped and cur_type():
            name = m.group(1).split(".")[-1]
            expr = m.group(3).strip()
            kind = STUB_BODIES.get(f"return {expr};", "body")
            prop_prefix = "" if m.group(2) else "get_"
            if name not in CS_KEYWORDS:
                out.append((cur_type(), (prop_prefix + name) if prop_prefix else name, kind))
            continue

        opens = stripped.count("{") - stripped.count("}")
        if stripped == "{" or stripped.endswith("{"):
            head = " ".join(header).strip() if stripped == "{" else stripped[:-1].strip()
            header = []
            tm = TYPE_DECL_RE.search(head)
            first_word = head.split("(")[0].strip().split()[-1] if head else ""
            if tm:
                stack.append(("type", tm.group(2)))
            elif head in ("get", "set") and cur_prop():
                stack.append(("method", f"{head}_{cur_prop()}"))
                body_start, body_depth = i, len(stack)
            elif "(" in head and first_word not in CS_KEYWORDS and METHOD_NAME_RE.search(head.split("(")[0] + "("):
                name = METHOD_NAME_RE.search(head.split("(")[0] + "(").group(1).split(".")[-1]
                if name == cur_type():  # constructor / static constructor
                    name = ".cctor" if re.search(r"\bstatic\b", head) else ".ctor"
                if name in CS_KEYWORDS or cur_type() is None:
                    stack.append(("other", None))
                else:
                    if body_start is None:
                        stack.append(("method", name))
                        body_start, body_depth = i, len(stack)
                    else:
                        stack.append(("other", None))
            elif head and "(" not in head and "=" not in head and PROP_RE.match(head) and cur_type():
                stack.append(("prop", PROP_RE.match(head).group(1).split(".")[-1]))
            else:
                stack.append(("other", None))
            depth += 1
            # same-line close (e.g. "{ }")
            extra = stripped.count("}")
            for _ in range(extra):
                if stack:
                    k, nm = stack.pop()
                    depth -= 1
                    if k == "method" and body_start is not None and len(stack) + 1 == body_depth:
                        out.append((cur_type(), nm, classify_body(lines[body_start:i - 1])))
                        body_start = None
            continue

        if stripped.startswith("}"):
            closes = stripped.count("}") - stripped.count("{")
            for _ in range(max(closes, 1) if stripped.startswith("}") else 0):
                if not stack:
                    break
                k, nm = stack.pop()
                depth -= 1
                if k == "method" and body_start is not None and len(stack) + 1 == body_depth:
                    out.append((cur_type(), nm, classify_body(lines[body_start:i - 1])))
                    body_start = None
            continue

        if stripped.endswith(";") or stripped.endswith(","):
            header = []
            continue
        if opens == 0:
            header.append(stripped)
    return out


def scan_sources():
    src_bodies = defaultdict(list)  # (type, method) -> [kind]
    roots = [CLIENT / "Assets" / "Scripts", CLIENT / "Assets" / "Plugins"]
    files = []
    for r in roots:
        files.extend(sorted(r.rglob("*.cs")))
    for f in files:
        for type_name, method_name, kind in parse_cs_file(f):
            if type_name:
                src_bodies[(type_name, method_name)].append(kind)
    return src_bodies


# --------------------------------------------------------------------------
# Reachability
# --------------------------------------------------------------------------

def compute_reachability(insp, methods, call_edges, typeinfo_refs, name_literals,
                         vtables, used_classes, event_names, anim_names):
    by_rva = defaultdict(list)
    game_type_methods = defaultdict(list)   # type_idx -> [method dict]
    game_type_by_name = defaultdict(list)   # simple type name -> [type_idx]
    for m in methods:
        if m["rva"]:
            by_rva[m["rva"]].append(m)
        if m["image"] in GAME_IMAGES:
            game_type_methods[m["type_idx"]].append(m)
            game_type_by_name[m["type"].split(".")[-1]].append(m["type_idx"])

    dispatch_names = set(event_names) | set(anim_names)

    roots_direct = set()
    root_types = set()
    for cls in sorted(used_classes):
        for t_idx in game_type_by_name.get(cls, []):
            root_types.add(t_idx)
            for m in game_type_methods[t_idx]:
                if (m["name"] in MESSAGE_NAMES or m["name"] in dispatch_names
                        or m["name"] in (".ctor", ".cctor")):
                    if m["rva"]:
                        roots_direct.add(m["rva"])

    # String-literal name dispatch (SendMessage/Invoke/StartCoroutine by name)
    name_dispatch = set()
    for m in methods:
        if m["image"] in GAME_IMAGES and m["rva"] and m["name"] in name_literals \
                and not m["name"].startswith((".", "get_", "set_")):
            name_dispatch.add(m["rva"])

    def bfs(seeds, allow_virtual: bool):
        seen = set(seeds)
        frontier = list(seeds)
        ref_types = set(root_types) if allow_virtual else set()
        processed_types = set()
        while frontier:
            nxt = []
            for rva in frontier:
                for dst in call_edges.get(rva, ()):
                    if dst not in seen:
                        seen.add(dst)
                        nxt.append(dst)
                if allow_virtual:
                    for t_idx in typeinfo_refs.get(rva, ()):
                        if t_idx in game_type_methods:
                            ref_types.add(t_idx)
            if allow_virtual:
                for t_idx in sorted(ref_types - processed_types):
                    processed_types.add(t_idx)
                    cand = set()
                    for mi in vtables.get(t_idx, ()):
                        mrva = insp.method_rvas.get(mi, 0) & ~1
                        if mrva:
                            cand.add(mrva)
                    for m in game_type_methods.get(t_idx, ()):
                        if m["name"] in (".ctor", ".cctor") and m["rva"]:
                            cand.add(m["rva"])
                    for rva in sorted(cand):
                        if rva not in seen:
                            seen.add(rva)
                            nxt.append(rva)
            frontier = nxt
        return seen

    reach_direct = bfs(roots_direct, allow_virtual=False)
    reach_virtual = bfs(roots_direct, allow_virtual=True)
    reach_named = bfs(roots_direct | name_dispatch, allow_virtual=True)

    def tag(m):
        if not m["rva"]:
            return "none"
        if m["rva"] in reach_direct:
            return "direct"
        if m["rva"] in reach_virtual:
            return "virtual"
        if m["rva"] in reach_named:
            return "by_name"
        return "none"

    return tag, roots_direct, reach_direct, reach_named


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    insp = Il2CppInspector(need_all_rvas=True)
    print("[1/6] metadata + binary body classification ...")
    methods, start_arr, sizes, code_end = build_binary_tables(insp)

    print("[2/6] code reference scan (BL/B/fnptr/MethodRef/TypeInfo/literals) ...")
    call_edges, typeinfo_refs, name_literals = scan_code_references(
        insp, methods, start_arr, sizes, code_end)

    print("[3/6] vtables + scene/prefab usage ...")
    vtables = parse_vtables(insp)
    used_classes, event_names, anim_names = scan_scene_usage()

    print("[4/6] exported C# source classification ...")
    src_bodies = scan_sources()

    print("[5/6] reachability ...")
    tag, roots, _reach_d, _reach_v = compute_reachability(
        insp, methods, call_edges, typeinfo_refs, name_literals,
        vtables, used_classes, event_names, anim_names)

    print("[6/6] writing outputs ...")
    game = [m for m in methods if m["image"] in GAME_IMAGES]
    used_simple = set(used_classes)

    records = []
    for m in sorted(game, key=lambda x: (x["type"], x["name"], x["token"])):
        simple_type = m["type"].split(".")[-1]
        if m["name"] in (".ctor", ".cctor"):
            src_key = (simple_type, m["name"])
        else:
            src_key = (simple_type, m["name"].split(".")[-1])
        kinds = sorted(set(src_bodies.get(src_key, [])))
        src = kinds[0] if len(kinds) == 1 else ("mixed" if kinds else None)
        records.append({
            "type": m["type"],
            "method": m["name"],
            "token": f"0x{m['token']:08X}",
            "rva": f"0x{m['rva']:08X}",
            "size": m["size"],
            "params": m["params"],
            "bin": m["bin"],
            "src": src,
            "reach": tag(m),
            "scene_used": simple_type in used_simple,
        })

    bin_hist = Counter(m["bin"] for m in game)
    src_hist = Counter(r["src"] for r in records)
    reach_hist = Counter(r["reach"] for r in records)
    image_hist = {}
    for m in methods:
        h = image_hist.setdefault(m["image"], Counter())
        h[m["bin"]] += 1

    STUB_SRC = {"empty", "ret_false", "ret_true", "ret_null", "ret_default", "ret_zero"}
    lost = [
        r for r in records
        if r["src"] in STUB_SRC and r["bin"] == "substantive" and r["reach"] != "none"
    ]
    rank = {"direct": 3, "virtual": 2, "by_name": 1}
    lost.sort(key=lambda r: (-rank[r["reach"]], not r["scene_used"], -r["size"],
                             r["type"], r["method"]))

    verified_noop = sum(
        1 for r in records
        if r["src"] in STUB_SRC and r["bin"] in ("empty", "tiny")
        or (r["src"] == "ret_false" and r["bin"] == "ret_const_0")
        or (r["src"] == "ret_true" and r["bin"] == "ret_const_1")
        or (r["src"] in ("ret_null", "ret_zero") and r["bin"] == "ret_const_0")
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "apk": "original/apk/com.rexetstudio.blockstrike_6.5.1_2492.apk",
        "binary": "lib/armeabi-v7a/libil2cpp.so",
        "metadata_version": "24.2",
        "total_methods_all_images": len(methods),
        "game_assembly_methods": len(game),
        "scene_used_classes": len(used_classes),
        "unityevent_method_names": len(event_names),
        "animationevent_method_names": len(anim_names),
        "call_graph_edges": sum(len(v) for v in call_edges.values()),
        "reachability_roots": len(roots),
        "binary_body_histogram": dict(sorted(bin_hist.items())),
        "source_body_histogram": {str(k): v for k, v in sorted(src_hist.items(), key=lambda kv: str(kv[0]))},
        "reachability_histogram": dict(sorted(reach_hist.items())),
        "verified_noop_stubs": verified_noop,
        "lost_implementations_reachable": len(lost),
        "per_image_binary_histogram": {
            k: dict(sorted(v.items())) for k, v in sorted(image_hist.items())
        },
    }
    (OUT_DIR / "inventory.json").write_text(
        json.dumps({"summary": summary, "methods": records},
                   ensure_ascii=False, indent=None, separators=(",", ":"))
        + "\n", encoding="utf-8")
    (OUT_DIR / "priorities.json").write_text(
        json.dumps({"summary": {
            "description": "Reachable methods whose exported C# body is a stub "
                           "but whose ARMv7 body in libil2cpp.so is substantive "
                           "(lost implementations), ranked by reachability tier, "
                           "scene usage and binary size.",
            "count": len(lost),
        }, "methods": lost}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    write_report(summary, lost)
    print(f"[OK] {len(records)} game-assembly methods inventoried; "
          f"{len(lost)} reachable lost implementations ranked; "
          f"{verified_noop} stubs verified as no-ops in the binary.")


def write_report(summary, lost) -> None:
    md = []
    md.append("# IL2CPP method/body inventory (Block Strike 6.5.1, build 2492)\n")
    md.append("Generated deterministically by `python3 tools/build_method_inventory.py` from")
    md.append("`lib/armeabi-v7a/libil2cpp.so` + `global-metadata.dat` of the ground-truth APK")
    md.append("and the exported C# sources in `client/Assets`. Outputs:")
    md.append("`tools/method-inventory/inventory.json` (full per-method inventory) and")
    md.append("`tools/method-inventory/priorities.json` (ranked lost-implementation worklist).\n")
    md.append("## Summary\n")
    md.append(f"- Methods in all 61 images: **{summary['total_methods_all_images']}**")
    md.append(f"- Methods in `Assembly-CSharp` + `Assembly-CSharp-firstpass`: **{summary['game_assembly_methods']}**")
    md.append(f"- Scene/prefab-referenced script classes: **{summary['scene_used_classes']}**")
    md.append(f"- Static call-graph edges decoded from ARMv7 code: **{summary['call_graph_edges']}**")
    md.append(f"- Reachability roots (engine/NGUI/Photon messages, UnityEvent `m_MethodName`, AnimationEvent `functionName`, serialized ctors): **{summary['reachability_roots']}**")
    md.append(f"- Exported stubs verified as genuine no-ops in the binary: **{summary['verified_noop_stubs']}**")
    md.append(f"- **Reachable lost implementations (stub in C#, substantive in binary): {summary['lost_implementations_reachable']}**\n")
    md.append("## Binary body classification (game assemblies)\n")
    md.append("| kind | count |\n| --- | --- |")
    for k, v in summary["binary_body_histogram"].items():
        md.append(f"| `{k}` | {v} |")
    md.append("\n## Exported C# body classification (game assemblies)\n")
    md.append("| kind | count |\n| --- | --- |")
    for k, v in summary["source_body_histogram"].items():
        md.append(f"| `{k}` | {v} |")
    md.append("\n## Reachability (from APK-confirmed entry points)\n")
    md.append("| tier | count |\n| --- | --- |")
    tier_desc = {
        "direct": "BL/B/function-pointer/MethodRef chain from scene roots",
        "virtual": "adds RTA-style vtable closure over TypeInfo-referenced game types",
        "by_name": "exact string-literal name dispatch (SendMessage/Invoke style)",
        "none": "not reachable through any decoded edge (includes dead code)",
    }
    for k, v in summary["reachability_histogram"].items():
        md.append(f"| `{k}` ({tier_desc.get(k, '')}) | {v} |")
    md.append("\n## Top 100 ranked lost implementations\n")
    md.append("Full list: `tools/method-inventory/priorities.json`.\n")
    md.append("| # | type | method | reach | scene | size | RVA |")
    md.append("| --- | --- | --- | --- | --- | --- | --- |")
    for i, r in enumerate(lost[:100], 1):
        t = r["type"] if len(r["type"]) <= 40 else r["type"][:37] + "..."
        m = r["method"] if len(r["method"]) <= 40 else r["method"][:37] + "..."
        md.append(f"| {i} | `{t}` | `{m}` | {r['reach']} | {'x' if r['scene_used'] else ''} | {r['size']} | `{r['rva']}` |")
    md.append("\n## Methodology and limitations\n")
    md.append("- **Binary classification** decodes the actual ARMv7 words: `bx lr` = `empty`,")
    md.append("  `mov r0, #imm; bx lr` = `ret_const_imm`, ≤16 bytes = `tiny`, otherwise `substantive`.")
    md.append("  Method sizes are estimated as the distance to the next method start inside the")
    md.append("  executable `PT_LOAD` segment, so trailing literal pools are included in `size`.")
    md.append("- **Call edges** cover BL/conditional-BL, cross-method unconditional B (tail calls),")
    md.append("  raw function-pointer literal words, and `Il2CppMetadataUsage` MethodRef slots.")
    md.append("  Virtual/interface dispatch is over-approximated per RTA: when reachable game code")
    md.append("  references a game type's TypeInfo, that type's metadata vtable slots and")
    md.append("  `.ctor`/`.cctor` become reachable. Generic-method vtable entries (kind 6) and")
    md.append("  reflection beyond exact-name string literals are not modeled; `none` therefore")
    md.append("  means *no decoded evidence of reachability*, not proven-dead.")
    md.append("- **Source classification** parses the exported client sources; only literal")
    md.append("  `{ }`, `return false/true/null/0/default` bodies count as stubs. A stub whose")
    md.append("  binary body is also trivial is counted as a verified no-op, not a loss.")
    md.append("- Everything is recomputed from the APK on each run; no cached or invented data.")
    (ROOT / "docs" / "method-inventory.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
