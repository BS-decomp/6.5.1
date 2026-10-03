#!/usr/bin/env python3
"""
Fast ARMv7 IL2CPP Disassembler & Metadata Resolver for Block Strike 6.5.1 (Unity 2019.2.3f1, v24.2).
Directly inspects lib/armeabi-v7a/libil2cpp.so and global-metadata.dat from the 6.5.1 APK in <0.3s.
"""

import argparse
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_META = Path("/tmp/apk_extract/assets/bin/Data/Managed/Metadata/global-metadata.dat")
DEFAULT_SO = Path("/tmp/apk_extract/lib/armeabi-v7a/libil2cpp.so")


def ensure_extracted() -> tuple[Path, Path]:
    if DEFAULT_META.exists() and DEFAULT_SO.exists():
        return DEFAULT_META, DEFAULT_SO
    apk_candidates = [
        ROOT / "original/apk/com.rexetstudio.blockstrike_6.5.1_2492.apk",
        Path("/tmp/bs651.apk"),
    ]
    for apk in apk_candidates:
        if apk.exists():
            DEFAULT_META.parent.mkdir(parents=True, exist_ok=True)
            DEFAULT_SO.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(apk, "r") as zf:
                DEFAULT_META.write_bytes(zf.read("assets/bin/Data/Managed/Metadata/global-metadata.dat"))
                DEFAULT_SO.write_bytes(zf.read("lib/armeabi-v7a/libil2cpp.so"))
            return DEFAULT_META, DEFAULT_SO
    raise FileNotFoundError("Could not find extracted global-metadata.dat / libil2cpp.so or 6.5.1 APK")


