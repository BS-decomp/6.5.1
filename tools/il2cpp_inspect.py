#!/usr/bin/env python3
"""
ARMv7 IL2CPP Disassembler & Metadata Resolver for Block Strike 6.5.1 (Unity 2019.2.3f1, v24.2).
Directly inspects lib/armeabi-v7a/libil2cpp.so and global-metadata.dat from the 6.5.1 APK.
"""

import argparse
import os
import struct
import zipfile
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM

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
    def __init__(self) -> None:
        meta_path, so_path = ensure_extracted()
        self.meta = meta_path.read_bytes()
        self.so = so_path.read_bytes()
        self._parse_metadata()

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

    def _parse_metadata(self) -> None:
        hdr = struct.unpack_from("<2I62i", self.meta, 0)
        self.stringLiteralOffset = hdr[2]
        self.stringLiteralDataOffset = hdr[4]
        self.stringOffset = hdr[6]
        self.methodsOffset = hdr[14]
        self.methodsSize = hdr[15]
        self.fieldsOffset = hdr[22]
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
            self.type_fields.append((tf[8], (tf[17] >> 16) & 0xFFFF))
            self.type_methods.append((tf[9], tf[16] & 0xFFFF))

        self.field_Offsets_off = self.v2o(0x023A613C)
        self.field_offset_ptrs = struct.unpack_from(
            f"<{self.num_types}I", self.so, self.field_Offsets_off
        )

        # Map all image method pointers
        num_images = self.imagesSize // 40
        self.method_rvas: dict[int, int] = {}
        self.rva_to_method: dict[int, str] = {}
        self.method_names: dict[int, str] = {}

        # Scan g_CodeRegistration.codeGenModules at 0x02460b78
        cgm_table_va = 0x02460B78
        num_modules = 62
        cgm_ptrs = struct.unpack_from(f"<{num_modules}I", self.so, self.v2o(cgm_table_va))
        module_by_name: dict[str, tuple[int, int]] = {}
        for ptr in cgm_ptrs:
            name_ptr, m_count, m_ptrs = struct.unpack_from("<III", self.so, self.v2o(ptr))
            end = self.so.find(b"\x00", self.v2o(name_ptr))
            m_name = self.so[self.v2o(name_ptr) : end].decode("utf-8", errors="replace")
            module_by_name[m_name] = (m_count, m_ptrs)

        for img_idx in range(num_images):
            im = struct.unpack_from("<10i", self.meta, self.imagesOffset + img_idx * 40)
            img_name = self.get_str(im[0])
            t_start, t_count = im[2], im[3]
            if img_name not in module_by_name:
                continue
            m_count, m_ptrs_va = module_by_name[img_name]
            ptrs = struct.unpack_from(f"<{m_count}I", self.so, self.v2o(m_ptrs_va))
            for t_idx in range(t_start, t_start + t_count):
                t_name = self.type_names[t_idx]
                m_start, mc = self.type_methods[t_idx]
                for mi in range(m_start, m_start + mc):
                    mf = struct.unpack_from("<6i4H", self.meta, self.methodsOffset + mi * 32)
                    m_name = self.get_str(mf[0])
                    token = mf[5]
                    rid = (token & 0xFFFFFF) - 1
                    rva = ptrs[rid] if 0 <= rid < len(ptrs) else 0
                    full_name = f"{t_name}::{m_name}"
                    self.method_names[mi] = full_name
                    self.method_rvas[mi] = rva
                    if rva:
                        self.rva_to_method[rva & ~1] = full_name

        # Map metadata usage slots (.bss 0x0247fc54..0x02499800)
        self.bss_usage: dict[int, str] = {}
        num_pairs = self.metadataUsagePairsSize // 8
        for i in range(num_pairs):
            dest, enc = struct.unpack_from("<II", self.meta, self.metadataUsagePairsOffset + i * 8)
            kind = (enc >> 29) & 7
            idx = enc & 0x1FFFFFFF
            slot_va = struct.unpack_from("<I", self.so, self.v2o(0x02272F10 + dest * 4))[0]
            if kind == 5:
                self.bss_usage[slot_va] = f'StringLiteral("{self.get_lit(idx)}")'
            elif kind == 1 or kind == 2:
                t_idx = idx & 0xFFFF
                self.bss_usage[slot_va] = f"TypeInfo({self.type_names[t_idx] if t_idx < len(self.type_names) else idx})"
            elif kind == 3:
                self.bss_usage[slot_va] = f"MethodRef({self.method_names.get(idx, str(idx))})"
            elif kind == 4:
                self.bss_usage[slot_va] = f"FieldInfo({idx})"

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
        md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        code = self.so[rva : rva + max_insns * 4]
        reg_vals: dict[str, int] = {}
        for insn in md.disasm(code, rva):
            note = ""
            op = insn.op_str
            # Track PC-relative literal pool loads: ldr rX, [pc, #imm]
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
                    note = f" ; VA=0x{va:x}"
                    if va in self.bss_usage:
                        note += f" -> {self.bss_usage[va]}"
            elif insn.mnemonic == "ldr" and "[" in op and "pc" not in op:
                parts = [p.strip() for p in op.split(",")]
                if len(parts) == 2 and parts[1].startswith("[") and parts[1].endswith("]"):
                    base_reg = parts[1][1:-1].strip()
                    if base_reg in reg_vals:
                        va = reg_vals[base_reg]
                        if va in self.bss_usage:
                            note = f" ; {self.bss_usage[va]}"
            elif insn.mnemonic in ("bl", "b"):
                try:
                    target = int(op.lstrip("#"), 0)
                    if target in self.rva_to_method:
                        note = f" ; {self.rva_to_method[target]}"
                except ValueError:
                    pass
            print(f"  0x{insn.address:08x}: {insn.mnemonic:8s} {insn.op_str:28s}{note}")
            if insn.mnemonic == "pop" and "pc" in insn.op_str:
                break
            if insn.mnemonic == "bx" and insn.op_str.strip() == "lr":
                break


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", help="Inspect type fields and methods")
    ap.add_argument("--rva", help="Disassemble method at hex RVA (e.g. 0x00773560)")
    ap.add_argument("--max-insns", type=int, default=200)
    args = ap.parse_args()

    insp = Il2CppInspector()
    if args.type:
        insp.inspect_type(args.type)
    if args.rva:
        insp.disasm(int(args.rva, 0), args.max_insns)


if __name__ == "__main__":
    main()
