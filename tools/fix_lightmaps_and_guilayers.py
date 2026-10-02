#!/usr/bin/env python3
"""
Fixes Unity 2021.3.45f2 LTS Editor issues in client/:
1. Strips obsolete GUILayer (!u!92) components from all 73 scenes and 1 prefab.
2. Installs canonical project shaders for Mobile/Unlit (Supports Lightmap) (10708),
   Mobile/VertexLit (Only Directional Lights) (10707), and Mobile/VertexLit (10701)
   with explicit 2.0 * lightmap.rgb dLDR decoding matching the 6.5.1 Android APK.
3. Rebinds all 119 materials referencing built-in fileIDs 10708, 10707, and 10701
   to the canonical project shaders.
4. Normalizes all 73 Lightmap-*_comp_light.png.meta files (textureType: 0, lightmap: 0,
   alphaUsage: 0, alphaIsTransparency: 0) so raw dLDR pixels are preserved on Desktop.
5. Installs LegacyLightmapBinder.cs ([ExecuteAlways]), populates BS651_LegacyLightmaps
   objects across all 71 lightmapped scenes (70 maps + Menu.unity), and populates
   m_BakedAmbientProbeInLinear in LightingData*.asset from RenderSettings.m_AmbientSkyColor.
"""

import hashlib
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SHADER_MAP = {
    "10708": (
        "Mobile-Lightmap-Unlit.shader",
        "977b8dcdfae84da47b9ca3f8973ea75b",
    ),
    "10707": (
        "Mobile-VertexLit-OnlyDirectionalLights.shader",
        "d20b77d9c078bcf44b2b6e4cdb06c0ae",
    ),
    "10701": (
        "Mobile-VertexLit.shader",
        "935fac1d1b691b24893f212c0fabd21c",
    ),
}

BINDER_GUID = hashlib.md5(b"BS651:Assets/Scripts/Assembly-CSharp/LegacyLightmapBinder.cs").hexdigest()


def git_ls_files(prefix: str) -> list[str]:
    out = subprocess.check_output(["git", "ls-files", prefix], cwd=ROOT).decode("utf-8")
    return [line for line in out.splitlines() if line]


def git_show_index(path: str) -> str:
    p = ROOT / path
    if p.exists():
        return p.read_text(encoding="utf-8")
    return subprocess.check_output(["git", "show", f":{path}"], cwd=ROOT).decode("utf-8")


def write_text(rel_path: str, content: str) -> None:
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")


def shader_meta(guid: str) -> str:
    return (
        "fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        "ShaderImporter:\n"
        "  externalObjects: {}\n"
        "  defaultTextures: []\n"
        "  nonModifiableTextures: []\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n"
    )


def mono_meta(guid: str) -> str:
    return (
        "fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        "MonoImporter:\n"
        "  externalObjects: {}\n"
        "  serializedVersion: 2\n"
        "  defaultReferences: []\n"
        "  executionOrder: -100\n"
        "  icon: {instanceID: 0}\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n"
    )


def srgb_to_linear(c: float) -> float:
    c = max(0.0, min(1.0, c))
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def strip_guilayer_from_yaml(txt: str) -> tuple[str, int]:
    guilayer_ids = set(re.findall(r"^--- !u!92 &(\d+)\s*$", txt, re.M))
    if not guilayer_ids:
        return txt, 0

    # Remove component references from GameObject m_Component lists
    for gid in guilayer_ids:
        txt = re.sub(rf"^[ \t]*-\s*component:\s*\{{fileID:\s*{gid}\}}\r?\n", "", txt, flags=re.M)

    # Remove the --- !u!92 &<id> document blocks
    parts = re.split(r"(^--- !u!\d+ &\d+.*$)", txt, flags=re.M)
    out = [parts[0]]
    removed = 0
    for i in range(1, len(parts), 2):
        header = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        m = re.match(r"^--- !u!92 &(\d+)", header)
        if m and m.group(1) in guilayer_ids:
            removed += 1
            continue
        out.append(header)
        out.append(body)

    return "".join(out), removed