class Il2CppInspector:
    def __init__(self, need_all_rvas: bool = False) -> None:
        meta_path, so_path = ensure_extracted()
        self.meta = meta_path.read_bytes()
        self.so = so_path.read_bytes()
        self._parse_metadata(need_all_rvas=need_all_rvas)

    @staticmethod
    def v2o(v: int) -> int:
        return v - 0x1000 if v >= 0x022723F0 else v

    def get_str(self, idx: int) -> str:
        off = self.stringOffset + idx
        end = self.meta.find(b"\x00", off)
        return self.meta[off:end].decode("utf-8", errors="replace")

    def get_lit(self, idx: int) -> str:
        length, data_idx = struct.unpack_from("<II", self.meta, self.stringLiteralOffset + idx * 8)
        off = self.stringLiteralDataOffset + data_idx
        return self.meta[off : off + length].decode("utf-8", errors="replace")

    def get_method_full_name(self, mi: int) -> str:
        mf = struct.unpack_from("<6i4H", self.meta, self.methodsOffset + mi * 32)
        m_name = self.get_str(mf[0])
        t_idx = mf[1]  # Il2CppMethodDefinition.declaringType (metadata v24.2)
        t_name = self.type_names[t_idx] if 0 <= t_idx < len(self.type_names) else f"Type{t_idx}"
        return f"{t_name}::{m_name}"

    def _parse_metadata(self, need_all_rvas: bool = False) -> None:
        hdr = struct.unpack_from("<2I62i", self.meta, 0)
        self.stringLiteralOffset = hdr[2]
        self.stringLiteralDataOffset = hdr[4]
        self.stringOffset = hdr[6]
        self.methodsOffset = hdr[12]
        self.methodsSize = hdr[13]
        self.fieldsOffset = hdr[24]
        self.typeDefinitionsOffset = hdr[40]
        self.typeDefinitionsSize = hdr[41]
        self.imagesOffset = hdr[42]
        self.imagesSize = hdr[43]
        self.metadataUsageListsOffset = hdr[46]
        self.metadataUsagePairsOffset = hdr[48]
        self.metadataUsagePairsSize = hdr[49]

        self.num_types = self.typeDefinitionsSize // 92
        self.type_names: list[str] = []
        self.type_fields: list[tuple[int, int]] = []
        self.type_methods: list[tuple[int, int]] = []
        for i in range(self.num_types):
            tf = struct.unpack_from("<23i", self.meta, self.typeDefinitionsOffset + i * 92)
            ns = self.get_str(tf[1])
            nm = self.get_str(tf[0])
            self.type_names.append(f"{ns}.{nm}" if ns else nm)
            self.type_fields.append((tf[9], tf[18] & 0xFFFF))
            self.type_methods.append((tf[10], tf[17] & 0xFFFF))

        self.field_Offsets_off = self.v2o(0x023A613C)
        self.field_offset_ptrs = struct.unpack_from(
            f"<{self.num_types}I", self.so, self.field_Offsets_off
        )

        # Map image method pointers
        num_images = self.imagesSize // 40
        self.method_rvas: dict[int, int] = {}
        self.rva_to_mi: dict[int, int] = {}

        cgm_table_va = 0x023C50A8
        num_modules = 61
        cgm_ptrs = struct.unpack_from(f"<{num_modules}I", self.so, self.v2o(cgm_table_va))
        self.module_by_name: dict[str, tuple[int, int]] = {}
        for ptr in cgm_ptrs:
            name_ptr, m_count, m_ptrs = struct.unpack_from("<III", self.so, self.v2o(ptr))
            end = self.so.find(b"\x00", self.v2o(name_ptr))
            m_name = self.so[self.v2o(name_ptr) : end].decode("utf-8", errors="replace")
            self.module_by_name[m_name] = (m_count, m_ptrs)

        for img_idx in range(num_images):
            im = struct.unpack_from("<10i", self.meta, self.imagesOffset + img_idx * 40)
            img_name = self.get_str(im[0])
            if not need_all_rvas and img_name not in ("Assembly-CSharp.dll", "Assembly-CSharp-firstpass.dll"):
                continue
            if img_name not in self.module_by_name:
                continue
            t_start, t_count = im[2], im[3]
            m_count, m_ptrs_va = self.module_by_name[img_name]
            if not m_count or not m_ptrs_va:
                continue
            ptrs = struct.unpack_from(f"<{m_count}I", self.so, self.v2o(m_ptrs_va))
            for t_idx in range(t_start, t_start + t_count):
                m_start, mc = self.type_methods[t_idx]
                for mi in range(m_start, m_start + mc):
                    token = struct.unpack_from("<I", self.meta, self.methodsOffset + mi * 32 + 20)[0]
                    rid = (token & 0xFFFFFF) - 1
                    rva = ptrs[rid] if 0 <= rid < len(ptrs) else 0
                    self.method_rvas[mi] = rva
                    if rva:
                        self.rva_to_mi[rva & ~1] = mi

        self.bss_usage: dict[int, tuple[int, int]] = {}
        if need_all_rvas:
            num_pairs = self.metadataUsagePairsSize // 8
            u_base = self.v2o(0x02272F10)
            for i in range(num_pairs):
                dest, enc = struct.unpack_from("<II", self.meta, self.metadataUsagePairsOffset + i * 8)
                slot_va = struct.unpack_from("<I", self.so, u_base + dest * 4)[0]
                self.bss_usage[slot_va] = ((enc >> 29) & 7, enc & 0x1FFFFFFF)
            self._parse_types_table()

    def _parse_types_table(self) -> None:
        """Resolve Il2CppMetadataRegistration.types so that TypeInfo/Il2CppType
        metadata-usage indices can be mapped back to typedef indices.
        The registration struct is located by its known fieldOffsets (0x023A613C)
        and metadataUsages (0x02272F10) member values."""
        self.type_ref_typedef: list[int] = []
        needle = struct.pack("<I", 0x023A613C)
        pos = -1
        while True:
            pos = self.so.find(needle, pos + 1)
            if pos < 0:
                return
            base = pos - 44  # fieldOffsets is member 11 of Il2CppMetadataRegistration
            if base < 0:
                continue
            if struct.unpack_from("<I", self.so, base + 60)[0] != 0x02272F10:
                continue
            types_count, types_ptr = struct.unpack_from("<II", self.so, base + 24)
            ptrs = struct.unpack_from(f"<{types_count}I", self.so, self.v2o(types_ptr))
            out = []
            for p in ptrs:
                data, bits = struct.unpack_from("<II", self.so, self.v2o(p))
                ty = (bits >> 16) & 0xFF
                if ty in (0x11, 0x12):  # VALUETYPE / CLASS -> typedef index
                    out.append(data)
                elif ty == 0x15:  # GENERICINST -> Il2CppGenericClass.typeDefinitionIndex
                    out.append(struct.unpack_from("<i", self.so, self.v2o(data))[0])
                else:
                    out.append(-1)
            self.type_ref_typedef = out
            return

    def type_ref_to_typedef(self, type_ref_idx: int) -> int:
        """Map a metadata-usage TypeInfo/Il2CppType index to a typedef index (-1 if N/A)."""
        if 0 <= type_ref_idx < len(self.type_ref_typedef):
            return self.type_ref_typedef[type_ref_idx]
        return -1

    def format_usage(self, va: int) -> str:
        if va not in self.bss_usage:
            return ""
        kind, idx = self.bss_usage[va]
        if kind == 5:
            return f'StringLiteral("{self.get_lit(idx)}")'
        if kind in (1, 2):
            td = self.type_ref_to_typedef(idx)
            if 0 <= td < len(self.type_names):
                return f"TypeInfo({self.type_names[td]})"
            return f"TypeInfo(typeRef {idx})"
        if kind == 3:
            return f"MethodRef({self.get_method_full_name(idx) if idx < (self.methodsSize // 32) else idx})"
        if kind == 4:
            return f"FieldInfo({idx})"
        return f"Usage({kind},{idx})"

    def inspect_type(self, query: str) -> None:
        for t_idx, name in enumerate(self.type_names):
            if query == name or name.endswith("." + query):
                print(f"=== Type[{t_idx}] {name} ===")
                f_start, f_count = self.type_fields[t_idx]
                f_table_va = self.field_offset_ptrs[t_idx]
                f_offs = (
                    struct.unpack_from(f"<{f_count}i", self.so, self.v2o(f_table_va))
                    if (f_table_va and f_count)
                    else ()
                )
                for fi in range(f_count):
                    ff = struct.unpack_from("<3i", self.meta, self.fieldsOffset + (f_start + fi) * 12)
                    f_name = self.get_str(ff[0])
                    off = f_offs[fi] if fi < len(f_offs) else -1
                    print(f"  field[{fi:2d}] +0x{off:02x}: {f_name}")
                m_start, m_count = self.type_methods[t_idx]
                for mi in range(m_start, m_start + m_count):
                    mf = struct.unpack_from("<6i4H", self.meta, self.methodsOffset + mi * 32)
                    m_name = self.get_str(mf[0])
                    p_count = mf[9]
                    rva = self.method_rvas.get(mi, 0)
                    print(f"  method[{mi}] RVA=0x{rva:08x} params={p_count} {m_name}")

    def disasm(self, rva: int, max_insns: int = 200) -> None:
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM

        md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        code = self.so[rva : rva + max_insns * 4]
        reg_vals: dict[str, int] = {}
        for insn in md.disasm(code, rva):
            note = ""
            op = insn.op_str
            if insn.mnemonic == "ldr" and "[pc" in op:
                parts = op.split(",")
                dst_reg = parts[0].strip()
                imm = 0
                if "#" in op:
                    imm_s = op.split("#")[1].rstrip("]! ")
                    imm = int(imm_s, 0)
                pool_addr = ((insn.address + 8) & ~3) + imm
                if 0 <= pool_addr <= len(self.so) - 4:
                    val = struct.unpack_from("<I", self.so, pool_addr)[0]
                    reg_vals[dst_reg] = val
                    note = f" ; [0x{pool_addr:x}] = 0x{val:x}"
            elif insn.mnemonic == "add" and "pc" in op:
                parts = [p.strip() for p in op.split(",")]
                if len(parts) >= 3 and parts[1] == "pc" and parts[2] in reg_vals:
                    va = (insn.address + 8 + reg_vals[parts[2]]) & 0xFFFFFFFF
                    reg_vals[parts[0]] = va
                    u_str = self.format_usage(va)
                    note = f" ; VA=0x{va:x}" + (f" -> {u_str}" if u_str else "")
            elif insn.mnemonic == "ldr" and "[" in op and "pc" not in op:
                parts = [p.strip() for p in op.split(",")]
                if len(parts) == 2 and parts[1].startswith("[") and parts[1].endswith("]"):
                    base_reg = parts[1][1:-1].strip()
                    if base_reg in reg_vals:
                        u_str = self.format_usage(reg_vals[base_reg])
                        if u_str:
                            note = f" ; {u_str}"
            elif insn.mnemonic in ("bl", "b"):
                try:
                    target = int(op.lstrip("#"), 0)
                    if target in self.rva_to_mi:
                        note = f" ; {self.get_method_full_name(self.rva_to_mi[target])}"
                except ValueError:
                    pass
            print(f"  0x{insn.address:08x}: {insn.mnemonic:8s} {insn.op_str:28s}{note}")
            if insn.mnemonic == "pop" and "pc" in insn.op_str:
                break
            if insn.mnemonic == "bx" and insn.op_str.strip() == "lr":
                break


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", action="append", help="Inspect type fields and methods")
    ap.add_argument("--rva", action="append", help="Disassemble method at hex RVA (e.g. 0x00773560)")
    ap.add_argument("--max-insns", type=int, default=200)
    args = ap.parse_args()

    insp = Il2CppInspector(need_all_rvas=bool(args.rva))
    for t in args.type or []:
        insp.inspect_type(t)
    for r in args.rva or []:
        print(f"=== Disasm {r} ===")
        insp.disasm(int(r, 0), args.max_insns)


if __name__ == "__main__":
    main()
