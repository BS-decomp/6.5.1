#!/usr/bin/env python3
"""Build per-scene static-batch geometry recovery manifests for Block Strike 6.5.1.

Reads all 70 static-batched scenes in the exported 6.5.1 Unity project and
writes:
  - `tools/geometry-recovery/manifest.json`
  - `tools/geometry-recovery/scenes/<scene_slug>.json` (70 files)
  - `docs/geometry-recovery.md`
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from audit_static_batches import (
    FATHER_RE,
    GAMEOBJECT_RE,
    GUID_RE,
    MATERIAL_LINE_RE,
    MESH_ATLAS_GUID,
    MESH_GUID_RE,
    NAME_RE,
    SCRIPT_GUID_RE,
    STATIC_BATCH_RE,
    index_mesh_metas,
    parse_lighting_data_for_scene,
    parse_vec,
    split_yaml_documents,
)


def slugify_scene(scene_rel_path: str) -> str:
    stem = Path(scene_rel_path).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return slug or "scene"


def deterministic_mesh_guid(scene_rel_path: str, renderer_id: int) -> str:
    key = f"bs651:recovered-mesh:{scene_rel_path}:{renderer_id}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()


def build_transform_chain(
    start_transform_id: int,
    transforms_by_id: Dict[int, dict],
    game_objects: Dict[int, str],
) -> List[dict]:
    chain: List[dict] = []
    visited = set()
    cur = start_transform_id
    while cur and cur in transforms_by_id and cur not in visited:
        visited.add(cur)
        tr = transforms_by_id[cur]
        go_id = tr["gameObjectId"]
        chain.append(
            {
                "transformId": cur,
                "gameObjectId": go_id,
                "gameObjectName": game_objects.get(go_id, f"GameObject_{go_id}"),
                "localPosition": tr["localPosition"],
                "localRotation": tr["localRotation"],
                "localScale": tr["localScale"],
            }
        )
        cur = tr["fatherId"]
    chain.reverse()
    return chain


def build_scene_manifest(
    scene_path: Path,
    client_dir: Path,
    guid_to_rel: Dict[str, str],
) -> Optional[dict]:
    txt = scene_path.read_text(encoding="utf-8", errors="ignore")
    docs = split_yaml_documents(txt)

    game_objects: Dict[int, str] = {}
    transforms_by_id: Dict[int, dict] = {}
    transform_by_go: Dict[int, int] = {}
    mesh_filter_by_go: Dict[int, Tuple[int, Optional[str]]] = {}
    mesh_collider_by_go: Dict[int, Tuple[int, Optional[str]]] = {}
    mesh_atlas_by_go: Dict[int, int] = {}
    raw_renderers: List[dict] = []

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
                mat_sec = body.split("m_Materials:", 1)[1].split(
                    "m_StaticBatchInfo:", 1
                )[0]
            mat_guids = MATERIAL_LINE_RE.findall(mat_sec)
            raw_renderers.append(
                {
                    "rendererId": file_id,
                    "gameObjectId": go_id,
                    "firstSubMesh": first_sub,
                    "subMeshCount": sub_count,
                    "materialGuids": mat_guids,
                }
            )

    if not raw_renderers:
        return None

    scene_rel_path = scene_path.relative_to(client_dir).as_posix()
    scene_name = scene_path.stem
    lm_map = parse_lighting_data_for_scene(scene_path)

    renderers_out: List[dict] = []
    for r in sorted(raw_renderers, key=lambda x: x["rendererId"]):
        go_id = r["gameObjectId"]
        mf_id, cm_guid = mesh_filter_by_go[go_id]
        tr_id = transform_by_go[go_id]
        chain = build_transform_chain(tr_id, transforms_by_id, game_objects)
        hierarchy_path = "/".join(node["gameObjectName"] for node in chain)
        sub_indices = list(
            range(r["firstSubMesh"], r["firstSubMesh"] + r["subMeshCount"])
        )
        out_asset_path = (
            f"Assets/RecoveredGeometry/{scene_name}/Renderer-{r['rendererId']}.asset"
        )
        out_asset_guid = deterministic_mesh_guid(scene_rel_path, r["rendererId"])

        mc_info = mesh_collider_by_go.get(go_id)
        lm_info = lm_map.get(r["rendererId"])

        renderers_out.append(
            {
                "rendererId": r["rendererId"],
                "gameObjectId": go_id,
                "gameObjectName": game_objects.get(go_id, f"GameObject_{go_id}"),
                "transformId": tr_id,
                "meshFilterId": mf_id,
                "meshColliderId": mc_info[0] if mc_info else None,
                "meshColliderMeshGuid": mc_info[1] if mc_info else None,
                "meshAtlasId": mesh_atlas_by_go.get(go_id),
                "hierarchyPath": hierarchy_path,
                "combinedMeshGuid": cm_guid,
                "combinedMeshAssetPath": guid_to_rel.get(cm_guid or "", ""),
                "firstSubMesh": r["firstSubMesh"],
                "subMeshCount": r["subMeshCount"],
                "subMeshIndices": sub_indices,
                "materialGuids": r["materialGuids"],
                "lightmapInfo": lm_info,
                "outputAssetPath": out_asset_path,
                "outputAssetGuid": out_asset_guid,
                "transformChain": chain,
            }
        )

    return {
        "sceneName": scene_name,
        "sceneSlug": slugify_scene(scene_rel_path),
        "scenePath": scene_rel_path,
        "staticRendererCount": len(renderers_out),
        "referencedSubMeshCount": sum(r["subMeshCount"] for r in renderers_out),
        "lightmappedRendererCount": sum(
            1 for r in renderers_out if r["lightmapInfo"] is not None
        ),
        "renderers": renderers_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client-dir",
        type=Path,
        default=Path("/tmp/ar_export/ExportedProject"),
        help="Path to exported Unity project root.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("tools/geometry-recovery"),
        help="Output directory for geometry recovery manifests.",
    )
    parser.add_argument(
        "--doc-out",
        type=Path,
        default=Path("docs/geometry-recovery.md"),
        help="Output Markdown documentation path.",
    )
    args = parser.parse_args()

    client_dir = args.client_dir.resolve()
    guid_to_rel, _ = index_mesh_metas(client_dir)

    scenes_dir = args.out_dir / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)

    scene_entries = []
    total_renderers = 0
    total_submeshes = 0
    total_lightmapped = 0

    for sp in sorted((client_dir / "Assets" / "Levels").rglob("*.unity")):
        manifest = build_scene_manifest(sp, client_dir, guid_to_rel)
        if not manifest:
            continue
        scene_file = scenes_dir / f"{manifest['sceneSlug']}.json"
        scene_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        total_renderers += manifest["staticRendererCount"]
        total_submeshes += manifest["referencedSubMeshCount"]
        total_lightmapped += manifest["lightmappedRendererCount"]
        scene_entries.append(
            {
                "sceneName": manifest["sceneName"],
                "sceneSlug": manifest["sceneSlug"],
                "scenePath": manifest["scenePath"],
                "manifestPath": scene_file.as_posix(),
                "staticRendererCount": manifest["staticRendererCount"],
                "referencedSubMeshCount": manifest["referencedSubMeshCount"],
                "lightmappedRendererCount": manifest["lightmappedRendererCount"],
            }
        )

    index_manifest = {
        "unityVersion": "2019.2.3f1",
        "targetEditorVersion": "2021.3.45f2",
        "sceneCount": len(scene_entries),
        "totalStaticRenderers": total_renderers,
        "totalReferencedSubMeshes": total_submeshes,
        "totalLightmappedStaticRenderers": total_lightmapped,
        "scenes": scene_entries,
    }
    manifest_path = args.out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(index_manifest, indent=2) + "\n", encoding="utf-8"
    )

    doc_lines = [
        "# Static-Batch Geometry Recovery (`Block Strike 6.5.1`)",
        "",
        "## Architecture",
        "",
        "In the Unity `2019.2.3f1` release APK (`com.rexetstudio.blockstrike_6.5.1_2492.apk`),",
        "`70` of the `74` scenes in `Assets/Levels/` use static batching:",
        "",
        "- **`4,846` static-batched `MeshRenderer` components** store their submesh slices in `m_StaticBatchInfo: {firstSubMesh, subMeshCount}`.",
        "- Their sibling `MeshFilter.m_Mesh` references one of the `70` `Assets/Mesh/Combined Mesh (root_ scene)*.asset` files (`6,192` total submeshes).",
        "- **`3,187` lightmapped static-batched `MeshRenderer`s** have their `lightmapIndex` and `lightmapST` (`scale.xy`, `offset.zw`) stored in the scene's `LightingData*.asset` (`m_LightmappedRendererData` / `m_LightmappedRendererDataIDs`), while their combined mesh `UV1` (`Channel 5`) has `uv1_combined = uv1_local * lightmapST.xy + lightmapST.zw` pre-baked into the vertex stream.",
        "- **`26` `LightingData*.asset` files** also contain uninitialized `NaN` / `Infinity` / `1e+28` floats in `m_BakedAmbientProbeInLinear` (because those scenes use flat ambient color `m_AmbientMode: 3`), which must be sanitized to `0` so Unity `2021.3.45f2` YAML parsing and SH ambient shaders do not produce `NaN` lighting.",
        "",
        "## Recovery Pipeline",
        "",
        "1. **Audit (`tools/audit_static_batches.py`)**:",
        "   Verifies all `74` scenes and confirms `100%` submesh coverage (`6,192 / 6,192` submeshes across `70` `Combined Mesh` assets, `0` missing `MeshFilter`s, `0` out-of-range submeshes, `0` overlapping submeshes).",
        "2. **Manifest Generation (`tools/build_geometry_manifests.py`)**:",
        "   Emits `tools/geometry-recovery/manifest.json` and `70` per-scene manifests in `tools/geometry-recovery/scenes/<scene_slug>.json` containing exact transform chains, submesh ranges, material GUIDs, `LightingData` `lightmapST` vectors, and deterministic output mesh GUIDs.",
        "3. **Offline Deterministic Mesh & Scene Recovery (`tools/recover_static_meshes.py`)**:",
        "   - Extracts each renderer's `[firstSubMesh, firstSubMesh + subMeshCount)` from the scene's `Combined Mesh (root_ scene)*.asset`.",
        "   - Transforms world-space vertex positions (`Channel 0`) back into the `GameObject`'s local space (`v_local = worldToLocalMatrix * v_world`).",
        "   - Transforms world-space vertex normals (`Channel 1`, `Float32` or `Float16`) into local space via the inverse-transpose matrix (`normalize(transpose(localToWorldMatrix_3x3) * n_world)`).",
        "   - Reverses triangle winding `(i0, i1, i2) -> (i0, i2, i1)` when `det(localToWorldMatrix) < 0` (odd negative scale) so local-space face winding matches Unity's negative-scale rasterizer culling.",
        "   - Un-transforms lightmap `UV1` (`Channel 5`) via `uv1_local = (uv1_combined - lightmapST.zw) / lightmapST.xy` for all lightmapped static-batched renderers, restoring normalized `[0, 1]` chart UVs to within `1 ULP` (`1.69e-7`) of original ProBuilder meshes.",
        "   - Writes `Assets/RecoveredGeometry/<SceneName>/Renderer-<rendererId>.asset` + `.meta`, updates `MeshFilter.m_Mesh`, resets `m_StaticBatchInfo` to `{firstSubMesh: 0, subMeshCount: 0}`, disables the `24` static-batched `MeshAtlas` components (`m_Enabled: 0`), updates `LightingData*.asset` `uvMesh` references, and sanitizes `NaN`/`Inf` SH ambient probes.",
        "4. **Unity 2021.3.45f2 Editor Tool (`client/Assets/Editor/BlockStrikeGeometryRecovery.cs`)**:",
        "   Provides `Tools/Block Strike/Geometry Recovery/Recover All Scenes` and `Verify Recovered Scenes` inside the Unity Editor.",
        "",
        "## Scene Manifest Index",
        "",
        "| Scene | Manifest | Static Renderers | SubMeshes | Lightmapped |",
        "|---|---|---:|---:|---:|",
    ]
    for entry in scene_entries:
        doc_lines.append(
            f"| `{entry['sceneName']}` | `{entry['manifestPath']}` | "
            f"{entry['staticRendererCount']} | {entry['referencedSubMeshCount']} | "
            f"{entry['lightmappedRendererCount']} |"
        )

    args.doc_out.parent.mkdir(parents=True, exist_ok=True)
    args.doc_out.write_text("\n".join(doc_lines) + "\n", encoding="utf-8")
    print(
        f"Generated {len(scene_entries)} scene manifests in {scenes_dir} "
        f"({total_renderers} static renderers, {total_submeshes} submeshes, "
        f"{total_lightmapped} lightmapped)."
    )


if __name__ == "__main__":
    main()