def parse_lighting_data(ld_txt: str):
    # Extract m_Lightmaps texture references
    lm_section = ld_txt.split("m_AOTextures:")[0]
    lightmaps = re.findall(
        r"m_Lightmap:\s*\{fileID:\s*(\d+),\s*guid:\s*([0-9a-f]{32}),\s*type:\s*(\d+)\}",
        lm_section,
    )

    # Extract m_LightmappedRendererData entries
    rd_start = ld_txt.find("m_LightmappedRendererData:")
    id_start = ld_txt.find("m_LightmappedRendererDataIDs:")
    lights_start = ld_txt.find("m_Lights:")
    if rd_start == -1 or id_start == -1:
        return lightmaps, [], [], []

    rd_block = ld_txt[rd_start:id_start]
    id_block = ld_txt[id_start : (lights_start if lights_start != -1 else len(ld_txt))]

    lm_indices = [int(x) for x in re.findall(r"lightmapIndex:\s*(\d+)", rd_block)]
    lm_sts = re.findall(
        r"lightmapST:\s*\{x:\s*([^,]+),\s*y:\s*([^,]+),\s*z:\s*([^,]+),\s*w:\s*([^\}]+)\}",
        rd_block,
    )
    target_ids = [int(x) for x in re.findall(r"targetObject:\s*(\d+)", id_block)]

    count = min(len(lm_indices), len(lm_sts), len(target_ids))
    return lightmaps, target_ids[:count], lm_indices[:count], lm_sts[:count]


def format_legacy_binder_yaml(
    max_id: int,
    lightmaps: list[tuple[str, str, str]],
    target_ids: list[int],
    lm_indices: list[int],
    lm_sts: list[tuple[str, str, str, str]],
) -> str:
    go_id = max_id + 100
    tr_id = max_id + 101
    mb_id = max_id + 102

    first_lm = (
        f"{{fileID: {lightmaps[0][0]}, guid: {lightmaps[0][1]}, type: {lightmaps[0][2]}}}"
        if lightmaps
        else "{fileID: 0}"
    )

    lm_colors_lines = []
    for fid, guid, tp in lightmaps:
        lm_colors_lines.append(f"  - {{fileID: {fid}, guid: {guid}, type: {tp}}}")
    lm_colors_yaml = "  lightmapColors:\n" + "\n".join(lm_colors_lines) if lm_colors_lines else "  lightmapColors: []"

    if target_ids:
        renderers_yaml = "  renderers:\n" + "\n".join(f"  - {{fileID: {tid}}}" for tid in target_ids)
        hex_idx = "".join(int(idx).to_bytes(4, "little", signed=False).hex() for idx in lm_indices)
        indexes_yaml = f"  lightmapIndexes: {hex_idx}"
        sts_yaml = "  lightmapScaleOffsets:\n" + "\n".join(
            f"  - {{x: {st[0].strip()}, y: {st[1].strip()}, z: {st[2].strip()}, w: {st[3].strip()}}}"
            for st in lm_sts
        )
    else:
        renderers_yaml = "  renderers: []"
        indexes_yaml = "  lightmapIndexes: "
        sts_yaml = "  lightmapScaleOffsets: []"

    return (
        f"--- !u!1 &{go_id}\n"
        "GameObject:\n"
        "  serializedVersion: 6\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_CorrespondingSourceObject: {fileID: 0}\n"
        "  m_PrefabInstance: {fileID: 0}\n"
        "  m_PrefabAsset: {fileID: 0}\n"
        "  m_Component:\n"
        f"  - component: {{fileID: {tr_id}}}\n"
        f"  - component: {{fileID: {mb_id}}}\n"
        "  m_Layer: 0\n"
        "  m_Name: BS651_LegacyLightmaps\n"
        "  m_TagString: Untagged\n"
        "  m_Icon: {fileID: 0}\n"
        "  m_NavMeshLayer: 0\n"
        "  m_StaticEditorFlags: 0\n"
        "  m_IsActive: 1\n"
        f"--- !u!4 &{tr_id}\n"
        "Transform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_CorrespondingSourceObject: {fileID: 0}\n"
        "  m_PrefabInstance: {fileID: 0}\n"
        "  m_PrefabAsset: {fileID: 0}\n"
        f"  m_GameObject: {{fileID: {go_id}}}\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 0}\n"
        "  m_RootOrder: 0\n"
        "  m_LocalEulerAnglesHint: {x: 0, y: 0, z: 0}\n"
        f"--- !u!114 &{mb_id}\n"
        "MonoBehaviour:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_CorrespondingSourceObject: {fileID: 0}\n"
        "  m_PrefabInstance: {fileID: 0}\n"
        "  m_PrefabAsset: {fileID: 0}\n"
        f"  m_GameObject: {{fileID: {go_id}}}\n"
        "  m_Enabled: 1\n"
        "  m_EditorHideFlags: 0\n"
        f"  m_Script: {{fileID: 11500000, guid: {BINDER_GUID}, type: 3}}\n"
        "  m_Name: \n"
        "  m_EditorClassIdentifier: \n"
        f"  lightmapColor: {first_lm}\n"
        f"{lm_colors_yaml}\n"
        f"{renderers_yaml}\n"
        f"{indexes_yaml}\n"
        f"{sts_yaml}\n"
    )


