#!/usr/bin/env python3
"""Offline deterministic static-batch geometry separator for Block Strike 6.5.1.

Reads `tools/geometry-recovery/manifest.json` + per-scene manifests, extracts
all 4,846 static-batched MeshRenderers from the 70 `Combined Mesh (root_ scene)*.asset`
files into local-space `Mesh` assets under `Assets/RecoveredGeometry/<SceneName>/`,
updates the 70 `.unity` scene files and `LightingData*.asset` files, and
sanitizes uninitialized `NaN` spherical harmonics probes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DOC_HEADER_RE = re.compile(r"^--- !u!(\d+) &(-?\d+)\s*$", re.M)


def trs_matrix(
    pos: List[float], rot: List[float], scale: List[float]
) -> Tuple[Tuple[float, ...], ...]:
    x, y, z, w = rot
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    return (
        (
            (1.0 - 2.0 * (yy + zz)) * scale[0],
            (2.0 * (xy - wz)) * scale[1],
            (2.0 * (xz + wy)) * scale[2],
            pos[0],
        ),
        (
            (2.0 * (xy + wz)) * scale[0],
            (1.0 - 2.0 * (xx + zz)) * scale[1],
            (2.0 * (yz - wx)) * scale[2],
            pos[1],
        ),
        (
            (2.0 * (xz - wy)) * scale[0],
            (2.0 * (yz + wx)) * scale[1],
            (1.0 - 2.0 * (xx + yy)) * scale[2],
            pos[2],
        ),
        (0.0, 0.0, 0.0, 1.0),
    )


def mat4_mul(
    a: Tuple[Tuple[float, ...], ...], b: Tuple[Tuple[float, ...], ...]
) -> Tuple[Tuple[float, ...], ...]:
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4))
        for i in range(4)
    )


def mat3_det(m: Tuple[Tuple[float, ...], ...]) -> float:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def mat4_affine_inverse(
    m: Tuple[Tuple[float, ...], ...]
) -> Tuple[Tuple[float, ...], ...]:
    det = mat3_det(m)
    if abs(det) < 1e-12:
        return (
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        )
    inv_det = 1.0 / det
    r00 = (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv_det
    r01 = (m[0][2] * m[2][1] - m[0][1] * m[2][2]) * inv_det
    r02 = (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv_det
    r10 = (m[1][2] * m[2][0] - m[1][0] * m[2][2]) * inv_det
    r11 = (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv_det
    r12 = (m[0][2] * m[1][0] - m[0][0] * m[1][2]) * inv_det
    r20 = (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv_det
    r21 = (m[0][1] * m[2][0] - m[0][0] * m[2][1]) * inv_det
    r22 = (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv_det
    tx, ty, tz = m[0][3], m[1][3], m[2][3]
    itx = -(r00 * tx + r01 * ty + r02 * tz)
    ity = -(r10 * tx + r11 * ty + r12 * tz)
    itz = -(r20 * tx + r21 * ty + r22 * tz)
    return (
        (r00, r01, r02, itx),
        (r10, r11, r12, ity),
        (r20, r21, r22, itz),
        (0.0, 0.0, 0.0, 1.0),
    )


def compute_local_to_world(chain: List[dict]) -> Tuple[Tuple[float, ...], ...]:
    m = (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
    for node in chain:
        m = mat4_mul(
            m,
            trs_matrix(
                node["localPosition"], node["localRotation"], node["localScale"]
            ),
        )
    return m


def fmt_float(v: float) -> str:
    if abs(v) < 1e-7:
        v = 0.0
    s = f"{v:.7g}"
    return "0" if s in ("-0", "-0.0", "0.0") else s


def write_folder_meta(folder_path: Path, seed: str) -> None:
    meta_path = folder_path.with_name(folder_path.name + ".meta")
    if meta_path.exists():
        return
    guid = hashlib.md5(seed.encode("utf-8")).hexdigest()
    meta_path.write_text(
        f"fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        f"folderAsset: yes\n"
        f"DefaultImporter:\n"
        f"  externalObjects: {{}}\n"
        f"  userData: \n"
        f"  assetBundleName: \n"
        f"  assetBundleVariant: \n",
        encoding="utf-8",
    )


def write_mesh_meta(asset_path: Path, guid: str) -> None:
    meta_path = asset_path.with_name(asset_path.name + ".meta")
    meta_path.write_text(
        f"fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        f"timeCreated: 1790907799\n"
        f"licenseType: Free\n"
        f"NativeFormatImporter:\n"
        f"  externalObjects: {{}}\n"
        f"  mainObjectFileID: 4300000\n"
        f"  userData:\n"
        f"  assetBundleName:\n"
        f"  assetBundleVariant:\n",
        encoding="utf-8",
    )


class CombinedMeshData:
    def __init__(self, asset_path: Path) -> None:
        txt = asset_path.read_text(encoding="utf-8", errors="ignore")
        self.vertex_count = int(re.search(r"m_VertexCount:\s*(\d+)", txt).group(1))
        self.data_size = int(re.search(r"m_DataSize:\s*(\d+)", txt).group(1))
        self.stride = self.data_size // self.vertex_count
        self.index_bytes = bytes.fromhex(
            re.search(r"m_IndexBuffer:\s*([0-9a-fA-F]*)", txt).group(1)
        )
        self.vertex_bytes = bytes.fromhex(
            re.search(r"_typelessdata:\s*([0-9a-fA-F]*)", txt).group(1)
        )
        ch_sec = txt.split("    m_Channels:\n", 1)[1].split("    m_DataSize:", 1)[0]
        self.channels_yaml = "    m_Channels:\n" + ch_sec
        self.channels = [
            tuple(map(int, m.groups()))
            for m in re.finditer(
                r"stream:\s*(\d+)\s+offset:\s*(\d+)\s+format:\s*(\d+)\s+dimension:\s*(\d+)",
                ch_sec,
            )
        ]
        sub_sec = txt.split("  m_SubMeshes:\n", 1)[1].split("  m_Shapes:", 1)[0]
        self.submeshes = []
        for s in re.split(r"  - serializedVersion: 2\n", sub_sec)[1:]:
            self.submeshes.append(
                {
                    "firstByte": int(re.search(r"firstByte:\s*(\d+)", s).group(1)),
                    "indexCount": int(re.search(r"indexCount:\s*(\d+)", s).group(1)),
                    "topology": int(re.search(r"topology:\s*(\d+)", s).group(1)),
                    "baseVertex": int(re.search(r"baseVertex:\s*(\d+)", s).group(1)),
                    "firstVertex": int(re.search(r"firstVertex:\s*(\d+)", s).group(1)),
                    "vertexCount": int(re.search(r"vertexCount:\s*(\d+)", s).group(1)),
                }
            )


def compute_aabb(
    pts: List[Tuple[float, float, float]]
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    if not pts:
        return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)
    cx = 0.5 * (min_x + max_x)
    cy = 0.5 * (min_y + max_y)
    cz = 0.5 * (min_z + max_z)
    ex = 0.5 * (max_x - min_x)
    ey = 0.5 * (max_y - min_y)
    ez = 0.5 * (max_z - min_z)
    return (cx, cy, cz), (ex, ey, ez)


def extract_renderer_mesh_yaml(
    cm: CombinedMeshData,
    renderer: dict,
) -> str:
    local_to_world = compute_local_to_world(renderer["transformChain"])
    world_to_local = mat4_affine_inverse(local_to_world)
    invert_winding = mat3_det(local_to_world) < 0.0

    norm_ch = cm.channels[1]
    has_normals = (norm_ch[3] & 0xF) > 0
    norm_offset = norm_ch[1]
    norm_format = norm_ch[2]

    uv1_ch = cm.channels[5]
    has_uv1 = (uv1_ch[3] & 0xF) > 0
    uv1_offset = uv1_ch[1]

    lm_info = renderer.get("lightmapInfo")
    lm_st: Optional[List[float]] = None
    if lm_info and has_uv1:
        st = lm_info.get("lightmapST", [1.0, 1.0, 0.0, 0.0])
        if len(st) == 4 and abs(st[0]) > 1e-7 and abs(st[1]) > 1e-7:
            lm_st = st

    stride = cm.stride
    out_indices: List[int] = []
    out_vertex_chunks: List[bytes] = []
    all_local_pts: List[Tuple[float, float, float]] = []
    submesh_blocks: List[str] = []

    current_first_vertex = 0
    current_first_byte = 0

    for sub_idx in renderer["subMeshIndices"]:
        sub = cm.submeshes[sub_idx]
        ic = sub["indexCount"]
        fb = sub["firstByte"]
        if ic == 0:
            submesh_blocks.append(
                f"  - serializedVersion: 2\n"
                f"    firstByte: {current_first_byte}\n"
                f"    indexCount: 0\n"
                f"    topology: {sub['topology']}\n"
                f"    baseVertex: 0\n"
                f"    firstVertex: 0\n"
                f"    vertexCount: 0\n"
                f"    localAABB:\n"
                f"      m_Center: {{x: 0, y: 0, z: 0}}\n"
                f"      m_Extent: {{x: 0, y: 0, z: 0}}"
            )
            continue

        raw_idxs = list(
            struct.unpack(f"<{ic}H", cm.index_bytes[fb : fb + ic * 2])
        )
        base_v = sub["baseVertex"]
        if base_v:
            raw_idxs = [i + base_v for i in raw_idxs]

        used_verts = sorted(set(raw_idxs))
        remap = {old_v: current_first_vertex + idx for idx, old_v in enumerate(used_verts)}
        local_sub_idxs = [remap[old_v] for old_v in raw_idxs]

        if invert_winding:
            for t in range(0, len(local_sub_idxs) - 2, 3):
                local_sub_idxs[t + 1], local_sub_idxs[t + 2] = (
                    local_sub_idxs[t + 2],
                    local_sub_idxs[t + 1],
                )

        out_indices.extend(local_sub_idxs)
        sub_local_pts: List[Tuple[float, float, float]] = []

        for old_v in used_verts:
            v_start = old_v * stride
            v_buf = bytearray(cm.vertex_bytes[v_start : v_start + stride])

            # 1. Position (Channel 0: offset 0, Float32 x 3)
            wx, wy, wz = struct.unpack_from("<fff", v_buf, 0)
            lx = (
                world_to_local[0][0] * wx
                + world_to_local[0][1] * wy
                + world_to_local[0][2] * wz
                + world_to_local[0][3]
            )
            ly = (
                world_to_local[1][0] * wx
                + world_to_local[1][1] * wy
                + world_to_local[1][2] * wz
                + world_to_local[1][3]
            )
            lz = (
                world_to_local[2][0] * wx
                + world_to_local[2][1] * wy
                + world_to_local[2][2] * wz
                + world_to_local[2][3]
            )
            struct.pack_into("<fff", v_buf, 0, lx, ly, lz)
            pt = (lx, ly, lz)
            sub_local_pts.append(pt)
            all_local_pts.append(pt)

            # 2. Normal (Channel 1: inverse-transpose = local_to_world^T * n_world)
            if has_normals:
                if norm_format == 0:
                    nx, ny, nz = struct.unpack_from("<fff", v_buf, norm_offset)
                else:
                    nx, ny, nz = struct.unpack_from("<eee", v_buf, norm_offset)
                lnx = (
                    local_to_world[0][0] * nx
                    + local_to_world[1][0] * ny
                    + local_to_world[2][0] * nz
                )
                lny = (
                    local_to_world[0][1] * nx
                    + local_to_world[1][1] * ny
                    + local_to_world[2][1] * nz
                )
                lnz = (
                    local_to_world[0][2] * nx
                    + local_to_world[1][2] * ny
                    + local_to_world[2][2] * nz
                )
                n_len = math.sqrt(lnx * lnx + lny * lny + lnz * lnz)
                if n_len > 1e-8:
                    lnx /= n_len
                    lny /= n_len
                    lnz /= n_len
                if norm_format == 0:
                    struct.pack_into("<fff", v_buf, norm_offset, lnx, lny, lnz)
                else:
                    struct.pack_into("<eee", v_buf, norm_offset, lnx, lny, lnz)

            # 3. Lightmap UV1 (Channel 5: Float32 x 2)
            if lm_st is not None:
                u1, v1 = struct.unpack_from("<ff", v_buf, uv1_offset)
                ul = (u1 - lm_st[2]) / lm_st[0]
                vl = (v1 - lm_st[3]) / lm_st[1]
                struct.pack_into("<ff", v_buf, uv1_offset, ul, vl)

            out_vertex_chunks.append(bytes(v_buf))

        center, extent = compute_aabb(sub_local_pts)
        sub_vc = len(used_verts)
        submesh_blocks.append(
            f"  - serializedVersion: 2\n"
            f"    firstByte: {current_first_byte}\n"
            f"    indexCount: {ic}\n"
            f"    topology: {sub['topology']}\n"
            f"    baseVertex: 0\n"
            f"    firstVertex: {current_first_vertex}\n"
            f"    vertexCount: {sub_vc}\n"
            f"    localAABB:\n"
            f"      m_Center: {{x: {fmt_float(center[0])}, y: {fmt_float(center[1])}, z: {fmt_float(center[2])}}}\n"
            f"      m_Extent: {{x: {fmt_float(extent[0])}, y: {fmt_float(extent[1])}, z: {fmt_float(extent[2])}}}"
        )
        current_first_vertex += sub_vc
        current_first_byte += ic * 2

    mesh_center, mesh_extent = compute_aabb(all_local_pts)
    total_verts = current_first_vertex
    total_data_size = total_verts * stride
    index_hex = (
        struct.pack(f"<{len(out_indices)}H", *out_indices).hex()
        if out_indices
        else ""
    )
    vertex_hex = b"".join(out_vertex_chunks).hex()
    mesh_name = f"Renderer-{renderer['rendererId']}"
    submeshes_yaml = "\n".join(submesh_blocks)

    return (
        f"%YAML 1.1\n"
        f"%TAG !u! tag:unity3d.com,2011:\n"
        f"--- !u!43 &4300000\n"
        f"Mesh:\n"
        f"  serializedVersion: 10\n"
        f"  m_ObjectHideFlags: 0\n"
        f"  m_CorrespondingSourceObject: {{fileID: 0}}\n"
        f"  m_PrefabInstance: {{fileID: 0}}\n"
        f"  m_PrefabAsset: {{fileID: 0}}\n"
        f"  m_Name: {mesh_name}\n"
        f"  m_SubMeshes:\n"
        f"{submeshes_yaml}\n"
        f"  m_Shapes:\n"
        f"    vertices: []\n"
        f"    shapes: []\n"
        f"    channels: []\n"
        f"    fullWeights: []\n"
        f"  m_BindPose: []\n"
        f"  m_BoneNameHashes:\n"
        f"  m_RootBoneNameHash: 0\n"
        f"  m_BonesAABB: []\n"
        f"  m_VariableBoneCountWeights:\n"
        f"    m_Data:\n"
        f"  m_MeshCompression: 0\n"
        f"  m_IsReadable: 1\n"
        f"  m_KeepVertices: 1\n"
        f"  m_KeepIndices: 1\n"
        f"  m_IndexFormat: 0\n"
        f"  m_IndexBuffer: {index_hex}\n"
        f"  m_VertexData:\n"
        f"    serializedVersion: 3\n"
        f"    m_VertexCount: {total_verts}\n"
        f"{cm.channels_yaml}"
        f"    m_DataSize: {total_data_size}\n"
        f"    _typelessdata: {vertex_hex}\n"
        f"  m_CompressedMesh:\n"
        f"    m_Vertices:\n"
        f"      m_NumItems: 0\n"
        f"      m_Range: 0\n"
        f"      m_Start: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_UV:\n"
        f"      m_NumItems: 0\n"
        f"      m_Range: 0\n"
        f"      m_Start: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_Normals:\n"
        f"      m_NumItems: 0\n"
        f"      m_Range: 0\n"
        f"      m_Start: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_Tangents:\n"
        f"      m_NumItems: 0\n"
        f"      m_Range: 0\n"
        f"      m_Start: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_Weights:\n"
        f"      m_NumItems: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_NormalSigns:\n"
        f"      m_NumItems: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_TangentSigns:\n"
        f"      m_NumItems: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_FloatColors:\n"
        f"      m_NumItems: 0\n"
        f"      m_Range: 0\n"
        f"      m_Start: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_BoneIndices:\n"
        f"      m_NumItems: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_Triangles:\n"
        f"      m_NumItems: 0\n"
        f"      m_Data:\n"
        f"      m_BitSize: 0\n"
        f"    m_UVInfo: 0\n"
        f"  m_LocalAABB:\n"
        f"    m_Center: {{x: {fmt_float(mesh_center[0])}, y: {fmt_float(mesh_center[1])}, z: {fmt_float(mesh_center[2])}}}\n"
        f"    m_Extent: {{x: {fmt_float(mesh_extent[0])}, y: {fmt_float(mesh_extent[1])}, z: {fmt_float(mesh_extent[2])}}}\n"
        f"  m_MeshUsageFlags: 0\n"
        f"  m_BakedConvexCollisionMesh:\n"
        f"  m_BakedTriangleCollisionMesh:\n"
        f"  m_MeshMetrics[0]: 1\n"
        f"  m_MeshMetrics[1]: 1\n"
        f"  m_MeshOptimizationFlags: -1\n"
        f"  m_StreamData:\n"
        f"    offset: 0\n"
        f"    size: 0\n"
        f"    path:\n"
    )


def patch_scene_yaml(scene_path: Path, scene_manifest: dict) -> Tuple[int, int, int]:
    txt = scene_path.read_text(encoding="utf-8", errors="ignore")
    matches = list(DOC_HEADER_RE.finditer(txt))
    if not matches:
        return 0, 0, 0

    mf_to_guid: Dict[int, str] = {}
    renderer_ids = set()
    meshatlas_ids = set()
    for r in scene_manifest["renderers"]:
        mf_to_guid[r["meshFilterId"]] = r["outputAssetGuid"]
        renderer_ids.add(r["rendererId"])
        if r.get("meshAtlasId") is not None:
            meshatlas_ids.add(r["meshAtlasId"])

    out_parts = [txt[: matches[0].start()]]
    patched_mf = 0
    patched_mr = 0
    patched_ma = 0

    for idx, m in enumerate(matches):
        class_id = int(m.group(1))
        file_id = int(m.group(2))
        doc_start = m.start()
        doc_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(txt)
        chunk = txt[doc_start:doc_end]

        if class_id == 33 and file_id in mf_to_guid:
            new_guid = mf_to_guid[file_id]
            new_chunk, n = re.subn(
                r"m_Mesh:\s*\{[^}]+\}",
                f"m_Mesh: {{fileID: 4300000, guid: {new_guid}, type: 2}}",
                chunk,
                count=1,
            )
            if n:
                chunk = new_chunk
                patched_mf += 1
        elif class_id == 23 and file_id in renderer_ids:
            new_chunk, n = re.subn(
                r"(m_StaticBatchInfo:\s*\n\s*firstSubMesh:\s*)\d+(\s*\n\s*subMeshCount:\s*)\d+",
                r"\g<1>0\g<2>0",
                chunk,
                count=1,
            )
            if n:
                chunk = new_chunk
                patched_mr += 1
        elif class_id == 114 and file_id in meshatlas_ids:
            new_chunk, n = re.subn(
                r"m_Enabled:\s*1",
                "m_Enabled: 0",
                chunk,
                count=1,
            )
            if n:
                chunk = new_chunk
                patched_ma += 1

        out_parts.append(chunk)

    scene_path.write_text("".join(out_parts), encoding="utf-8")
    return patched_mf, patched_mr, patched_ma


def patch_lighting_data_assets(
    client_dir: Path, renderer_guid_map: Dict[Tuple[str, int], str]
) -> Tuple[int, int]:
    """Update uvMesh references for static-batched renderers and sanitize NaN SH probes."""
    levels_dir = client_dir / "Assets" / "Levels"
    updated_uvmesh = 0
    sanitized_probes = 0

    zero_probe_lines = "\n".join(f"    sh[{i:2d}]: 0" for i in range(27))

    for ld_path in sorted(levels_dir.rglob("LightingData*.asset")):
        txt = ld_path.read_text(encoding="utf-8", errors="ignore")
        if "LightingDataAsset:" not in txt:
            continue
        modified = False

        # 1. Sanitize NaN / Inf / huge uninitialized SH probe values
        if "  m_BakedAmbientProbeInLinear:\n" in txt:
            pre, rest = txt.split("  m_BakedAmbientProbeInLinear:\n", 1)
            probe_sec, post = rest.split("\n  m_LightmappedRendererData:", 1)
            if (
                "NaN" in probe_sec
                or "Infinity" in probe_sec
                or "E+" in probe_sec
                or "e+" in probe_sec
            ):
                txt = (
                    pre
                    + "  m_BakedAmbientProbeInLinear:\n"
                    + zero_probe_lines
                    + "\n  m_LightmappedRendererData:"
                    + post
                )
                modified = True
                sanitized_probes += 1

        # 2. Update uvMesh GUIDs for static-batched renderers in this scene
        scene_folder = ld_path.parent
        scene_unity = scene_folder.parent / f"{scene_folder.name}.unity"
        if (
            scene_unity.exists()
            and "  m_LightmappedRendererData:\n" in txt
            and "  m_LightmappedRendererDataIDs:\n" in txt
        ):
            scene_rel = scene_unity.relative_to(client_dir).as_posix()
            pre, rest = txt.split("  m_LightmappedRendererData:\n", 1)
            data_sec, post = rest.split("  m_LightmappedRendererDataIDs:\n", 1)
            ids_sec = post.split("  m_EnlightenSceneMapping:", 1)[0]
            target_ids = [
                int(x) for x in re.findall(r"targetObject:\s*(-?\d+)", ids_sec)
            ]
            entries = re.split(r"(?=  - uvMesh:)", data_sec)
            entries = [e for e in entries if e.strip()]
            if len(entries) == len(target_ids):
                new_entries = []
                for tid, entry in zip(target_ids, entries):
                    new_guid = renderer_guid_map.get((scene_rel, tid))
                    if new_guid:
                        new_entry, n = re.subn(
                            r"uvMesh:\s*\{[^}]+\}",
                            f"uvMesh: {{fileID: 4300000, guid: {new_guid}, type: 2}}",
                            entry,
                            count=1,
                        )
                        if n and new_entry != entry:
                            entry = new_entry
                            updated_uvmesh += 1
                            modified = True
                    new_entries.append(entry)
                if modified:
                    txt = (
                        pre
                        + "  m_LightmappedRendererData:\n"
                        + "".join(new_entries)
                        + "  m_LightmappedRendererDataIDs:\n"
                        + post
                    )

        if modified:
            ld_path.write_text(txt, encoding="utf-8")

    return updated_uvmesh, sanitized_probes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client-dir",
        type=Path,
        default=Path("/tmp/ar_export/ExportedProject"),
        help="Path to Unity project root (containing Assets/).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("tools/geometry-recovery/manifest.json"),
        help="Path to geometry recovery index manifest.",
    )
    args = parser.parse_args()

    client_dir = args.client_dir.resolve()
    manifest_data = json.loads(args.manifest.read_text(encoding="utf-8"))

    recovered_root = client_dir / "Assets" / "RecoveredGeometry"
    recovered_root.mkdir(parents=True, exist_ok=True)
    write_folder_meta(recovered_root, "bs651:folder:Assets/RecoveredGeometry")

    cm_cache: Dict[str, CombinedMeshData] = {}
    renderer_guid_map: Dict[Tuple[str, int], str] = {}

    total_meshes_written = 0
    total_patched_mf = 0
    total_patched_mr = 0
    total_patched_ma = 0

    for scene_entry in manifest_data["scenes"]:
        scene_manifest_path = Path(scene_entry["manifestPath"])
        scene_manifest = json.loads(scene_manifest_path.read_text(encoding="utf-8"))
        scene_rel = scene_manifest["scenePath"]
        scene_name = scene_manifest["sceneName"]

        scene_out_dir = recovered_root / scene_name
        scene_out_dir.mkdir(parents=True, exist_ok=True)
        write_folder_meta(
            scene_out_dir, f"bs651:folder:Assets/RecoveredGeometry/{scene_name}"
        )

        for r in scene_manifest["renderers"]:
            cm_rel = r["combinedMeshAssetPath"]
            if cm_rel not in cm_cache:
                cm_cache[cm_rel] = CombinedMeshData(client_dir / cm_rel)
            cm = cm_cache[cm_rel]

            mesh_yaml = extract_renderer_mesh_yaml(cm, r)
            out_asset_path = client_dir / r["outputAssetPath"]
            out_asset_path.write_text(mesh_yaml, encoding="utf-8")
            write_mesh_meta(out_asset_path, r["outputAssetGuid"])
            renderer_guid_map[(scene_rel, r["rendererId"])] = r["outputAssetGuid"]
            total_meshes_written += 1

        mf_c, mr_c, ma_c = patch_scene_yaml(client_dir / scene_rel, scene_manifest)
        total_patched_mf += mf_c
        total_patched_mr += mr_c
        total_patched_ma += ma_c

    updated_uvmesh, sanitized_probes = patch_lighting_data_assets(
        client_dir, renderer_guid_map
    )

    print(
        f"Recovered {total_meshes_written} meshes across {len(manifest_data['scenes'])} scenes: "
        f"patched {total_patched_mf} MeshFilters, {total_patched_mr} MeshRenderers, "
        f"{total_patched_ma} MeshAtlas components, {updated_uvmesh} LightingData uvMesh refs, "
        f"and sanitized {sanitized_probes} LightingData SH probes."
    )


if __name__ == "__main__":
    main()
