"""Extract SerializedShader definitions and compiled GLSL ES subprograms from the Block Strike 6.5.1 APK."""
import argparse
import json
from pathlib import Path
import re
import zipfile
import UnityPy


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_")


def extract_shaders(apk_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(apk_path) as z:
        names = z.namelist()
        groups = {}
        for n in names:
            if not n.startswith("assets/bin/Data/"):
                continue
            m = re.fullmatch(r"(.+)\.split(\d+)", n)
            if m:
                groups.setdefault(m.group(1), {})[int(m.group(2))] = n
            elif not n.endswith((".resource", ".resS")) and "/Managed/" not in n:
                groups[n] = {0: n}

        manifest = []
        idx = 0
        for base, parts in sorted(groups.items()):
            container_name = base.split("/")[-1]
            # Skip unity_builtin_extra internal hidden shaders unless used directly by project materials
            raw = b"".join(z.read(parts[i]) for i in sorted(parts))
            try:
                env = UnityPy.load(raw)
                for obj in env.objects:
                    if obj.type.name != "Shader":
                        continue
                    data = obj.read()
                    shader_name = data.m_ParsedForm.m_Name
                    if container_name in ("unity_builtin_extra", "unity default resources"):
                        if shader_name not in (
                            "Legacy Shaders/VertexLit",
                            "Legacy Shaders/Diffuse",
                            "Sprites/Default",
                            "UI/Default",
                        ):
                            continue
                    idx += 1
                    exported_text = data.export()
                    fname = f"shader_{idx:02d}_{sanitize_filename(shader_name)}.txt"
                    (out_dir / fname).write_text(exported_text, encoding="utf-8")
                    manifest.append(
                        {
                            "index": idx,
                            "shader_name": shader_name,
                            "container": container_name,
                            "path_id": obj.path_id,
                            "file": fname,
                        }
                    )
            except Exception:
                continue

        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Extracted {len(manifest)} shaders to {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apk",
        type=Path,
        default=Path("original/apk/com.rexetstudio.blockstrike_6.5.1_2492.apk"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tools/shader-extract"),
    )
    args = parser.parse_args()
    extract_shaders(args.apk, args.output)
