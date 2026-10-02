#!/usr/bin/env python3
"""Audit static-batched MeshRenderers across all Block Strike 6.5.1 scenes.

In Unity 2019.2.3f1 (the engine version used to build Block Strike 6.5.1),
static-batched MeshRenderers serialize their submesh range inside
`m_StaticBatchInfo: {firstSubMesh, subMeshCount}` (with `subMeshCount > 0`)
and their sibling `MeshFilter.m_Mesh` points to the scene's
`Assets/Mesh/Combined Mesh (root_ scene)*.asset`.

Meanwhile, per-renderer lightmap indices and scale/offset (`lightmapST`) are
stored in the scene's `LightingData*.asset` (`m_LightmappedRendererData` +
`m_LightmappedRendererDataIDs`).

This script audits all 74 scenes in the exported project, verifies that every
static-batched MeshRenderer maps cleanly to valid submeshes in its referenced
Combined Mesh, and writes `docs/static-batch-audit.json` and
`docs/static-batch-audit.md`.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DOC_HEADER_RE = re.compile(r"^--- !u!(\d+) &(-?\d+)\s*$", re.M)
GUID_RE = re.compile(r"guid:\s*([0-9a-f]{32})")
GAMEOBJECT_RE = re.compile(r"m_GameObject:\s*\{fileID:\s*(-?\d+)\}")
FATHER_RE = re.compile(r"m_Father:\s*\{fileID:\s*(-?\d+)\}")
NAME_RE = re.compile(r"^\s*m_Name:\s*(.*?)\s*$", re.M)
STATIC_BATCH_RE = re.compile(
    r"m_StaticBatchInfo:\s*\n\s*firstSubMesh:\s*(\d+)\s*\n\s*subMeshCount:\s*(\d+)"
)
MESH_GUID_RE = re.compile(
    r"m_Mesh:\s*\{fileID:\s*\d+,\s*guid:\s*([0-9a-f]{32}),\s*type:\s*\d+\}"
)
SCRIPT_GUID_RE = re.compile(
    r"m_Script:\s*\{fileID:\s*-?\d+,\s*guid:\s*([0-9a-f]{32}),\s*type:\s*\d+\}"
)
MATERIAL_LINE_RE = re.compile(
    r"^\s*-\s*\{fileID:\s*\d+,\s*guid:\s*([0-9a-f]{32}),\s*type:\s*\d+\}", re.M
)

MESH_ATLAS_GUID = "77acf2f35990d41a7230a8b5f22a2b04"


def split_yaml_documents(text: str) -> List[Tuple[int, int, str]]:
    matches = list(DOC_HEADER_RE.finditer(text))
    docs: List[Tuple[int, int, str]] = []
    for idx, match in enumerate(matches):
        class_id = int(match.group(1))
        file_id = int(match.group(2))
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        docs.append((class_id, file_id, text[start:end]))
    return docs


def parse_vec(block: str, field_name: str) -> List[float]:
    match = re.search(rf"{field_name}:\s*\{{([^}}]+)\}}", block)
    if not match:
        return []
    return [
        float(v)
        for v in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", match.group(1))
    ]


def index_mesh_metas(client_dir: Path) -> Tuple[Dict[str, str], Dict[str, int]]:
    guid_to_rel: Dict[str, str] = {}
    guid_to_submeshes: Dict[str, int] = {}
    mesh_dir = client_dir / "Assets" / "Mesh"
    for meta_path in sorted(mesh_dir.glob("*.asset.meta")):
        m = GUID_RE.search(meta_path.read_text(encoding="utf-8", errors="ignore"))
        if not m:
            continue
        guid = m.group(1)
        asset_path = meta_path.with_suffix("")
        rel_path = asset_path.relative_to(client_dir).as_posix()
        guid_to_rel[guid] = rel_path
        if asset_path.name.startswith("Combined Mesh"):
            txt = asset_path.read_text(encoding="utf-8", errors="ignore")
            sub_sec = txt.split("  m_SubMeshes:\n", 1)[1].split("  m_Shapes:", 1)[0]
            sub_count = sub_sec.count("- serializedVersion: 2")
            guid_to_submeshes[guid] = sub_count
    return guid_to_rel, guid_to_submeshes


def parse_lighting_data_for_scene(scene_path: Path) -> Dict[int, dict]:
    """Return mapping of renderer targetObject fileID -> lightmap info from LightingData*.asset."""
    scene_stem = scene_path.stem
    scene_sub = scene_path.parent / scene_stem
    if not scene_sub.is_dir():
        return {}
    result: Dict[int, dict] = {}
    for ld_path in sorted(scene_sub.glob("LightingData*.asset")):
        txt = ld_path.read_text(encoding="utf-8", errors="ignore")
        if "LightingDataAsset:" not in txt:
            continue
        if (
            "  m_LightmappedRendererData:\n" not in txt
            or "  m_LightmappedRendererDataIDs:\n" not in txt
        ):
            continue
        data_sec = txt.split("  m_LightmappedRendererData:\n", 1)[1].split(
            "  m_LightmappedRendererDataIDs:", 1
        )[0]
        ids_sec = txt.split("  m_LightmappedRendererDataIDs:\n", 1)[1].split(
            "  m_EnlightenSceneMapping:", 1
        )[0]
        target_ids = [int(x) for x in re.findall(r"targetObject:\s*(-?\d+)", ids_sec)]
        entries = re.split(r"  - uvMesh:", data_sec)[1:]
        for tid, entry in zip(target_ids, entries):
            lm_idx_m = re.search(r"lightmapIndex:\s*(\d+)", entry)
            lm_st = parse_vec(entry, "lightmapST")
            result[tid] = {
                "lightingDataAsset": ld_path.name,
                "lightmapIndex": int(lm_idx_m.group(1)) if lm_idx_m else 65535,
                "lightmapST": lm_st if len(lm_st) == 4 else [1.0, 1.0, 0.0, 0.0],
            }
    return result


def audit_scene(
    scene_path: Path,
    client_dir: Path,
    guid_to_rel: Dict[str, str],
    guid_to_submeshes: Dict[str, int],
) -> dict:
    txt = scene_path.read_text(encoding="utf-8", errors="ignore")
    docs = split_yaml_documents(txt)

    game_objects: Dict[int, str] = {}
    transforms_by_id: Dict[int, dict] = {}
    transform_by_go: Dict[int, int] = {}
    mesh_filter_by_go: Dict[int, Tuple[int, Optional[str]]] = {}
    mesh_collider_by_go: Dict[int, Tuple[int, Optional[str]]] = {}
    mesh_atlas_by_go: Dict[int, int] = {}
    renderers: List[dict] = []

    for class_id, file_id, body in docs:
        if class_id == 1:
            nm = NAME_RE.search(body)
            game_objects[file_id] = nm.group(1) if nm else f"GameObject_{file_id}"
        elif class_id == 4:
            go_m = GAMEOBJECT_RE.search(body)
            father_m = FATHER_RE.search(body)
            if go_m:
                go_id = int(go_m.group(1))
                transforms_by_id[file_id] = {
                    "transformId": file_id,
                    "gameObjectId": go_id,
                    "fatherId": int(father_m.group(1)) if father_m else 0,
                    "localPosition": parse_vec(body, "m_LocalPosition"),
                    "localRotation": parse_vec(body, "m_LocalRotation"),
                    "localScale": parse_vec(body, "m_LocalScale"),
                }
                transform_by_go[go_id] = file_id
        elif class_id == 33:
            go_m = GAMEOBJECT_RE.search(body)
            if go_m:
                mg = MESH_GUID_RE.search(body)
                mesh_filter_by_go[int(go_m.group(1))] = (
                    file_id,
                    mg.group(1) if mg else None,
                )
        elif class_id == 64:
            go_m = GAMEOBJECT_RE.search(body)
            if go_m:
                mg = MESH_GUID_RE.search(body)
                mesh_collider_by_go[int(go_m.group(1))] = (
                    file_id,
                    mg.group(1) if mg else None,
                )
        elif class_id == 114:
            sg = SCRIPT_GUID_RE.search(body)
            if sg and sg.group(1) == MESH_ATLAS_GUID:
                go_m = GAMEOBJECT_RE.search(body)
                if go_m:
                    mesh_atlas_by_go[int(go_m.group(1))] = file_id
        elif class_id == 23:
            sb = STATIC_BATCH_RE.search(body)
            if not sb:
                continue
            first_sub = int(sb.group(1))
            sub_count = int(sb.group(2))
            if sub_count <= 0:
                continue
            go_m = GAMEOBJECT_RE.search(body)
            go_id = int(go_m.group(1)) if go_m else 0
            mat_sec = ""
            if "m_Materials:" in body and "m_StaticBatchInfo:" in body:
                mat_sec = body.split("m_Materials:", 1)[1].split("m_StaticBatchInfo:", 1)[0]
            mat_guids = MATERIAL_LINE_RE.findall(mat_sec)
            renderers.append(
                {
                    "rendererId": file_id,
                    "gameObjectId": go_id,
                    "firstSubMesh": first_sub,
                    "subMeshCount": sub_count,
                    "materialGuids": mat_guids,
                }
            )

    lm_map = parse_lighting_data_for_scene(scene_path)

    combined_mesh_guids = set()
    used_submeshes: Dict[str, set] = {}
    overlapping_submeshes = 0
    out_of_range_submeshes = 0
    missing_mesh_filters = 0
    with_mesh_collider = 0
    with_mesh_atlas = 0
    lightmapped_count = 0

    for r in renderers:
        go_id = r["gameObjectId"]
        mf = mesh_filter_by_go.get(go_id)
        if not mf or not mf[1]:
            missing_mesh_filters += 1
            continue
        mf_id, cm_guid = mf
        r["meshFilterId"] = mf_id
        r["combinedMeshGuid"] = cm_guid
        r["combinedMeshPath"] = guid_to_rel.get(cm_guid, "")
        combined_mesh_guids.add(cm_guid)

        total_subs = guid_to_submeshes.get(cm_guid, 0)
        used = used_submeshes.setdefault(cm_guid, set())
        for sub_idx in range(r["firstSubMesh"], r["firstSubMesh"] + r["subMeshCount"]):
            if sub_idx < 0 or sub_idx >= total_subs:
                out_of_range_submeshes += 1
            if sub_idx in used:
                overlapping_submeshes += 1
            used.add(sub_idx)

        if go_id in mesh_collider_by_go and mesh_collider_by_go[go_id][1]:
            with_mesh_collider += 1
        if go_id in mesh_atlas_by_go:
            with_mesh_atlas += 1
        if r["rendererId"] in lm_map:
            lightmapped_count += 1

    combined_meshes_summary = []
    for g in sorted(combined_mesh_guids):
        combined_meshes_summary.append(
            {
                "guid": g,
                "path": guid_to_rel.get(g, ""),
                "totalSubMeshes": guid_to_submeshes.get(g, 0),
                "referencedSubMeshes": len(used_submeshes.get(g, set())),
            }
        )

    return {
        "sceneName": scene_path.stem,
        "scenePath": scene_path.relative_to(client_dir).as_posix(),
        "staticRendererCount": len(renderers),
        "referencedSubMeshCount": sum(len(s) for s in used_submeshes.values()),
        "lightmappedStaticRendererCount": lightmapped_count,
        "staticWithMeshColliderCount": with_mesh_collider,
        "staticWithMeshAtlasCount": with_mesh_atlas,
        "missingMeshFilters": missing_mesh_filters,
        "outOfRangeSubMeshes": out_of_range_submeshes,
        "overlappingSubMeshes": overlapping_submeshes,
        "combinedMeshes": combined_meshes_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client-dir",
        type=Path,
        default=Path("/tmp/ar_export/ExportedProject"),
        help="Path to exported Unity project root (containing Assets/).",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("docs/static-batch-audit.json"),
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=Path("docs/static-batch-audit.md"),
        help="Output Markdown report path.",
    )
    args = parser.parse_args()

    client_dir = args.client_dir.resolve()
    guid_to_rel, guid_to_submeshes = index_mesh_metas(client_dir)

    scene_paths = sorted((client_dir / "Assets" / "Levels").rglob("*.unity"))
    scene_reports = [
        audit_scene(sp, client_dir, guid_to_rel, guid_to_submeshes)
        for sp in scene_paths
    ]

    batched_scenes = [s for s in scene_reports if s["staticRendererCount"] > 0]
    unbatched_scenes = [s for s in scene_reports if s["staticRendererCount"] == 0]

    summary = {
        "unityVersion": "2019.2.3f1",
        "targetEditorVersion": "2021.3.45f2",
        "totalScenes": len(scene_reports),
        "staticBatchedScenes": len(batched_scenes),
        "unbatchedScenes": [s["scenePath"] for s in unbatched_scenes],
        "totalCombinedMeshAssets": len(guid_to_submeshes),
        "totalStaticRenderers": sum(s["staticRendererCount"] for s in scene_reports),
        "totalReferencedSubMeshes": sum(
            s["referencedSubMeshCount"] for s in scene_reports
        ),
        "totalCombinedMeshSubMeshes": sum(guid_to_submeshes.values()),
        "totalLightmappedStaticRenderers": sum(
            s["lightmappedStaticRendererCount"] for s in scene_reports
        ),
        "totalStaticWithMeshCollider": sum(
            s["staticWithMeshColliderCount"] for s in scene_reports
        ),
        "totalStaticWithMeshAtlas": sum(
            s["staticWithMeshAtlasCount"] for s in scene_reports
        ),
        "totalMissingMeshFilters": sum(
            s["missingMeshFilters"] for s in scene_reports
        ),
        "totalOutOfRangeSubMeshes": sum(
            s["outOfRangeSubMeshes"] for s in scene_reports
        ),
        "totalOverlappingSubMeshes": sum(
            s["overlappingSubMeshes"] for s in scene_reports
        ),
        "scenes": scene_reports,
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Static-Batch Geometry Audit (`Block Strike 6.5.1`)",
        "",
        "## Overview",
        "",
        f"- **Source APK Unity Version**: `{summary['unityVersion']}`",
        f"- **Target Unity Editor Version**: `{summary['targetEditorVersion']}`",
        f"- **Total Scenes (`Assets/Levels/**/*.unity`)**: `{summary['totalScenes']}`",
        f"- **Scenes with Static-Batched Geometry**: `{summary['staticBatchedScenes']}`",
        f"- **Scenes without Static-Batched Geometry**: `{len(summary['unbatchedScenes'])}` (`{', '.join(summary['unbatchedScenes'])}`)",
        f"- **Total `Combined Mesh (root_ scene)*.asset` Files**: `{summary['totalCombinedMeshAssets']}`",
        f"- **Total Static-Batched `MeshRenderer`s**: `{summary['totalStaticRenderers']}`",
        f"- **Total Submeshes in Combined Meshes**: `{summary['totalCombinedMeshSubMeshes']}` (`{summary['totalReferencedSubMeshes']}` referenced)",
        f"- **Lightmapped Static-Batched `MeshRenderer`s**: `{summary['totalLightmappedStaticRenderers']}`",
        f"- **Static-Batched `GameObject`s with Original `pb_Mesh` on `MeshCollider`**: `{summary['totalStaticWithMeshCollider']}`",
        f"- **Static-Batched `GameObject`s with `MeshAtlas`**: `{summary['totalStaticWithMeshAtlas']}`",
        f"- **Missing `MeshFilter` Components**: `{summary['totalMissingMeshFilters']}`",
        f"- **Out-of-Range Submeshes**: `{summary['totalOutOfRangeSubMeshes']}`",
        f"- **Overlapping Submeshes**: `{summary['totalOverlappingSubMeshes']}`",
        "",
        "## Per-Scene Static Batch Summary",
        "",
        "| Scene | Path | Combined Mesh Asset | Static Renderers | SubMeshes (Ref / Total) | Lightmapped | MeshCollider | MeshAtlas |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]

    for s in batched_scenes:
        cm_names = ", ".join(Path(c["path"]).name for c in s["combinedMeshes"])
        total_cm_subs = sum(c["totalSubMeshes"] for c in s["combinedMeshes"])
        md_lines.append(
            f"| `{s['sceneName']}` | `{s['scenePath']}` | `{cm_names}` | "
            f"{s['staticRendererCount']} | {s['referencedSubMeshCount']} / {total_cm_subs} | "
            f"{s['lightmappedStaticRendererCount']} | {s['staticWithMeshColliderCount']} | "
            f"{s['staticWithMeshAtlasCount']} |"
        )

    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(
        f"Audited {summary['totalScenes']} scenes: "
        f"{summary['staticBatchedScenes']} static-batched scenes, "
        f"{summary['totalStaticRenderers']} static renderers, "
        f"{summary['totalReferencedSubMeshes']}/{summary['totalCombinedMeshSubMeshes']} submeshes."
    )


if __name__ == "__main__":
    main()