def main() -> None:
    modified_files: list[str] = []

    # 1. Install the 3 canonical built-in lightmap shaders + .meta files
    for fid, (shader_name, guid) in SHADER_MAP.items():
        src = (ROOT / "tools" / "shader-canonical" / "builtin" / shader_name).read_text(encoding="utf-8")
        dst_rel = f"client/Assets/Shader/{shader_name}"
        write_text(dst_rel, src)
        write_text(f"{dst_rel}.meta", shader_meta(guid))
        modified_files.extend([dst_rel, f"{dst_rel}.meta"])

    # 2. Install LegacyLightmapBinder.cs + .meta
    binder_src = (ROOT / "tools" / "unity-editor" / "LegacyLightmapBinder.cs").read_text(encoding="utf-8")
    binder_rel = "client/Assets/Scripts/Assembly-CSharp/LegacyLightmapBinder.cs"
    write_text(binder_rel, binder_src)
    write_text(f"{binder_rel}.meta", mono_meta(BINDER_GUID))
    modified_files.extend([binder_rel, f"{binder_rel}.meta"])

    # 3. Rebind all 119 materials referencing built-in shader fileIDs 10708, 10707, 10701
    mat_files = [p for p in git_ls_files("client/Assets") if p.endswith(".mat")]
    rebound_counts = {k: 0 for k in SHADER_MAP}
    for mat_rel in mat_files:
        txt = git_show_index(mat_rel)
        new_txt = txt
        for fid, (_, guid) in SHADER_MAP.items():
            pattern = f"{{fileID: {fid}, guid: 0000000000000000f000000000000000, type: 0}}"
            replacement = f"{{fileID: 4800000, guid: {guid}, type: 3}}"
            if pattern in new_txt:
                new_txt = new_txt.replace(pattern, replacement)
                rebound_counts[fid] += 1
        if new_txt != txt:
            write_text(mat_rel, new_txt)
            modified_files.append(mat_rel)

    print(f"Rebound materials: {rebound_counts} (total={sum(rebound_counts.values())})")

    # 4. Normalize all 73 Lightmap-*_comp_light.png.meta files (RGB24 uncompressed on Desktop & Android)
    lm_metas = [
        p
        for p in git_ls_files("client/Assets/Levels")
        if p.endswith("_comp_light.png.meta")
    ]
    lm_meta_updated = 0
    for meta_rel in lm_metas:
        txt = git_show_index(meta_rel)
        new_txt = txt
        new_txt = re.sub(r"alphaUsage:\s*\d+", "alphaUsage: 0", new_txt)
        new_txt = re.sub(r"alphaIsTransparency:\s*\d+", "alphaIsTransparency: 0", new_txt)
        new_txt = re.sub(r"textureType:\s*\d+", "textureType: 0", new_txt)
        new_txt = re.sub(r"lightmap:\s*\d+", "lightmap: 0", new_txt)
        new_txt = re.sub(r"textureFormat:\s*-?\d+", "textureFormat: 3", new_txt)
        new_txt = re.sub(r"textureCompression:\s*\d+", "textureCompression: 0", new_txt)
        new_txt = re.sub(
            r"(buildTarget:\s*(?:Standalone|Android)\s*\n(?:[ \t]+[^\n]+\n)*?[ \t]+overridden:\s*)\d+",
            r"\g<1>1",
            new_txt,
        )
        if new_txt != txt:
            write_text(meta_rel, new_txt)
            modified_files.append(meta_rel)
            lm_meta_updated += 1
    print(f"Normalized {lm_meta_updated}/{len(lm_metas)} Lightmap PNG .meta files")

    # Build map of LightingData GUID -> path
    ld_guid_to_path: dict[str, str] = {}
    for p in git_ls_files("client/Assets/Levels"):
        if p.endswith(".asset.meta") and "LightingData" in p:
            m_txt = git_show_index(p)
            m = re.search(r"guid:\s*([0-9a-f]{32})", m_txt)
            if m:
                ld_guid_to_path[m.group(1)] = p[:-5]

    # 5. Strip GUILayer from all .prefab and .unity files, and bind LegacyLightmapBinder on lightmapped scenes
    prefab_files = [p for p in git_ls_files("client/Assets") if p.endswith(".prefab")]
    prefab_guilayers = 0
    for pf_rel in prefab_files:
        txt = git_show_index(pf_rel)
        if "--- !u!92 &" not in txt:
            continue
        new_txt, removed = strip_guilayer_from_yaml(txt)
        if removed > 0:
            write_text(pf_rel, new_txt)
            modified_files.append(pf_rel)
            prefab_guilayers += removed

    scene_files = [p for p in git_ls_files("client/Assets/Levels") if p.endswith(".unity")]
    scene_guilayers = 0
    scenes_bound = 0
    ld_updated = 0

    for sc_rel in scene_files:
        txt = git_show_index(sc_rel)
        new_txt, removed = strip_guilayer_from_yaml(txt)
        scene_guilayers += removed

        # Check if scene references a LightingDataAsset with lightmaps
        m_ld = re.search(r"m_LightingDataAsset:\s*\{fileID:\s*112000000,\s*guid:\s*([0-9a-f]{32})", new_txt)
        if m_ld and m_ld.group(1) in ld_guid_to_path:
            ld_rel = ld_guid_to_path[m_ld.group(1)]
            ld_txt = git_show_index(ld_rel)
            lightmaps, target_ids, lm_indices, lm_sts = parse_lighting_data(ld_txt)

            if lightmaps:
                # Update LightingData's m_BakedAmbientProbeInLinear from RenderSettings.m_AmbientSkyColor
                m_amb = re.search(
                    r"m_AmbientSkyColor:\s*\{r:\s*([^,]+),\s*g:\s*([^,]+),\s*b:\s*([^,]+),",
                    new_txt,
                )
                if m_amb:
                    r_lin = srgb_to_linear(float(m_amb.group(1)))
                    g_lin = srgb_to_linear(float(m_amb.group(2)))
                    b_lin = srgb_to_linear(float(m_amb.group(3)))
                    new_ld_txt = ld_txt
                    new_ld_txt = re.sub(r"sh\[\s*0\]:\s*[^\n]+", f"sh[ 0]: {r_lin:.7g}", new_ld_txt, count=1)
                    new_ld_txt = re.sub(r"sh\[\s*9\]:\s*[^\n]+", f"sh[ 9]: {g_lin:.7g}", new_ld_txt, count=1)
                    new_ld_txt = re.sub(r"sh\[18\]:\s*[^\n]+", f"sh[18]: {b_lin:.7g}", new_ld_txt, count=1)
                    if new_ld_txt != ld_txt:
                        write_text(ld_rel, new_ld_txt)
                        modified_files.append(ld_rel)
                        ld_updated += 1

                # Add or replace BS651_LegacyLightmaps in the scene
                if "BS651_LegacyLightmaps" not in new_txt:
                    all_ids = [int(x) for x in re.findall(r"^--- !u!\d+ &(\d+)", new_txt, re.M)]
                    max_id = max(all_ids) if all_ids else 10000
                    binder_yaml = format_legacy_binder_yaml(max_id, lightmaps, target_ids, lm_indices, lm_sts)
                    if not new_txt.endswith("\n"):
                        new_txt += "\n"
                    new_txt += binder_yaml
                    scenes_bound += 1

        # Unlink m_LightingDataAsset so Unity 2021 does not override LegacyLightmapBinder with broken baked data
        new_txt = re.sub(
            r"m_LightingDataAsset:\s*\{fileID:\s*112000000,\s*guid:\s*[0-9a-f]{32},\s*type:\s*\d+\}",
            "m_LightingDataAsset: {fileID: 0}",
            new_txt,
        )

        if new_txt != txt:
            write_text(sc_rel, new_txt)
            modified_files.append(sc_rel)

    print(
        f"Stripped {scene_guilayers} GUILayers from scenes and {prefab_guilayers} from prefabs; "
        f"bound LegacyLightmapBinder in {scenes_bound} scenes; updated {ld_updated} LightingData assets."
    )
    print(f"Total modified/created files on disk: {len(set(modified_files))}")


if __name__ == "__main__":
    main()
