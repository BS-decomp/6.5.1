#!/usr/bin/env python3
"""
Deterministic Unity 2021.3.45f2 LTS compatibility patcher for Block Strike 6.5.1.

Fixes IL2CPP + Beebyte Obfuscator 2.7.1 + ILSpy decompilation artifacts across
Assets/Scripts/, removes conflicting legacy UnityEngine.UI.dll plugin, updates
ProjectSettings/ProjectVersion.txt and Packages/manifest.json for Unity 2021.3.45f2 LTS,
and installs the Block Strike Editor verification/recovery tools.
"""

import argparse
import glob
import json
import os
import re
import shutil
import uuid


ATLAS_PROPS = [
    ("Material", "spriteMaterial", "IIJJJJJJIJJIIIJIIJJIJIIJJJIJIJJIIIIIJIIJJIJJJII", True, "null"),
    ("List<IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ>", "spriteList", "JIIJJJJIJJIIIJIJJIJIJJIJJIJIJIIIIJIIJIIIIJIJIJI", True, "null"),
    ("Texture", "texture", "IIJIJIIIJJJIIIJJIIJJIJIIIIIIJJJIIJIJIJJIIIJIIIJ", False, "null"),
    ("float", "pixelSize", "IIJIJIIIIIIJJIIIJJIJJIJJJJIJIJIJIIJIIJJIJ", True, "0f"),
    ("bool", "premultipliedAlpha", "JIJJJIIJIIIJIJIJIIJIIIIJJIJIJIJIJIJIJJIJJJJIIJI", False, "false"),
    ("IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII", "replacement", "JJJJJJIJJIJJJIIJIIIIJIJJJJJJJIJIJIJIJJIJIIIJJII", True, "null"),
]


def patch_project_settings(client_dir: str) -> None:
    pv_path = os.path.join(client_dir, "ProjectSettings", "ProjectVersion.txt")
    with open(pv_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(
            "m_EditorVersion: 2021.3.45f2\n"
            "m_EditorVersionWithRevision: 2021.3.45f2 (0da89fac8e79)\n"
        )

    manifest_path = os.path.join(client_dir, "Packages", "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    deps = manifest.setdefault("dependencies", {})
    deps["com.unity.ugui"] = "1.0.0"
    manifest["dependencies"] = dict(sorted(deps.items()))
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def patch_plugins(client_dir: str) -> int:
    removed = 0
    for ext in ("", ".meta"):
        ui_dll = os.path.join(client_dir, "Assets", "Plugins", f"UnityEngine.UI.dll{ext}")
        if os.path.exists(ui_dll):
            os.remove(ui_dll)
            removed += 1

    for meta_path in sorted(glob.glob(os.path.join(client_dir, "Assets", "Plugins", "*.dll.meta"))):
        with open(meta_path, "r", encoding="utf-8") as f:
            txt = f.read()
        new_txt = txt.replace(
            "  - first:\n      Editor: Editor\n    second:\n      enabled: 0",
            "  - first:\n      Editor: Editor\n    second:\n      enabled: 1",
        )
        if new_txt != txt:
            with open(meta_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_txt)
    return removed


def remove_assembly_info(client_dir: str) -> int:
    removed = 0
    for rel_props in (
        os.path.join("Assets", "Scripts", "Assembly-CSharp", "Properties"),
        os.path.join("Assets", "Plugins", "Assembly-CSharp-firstpass", "Properties"),
    ):
        props_dir = os.path.join(client_dir, rel_props)
        props_meta = props_dir + ".meta"
        if os.path.isdir(props_dir):
            shutil.rmtree(props_dir)
            removed += 1
        if os.path.exists(props_meta):
            os.remove(props_meta)
            removed += 1
    return removed


def patch_ingui_atlas(scripts_dir: str) -> None:
    iface_path = os.path.join(scripts_dir, "Assembly-CSharp", "IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII.cs")
    with open(iface_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # Replace get_*/set_* method declarations with C# property declarations
    replacements = [
        ("Material get_spriteMaterial();\n", "Material spriteMaterial { get; set; }\n"),
        ("\tvoid set_spriteMaterial(Material JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI);\n", ""),
        ("List<IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ> get_spriteList();\n", "List<IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ> spriteList { get; set; }\n"),
        ("\tvoid set_spriteList(List<IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ> JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI);\n", ""),
        ("Texture get_texture();\n", "Texture texture { get; }\n"),
        ("float get_pixelSize();\n", "float pixelSize { get; set; }\n"),
        ("\tvoid set_pixelSize(float JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI);\n", ""),
        ("bool get_premultipliedAlpha();\n", "bool premultipliedAlpha { get; }\n"),
        ("IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII get_replacement();\n", "IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII replacement { get; set; }\n"),
        ("\tvoid set_replacement(IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI);\n", ""),
    ]
    for old, new in replacements:
        txt = txt.replace(old, new)
    with open(iface_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)

    # Patch UIAtlas.cs
    ui_atlas_path = os.path.join(scripts_dir, "Assembly-CSharp", "UIAtlas.cs")
    with open(ui_atlas_path, "r", encoding="utf-8") as f:
        utxt = f.read()

    for _, prop_name, _, has_set, _ in [
        ("Material", "spriteMaterial", "", True, "null"),
        ("List<IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ>", "spriteList", "", True, "null"),
        ("Texture", "texture", "", False, "null"),
        ("float", "pixelSize", "", True, "0f"),
        ("bool", "premultipliedAlpha", "", False, "false"),
        ("IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII", "replacement", "", True, "null"),
    ]:
        utxt = utxt.replace(f"return get_{prop_name}();", f"return {prop_name};")
        utxt = utxt.replace(f"=> get_{prop_name}();", f"=> {prop_name};")
        if has_set:
            utxt = utxt.replace(f"set_{prop_name}(value);", f"{prop_name} = value;")

    # Remove raw get_*/set_* methods and add clean C# properties
    for prop_name in ("spriteMaterial", "spriteList", "texture", "pixelSize", "premultipliedAlpha", "replacement"):
        utxt = re.sub(
            rf"\n\tpublic\s+[^\n]+\b(?:get|set)_{prop_name}\s*\([^)]*\)\s*\{{[^}}]*\}}\n",
            "\n",
            utxt,
        )

    clean_props = """
	public Material spriteMaterial
	{
		get
		{
			return null;
		}
		set
		{
		}
	}

	public bool premultipliedAlpha => false;

	public List<IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ> spriteList
	{
		get
		{
			return null;
		}
		set
		{
		}
	}

	public Texture texture => null;

	public float pixelSize
	{
		get
		{
			return 0f;
		}
		set
		{
		}
	}

	public IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII replacement
	{
		get
		{
			return null;
		}
		set
		{
		}
	}
"""
    if "\tpublic Material spriteMaterial" not in utxt:
        utxt = utxt.replace(
            "public Material IIJJJJJJIJJIIIJIIJJIJIIJJJIJIJJIIIIIJIIJJIJJJII",
            clean_props.lstrip("\n") + "\n\tpublic Material IIJJJJJJIJJIIIJIIJJIJIIJJJIJIJJIIIIIJIIJJIJJJII",
        )
    with open(ui_atlas_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(utxt)

    # Patch NGUIAtlas.cs to include the 6 obfuscated interface properties forwarding to the clean properties
    ngui_atlas_path = os.path.join(scripts_dir, "Assembly-CSharp", "NGUIAtlas.cs")
    with open(ngui_atlas_path, "r", encoding="utf-8") as f:
        ntxt = f.read()

    obf_atlas_props = """
	public Material IIJJJJJJIJJIIIJIIJJIJIIJJJIJIJJIIIIIJIIJJIJJJII
	{
		get
		{
			return spriteMaterial;
		}
		set
		{
			spriteMaterial = value;
		}
	}

	public List<IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ> JJJIIIIJIIJJJJJIIIJIIIJJIIJJIIJIJJIJIJIIIIJJJJJ
	{
		get
		{
			return spriteList;
		}
		set
		{
			spriteList = value;
		}
	}

	public Texture IIJIJIIIJJJIIIJJIIJJIJIIIIIIJJJIIJIJIJJIIIJIIIJ => texture;

	public float JJIIIIIIIIIJJIIJIIJIJIIIIJJIJJIIIIIIIJJIJIIIIII
	{
		get
		{
			return pixelSize;
		}
		set
		{
			pixelSize = value;
		}
	}

	public bool JIJJJIIJIIIJIJIJIIJIIIIJJIJIJIJIJIJIJJIJJJJIIJI => premultipliedAlpha;

	public IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII JJJJJJIJJIJJJIIJIIIIJIJJJJJJJIJIJIJIJJIJIIIJJII
	{
		get
		{
			return replacement;
		}
		set
		{
			replacement = value;
		}
	}
"""
    if "IIJJJJJJIJJIIIJIIJJIJIIJJJIJIJJIIIIIJIIJJIJJJII" not in ntxt:
        ntxt = ntxt.replace(
            "\tpublic Material spriteMaterial",
            obf_atlas_props.lstrip("\n") + "\n\tpublic Material spriteMaterial",
        )
    with open(ngui_atlas_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(ntxt)


def patch_ingui_font(scripts_dir: str) -> None:
    font_props = [
        ("JJIIJIIIJJIIIJJJIJJIIJIJJIIJJJJJJJIJIIIIIIIJJJI", "bmFont", "IJJIJJJIJJJIJJIIJJJJJJIJIIIIIIJJIJIJIIJJJJJJIIJ", True, "null"),
        ("int", "texWidth", "JIJIIIJJJJJIIJJJIIJIJJIIJIJJJIJJIJIIIIJIJIIIIII", True, "0"),
        ("int", "texHeight", "IIJIIJIJIIIJIJJIJJJJJJJIJJIIIJJIIIJJIIJJJJIJJJJ", True, "0"),
        ("bool", "hasSymbols", "IIIJJJIJJJJIIIIIJIJJIJJIJJIJIIIIIIIJIIJJIJIIJJJ", False, "false"),
        ("List<IJJIIIIJIJJJIJJJJIIIIJJJIJIJIIJJJIIIIIJJIJIJJII>", "symbols", "JIIJJJJIJJIJIJIJJJIJJJJIJJJJIJIIIIIJIIJJJIIIJJJ", True, "null"),
        ("IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII", "atlas", "JJJIIIJJJIIIIIJIJIJJIIIJIIIIIIIJIIIJIIIIIIJJJJI", True, "null"),
        ("Material", "material", "IJIIJJJJJIIIJJJJIIIJJJJJIJJIJIJJIIIJJIIJJIIIIII", True, "null"),
        ("bool", "premultipliedAlphaShader", "JJIIIJJJJIIJJIJIJJIJIIIJIJJIIJJIIJJIIJIJJIIIIIJ", False, "false"),
        ("bool", "packedFontShader", "JJJIJJIIIJIIIIIJIJJJJJJIJJIJJIJIIIJIIIJJJIJJJIJ", False, "false"),
        ("Texture2D", "texture", "IIJIJIIIJJJIIIJJIIJJIJIIIIIIJJJIIJIJIJJIIIJIIIJ", False, "null"),
        ("Rect", "uvRect", "IIIIIIIIIJIIIJJJIIJJJJIIIJIIJIIIIJJJJIJIIJJIIJJ", True, "default"),
        ("string", "spriteName", "JIJJIIIIIIIJIIJIJJIJIJJIIJJIIIIIJIJJIJJJIIIJIJJ", True, "null"),
        ("bool", "isValid", "IIIJIJJJIIJIJIJJJJJJJJJIJJIJIJIJIIIIIIJJJJJJIII", False, "false"),
        ("int", "defaultSize", "JIJIIIJJJIJJIJJIIIJIIJIIJJJJJJIJIIJJJIJIJJIIJII", True, "0"),
        ("IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ", "sprite", "JIIIJIIJJIIIJIJJJJJIJIIJIJIJJIIJIJJJIIJJJJJJJIJ", False, "null"),
        ("JJIJJJJJIIJIIIIJIIJJJIIIIIJIIIJIJIJIIJJJIJJJIJI", "replacement", "JJJJJJIJJIJJJIIJIIIIJIJJJJJJJIJIJIJIJJIJIIIJJII", True, "null"),
        ("bool", "isDynamic", "IIJJJIIJJJJJIIJIJJJIIJIIIJJJIJJJJJIIJIJIJJIJIJI", False, "false"),
        ("Font", "dynamicFont", "JJJIJJJJJIJJJIIIJJJIIIIJIIIIIJIIJJIIJJJIIJIIJJI", True, "null"),
        ("FontStyle", "dynamicFontStyle", "IIJJJJJJIIIIIIIIJJIJIJIJIJJIIJJJIIJJIJIJIJIJIII", True, "FontStyle.Normal"),
    ]

    iface_path = os.path.join(scripts_dir, "Assembly-CSharp", "JJIJJJJJIIJIIIIJIIJJJIIIIIJIIIJIJIJIIJJJIJJJIJI.cs")
    with open(iface_path, "r", encoding="utf-8") as f:
        itxt = f.read()

    for ptype, pname, _, has_set, _ in font_props:
        if has_set:
            itxt = re.sub(
                rf"\t{re.escape(ptype)}\s+get_{pname}\(\);\s*\n\s*void\s+set_{pname}\([^)]+\);",
                f"\t{ptype} {pname} {{ get; set; }}",
                itxt,
            )
        else:
            itxt = re.sub(
                rf"\t{re.escape(ptype)}\s+get_{pname}\(\);",
                f"\t{ptype} {pname} {{ get; }}",
                itxt,
            )
    with open(iface_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(itxt)

    # Patch UIFont.cs
    uifont_path = os.path.join(scripts_dir, "Assembly-CSharp", "UIFont.cs")
    with open(uifont_path, "r", encoding="utf-8") as f:
        utxt = f.read()

    for ptype, pname, _, has_set, _ in font_props:
        utxt = utxt.replace(f"return get_{pname}();", f"return {pname};")
        utxt = utxt.replace(f"=> get_{pname}();", f"=> {pname};")
        if has_set:
            utxt = utxt.replace(f"set_{pname}(value);", f"{pname} = value;")
        utxt = re.sub(
            rf"\n\tpublic\s+[^\n]+\b(?:get|set)_{pname}\s*\([^)]*\)\s*\{{[^}}]*\}}\n",
            "\n",
            utxt,
        )

    clean_font_props = []
    for ptype, pname, _, has_set, defval in font_props:
        if has_set:
            clean_font_props.append(
                f"\tpublic {ptype} {pname}\n\t{{\n\t\tget\n\t\t{{\n\t\t\treturn {defval};\n\t\t}}\n\t\tset\n\t\t{{\n\t\t}}\n\t}}\n"
            )
        else:
            clean_font_props.append(f"\tpublic {ptype} {pname} => {defval};\n")

    if "\tpublic JJIIJIIIJJIIIJJJIJJIIJIJJIIJJJJJJJIJIIIIIIIJJJI bmFont" not in utxt:
        utxt = utxt.replace(
            "\tpublic JJIIJIIIJJIIIJJJIJJIIJIJJIIJJJJJJJIJIIIIIIIJJJI IJJIJJJIJJJIJJIIJJJJJJIJIIIIIIJJIJIJIIJJJJJJIIJ",
            "\n".join(clean_font_props)
            + "\n\tpublic JJIIJIIIJJIIIJJJIJJIIJIJJIIJJJJJJJIJIIIIIIIJJJI IJJIJJJIJJJIJJIIJJJJJJIJIIIIIIJJIJIJIIJJJJJJIIJ",
        )
    with open(uifont_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(utxt)

    # Patch NGUIFont.cs
    nguifont_path = os.path.join(scripts_dir, "Assembly-CSharp", "NGUIFont.cs")
    with open(nguifont_path, "r", encoding="utf-8") as f:
        ntxt = f.read()

    obf_font_props = []
    for ptype, pname, obfname, has_set, _ in font_props:
        if has_set:
            obf_font_props.append(
                f"\tpublic {ptype} {obfname}\n\t{{\n\t\tget\n\t\t{{\n\t\t\treturn {pname};\n\t\t}}\n\t\tset\n\t\t{{\n\t\t\t{pname} = value;\n\t\t}}\n\t}}\n"
            )
        else:
            obf_font_props.append(f"\tpublic {ptype} {obfname} => {pname};\n")
    obf_font_props.append("\t[Obsolete]\n\tpublic bool JIJJJIIJIIIJIJIJIIJIIIIJJIJIJIJIJIJIJJIJJJJIIJI => premultipliedAlpha;\n")
    obf_font_props.append(
        "\t[Obsolete]\n\tpublic int IJJJJJJIJIIIJJIIIJIJIJJIJIIIJJIJJJIIJJJJJIIJIII\n\t{\n\t\tget\n\t\t{\n\t\t\treturn size;\n\t\t}\n\t\tset\n\t\t{\n\t\t\tsize = value;\n\t\t}\n\t}\n"
    )

    if "IJJIJJJIJJJIJJIIJJJJJJIJIIIIIIJJIJIJIIJJJJJJIIJ" not in ntxt:
        ntxt = ntxt.replace(
            "\tpublic JJIIJIIIJJIIIJJJIJJIIJIJJIIJJJJJJJIJIIIIIIIJJJI bmFont",
            "\n".join(obf_font_props)
            + "\n\tpublic JJIIJIIIJJIIIJJJIJJIIJIJJIIJJJJJJJIJIIIIIIIJJJI bmFont",
        )
    with open(nguifont_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(ntxt)


def patch_collection_classes(scripts_dir: str) -> None:
    # 1. JJJJIJJIJIJIJIIJIIIJJJJIIIIJJJIJIIIIJIIJJIIIIJJ.cs
    p1 = os.path.join(scripts_dir, "Assembly-CSharp", "JJJJIJJIJIJIJIIJIIIJJJJIIIIJJJIJIIIIJIIJJIIIIJJ.cs")
    with open(p1, "r", encoding="utf-8") as f:
        t1 = f.read()
    t1 = t1.replace(
        "IJIJIJIJJJIIIJJIJJJJIJIIIJIIIIIIIIJIIJJJJIJIJII(JJIIIJJJJIJIJJIJIJJJJJIJJJIIJIJJJIIIJJIJIJJIIII, value);",
        "IJIJIJIJJJIIIJJIJJJJIJIIIJIIIIIIIIJIIJJJJIJIJII(JJIIIJJJJIJIJJIJIJJJJJIJJJIIJIJJJIIIJJIJIJJIIII, JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI);",
    )
    with open(p1, "w", encoding="utf-8", newline="\n") as f:
        f.write(t1)

    # 2. IJIJJJJIJIJIIIIIIIJJIJIJJIJJJJJIIIJIIIIJJJIJJJJ.cs (IList, ICollection, IEnumerable)
    p2 = os.path.join(scripts_dir, "Assembly-CSharp", "IJIJJJJIJIJIIIIIIIJJIJIJJIJJJJJIIIJIIIIJJJIJJJJ.cs")
    with open(p2, "r", encoding="utf-8") as f:
        t2 = f.read()
    t2 = t2.replace("=> get_Count();", "=> Count;")
    t2 = t2.replace("=> get_IsReadOnly();", "=> IsReadOnly;")
    t2 = t2.replace("=> get_IsFixedSize();", "=> IsFixedSize;")
    t2 = t2.replace("=> get_IsSynchronized();", "=> IsSynchronized;")
    t2 = t2.replace("=> get_SyncRoot();", "=> SyncRoot;")
    t2 = t2.replace(
        "return get_Item(IIJJIJJJIJIIJIIJJJIJJJIIJJIIJJJIIJJIJJIJIJJIIJJ);",
        "return this[IIJJIJJJIJIIJIIJJJIJJJIIJJIIJJJIIJJIJJIJIJJIIJJ];",
    )
    t2 = t2.replace(
        "set_Item(IIJJIJJJIJIIJIIJJJIJJJIIJJIIJJJIIJJIJJIJIJJIIJJ, value);",
        "this[IIJJIJJJIJIIJIIJJJIJJJIIJJIIJJJIIJJIJJIJIJJIIJJ] = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI;",
    )
    for mname in ("SyncRoot", "Item", "IsReadOnly", "Count", "IsFixedSize", "IsSynchronized"):
        t2 = re.sub(
            rf"\n\tpublic\s+[^\n]+\b(?:get|set)_{mname}\s*\([^)]*\)\s*\{{[^}}]*\}}\n",
            "\n",
            t2,
        )
    ilist_props = """
	public int Count => 0;

	public bool IsReadOnly => false;

	public bool IsFixedSize => false;

	public bool IsSynchronized => false;

	public object SyncRoot => null;

	public object this[int IIJJIJJJIJIIJIIJJJIJJJIIJJIIJJJIIJJIJJIJIJJIIJJ]
	{
		get
		{
			return null;
		}
		set
		{
		}
	}
"""
    if "\tpublic int Count => 0;" not in t2:
        t2 = t2.replace(
            "\tpublic int JJIJJJIIJIJIJIIIJJJIIIJIJJJJIIJIIJJJIJJIJIJJIII => Count;",
            ilist_props.lstrip("\n") + "\n\tpublic int JJIJJJIIJIJIJIIIJJJIIIJIJJJJIIJIIJJJIJJIJIJJIII => Count;",
        )
    with open(p2, "w", encoding="utf-8", newline="\n") as f:
        f.write(t2)

    # 3. JIJJIIIIIIJJIJJJJJJIIIJJIJJJJJIJJJJIJIIJJJJIIIJ.cs (IDictionary<TKey, TValue>, INotifyPropertyChanged)
    p3 = os.path.join(scripts_dir, "Assembly-CSharp", "JIJJIIIIIIJJIJJJJJJIIIJJIJJJJJIJJJJIJIIJJJJIIIJ.cs")
    with open(p3, "r", encoding="utf-8") as f:
        t3 = f.read()
    t3 = t3.replace("=> get_Keys();", "=> Keys;")
    t3 = t3.replace("=> get_Values();", "=> Values;")
    t3 = t3.replace("=> get_Count();", "=> Count;")
    t3 = t3.replace("=> get_IsReadOnly();", "=> IsReadOnly;")
    t3 = t3.replace(
        "return get_Item(IIIJIJJJIIIIJJIIJJJIJJJIIIJJIJIIJJIJIJJJIIJIJIJ);",
        "return this[IIIJIJJJIIIIJJIIJJJIJJJIIIJJIJIIJJIJIJJJIIJIJIJ];",
    )
    t3 = t3.replace(
        "set_Item(IIIJIJJJIIIIJJIIJJJIJJJIIIJJIJIIJJIJIJJJIIJIJIJ, value);",
        "this[IIIJIJJJIIIIJJIIJJJIJJJIIIJJIJIIJJIJIJJJIIJIJIJ] = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI;",
    )
    t3 = t3.replace("add_PropertyChanged(value);", "PropertyChanged += value;")
    t3 = t3.replace("remove_PropertyChanged(value);", "PropertyChanged -= value;")
    for mname in ("Keys", "Values", "Count", "IsReadOnly", "Item", "PropertyChanged"):
        t3 = re.sub(
            rf"\n\tpublic\s+[^\n]+\b(?:get|set|add|remove)_{mname}\s*\([^)]*\)\s*\{{[^}}]*\}}\n",
            "\n",
            t3,
        )
    idict_props = """
	public ICollection<TKey> Keys => null;

	public ICollection<TValue> Values => null;

	public int Count => 0;

	public bool IsReadOnly => false;

	public TValue this[TKey IIIJIJJJIIIIJJIIJJJIJJJIIIJJIJIIJJIJIJJJIIJIJIJ]
	{
		get
		{
			return default;
		}
		set
		{
		}
	}

	public event PropertyChangedEventHandler PropertyChanged
	{
		add
		{
		}
		remove
		{
		}
	}
"""
    if "\tpublic ICollection<TKey> Keys => null;" not in t3:
        t3 = t3.replace(
            "\tpublic ICollection<TKey> IIJIIIIJJIJIIJIIJJIJJJJJJIJIJIJJJIIIJIIJIIIJJJI => Keys;",
            idict_props.lstrip("\n") + "\n\tpublic ICollection<TKey> IIJIIIIJJIJIIJIIJJIJJJJJJIJIJIJJJIIIJIIJIIIJJJI => Keys;",
        )
    with open(p3, "w", encoding="utf-8", newline="\n") as f:
        f.write(t3)

    for www_file in (
        "Logo.cs",
        "IJIIJJIIIJIIJJJJJJIJIIJIJJIJIIJJIIJJJJJIIJJIIJJ.cs",
        "UIFontControl.cs",
        "NTPManager.cs",
    ):
        wp = os.path.join(scripts_dir, "Assembly-CSharp", www_file)
        if os.path.exists(wp):
            with open(wp, "r", encoding="utf-8") as f:
                wtxt = f.read()
            if "#pragma warning disable 0618" not in wtxt:
                wtxt = "#pragma warning disable 0618\n" + wtxt
                with open(wp, "w", encoding="utf-8", newline="\n") as f:
                    f.write(wtxt)


def patch_uiwidget(scripts_dir: str) -> None:
    p = os.path.join(scripts_dir, "Assembly-CSharp", "UIWidget.cs")
    with open(p, "r", encoding="utf-8") as f:
        txt = f.read()

    old_block = """\tpublic override float alpha
\t{
\t\tget
\t\t{
\t\t\treturn IJJJJIIJJIJJJJIIIIIJJJIIJJJJJJJIIJJJJIJJJJIIJIJ();
\t\t}
\t\tset
\t\t{
\t\t\tIIIJIIJIIJJJJIIIJIJJIJJJJJIIIIIJIJIJJIIIJJJIJJJ(value);
\t\t}
\t}"""

    new_block = """\tpublic override float IJIIJJIIJIJJJIJIJJJIIJJIIIJJJIIIJJJJIIJJIIJIIIJ
\t{
\t\tget
\t\t{
\t\t\treturn IJJJJIIJJIJJJJIIIIIJJJIIJJJJJJJIIJJJJIJJJJIIJIJ();
\t\t}
\t\tset
\t\t{
\t\t\tIIIJIIJIIJJJJIIIJIJJIJJJJJIIIIIJIJIJJIIIJJJIJJJ(value);
\t\t}
\t}

\tpublic float alpha
\t{
\t\tget
\t\t{
\t\t\treturn IJJJJIIJJIJJJJIIIIIJJJIIJJJJJJJIIJJJJIJJJJIIJIJ();
\t\t}
\t\tset
\t\t{
\t\t\tIIIJIIJIIJJJJIIIJIJJIJJJJJIIIIIJIJIJJIIIJJJIJJJ(value);
\t\t}
\t}"""

    if "public override float IJIIJJIIJIJJJIJIJJJIIJJIIIJJJIIIJJJJIIJJIIJIIIJ" not in txt:
        assert old_block in txt, "Expected UIWidget.alpha block not found"
        txt = txt.replace(old_block, new_block, 1)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)


def patch_all_scripts(scripts_dir: str) -> dict:
    stats = {
        "special_name_removed": 0,
        "debugger_hidden_removed": 0,
        "preserve_sig_replaced": 0,
        "implicit_ops_restored": 0,
        "files_modified": 0,
    }

    for cs_path in sorted(glob.glob(os.path.join(scripts_dir, "**", "*.cs"), recursive=True)):
        with open(cs_path, "r", encoding="utf-8") as f:
            orig = f.read()
        txt = orig

        # 1. Strip [SpecialName]
        sn_matches = len(re.findall(r"^\s*\[SpecialName\]\s*\n", txt, re.M))
        if sn_matches:
            txt = re.sub(r"^\s*\[SpecialName\]\s*\n", "", txt, flags=re.M)
            stats["special_name_removed"] += sn_matches

        # 2. Strip [property: DebuggerHidden]
        dh_matches = len(re.findall(r"^\s*\[property:\s*DebuggerHidden\]\s*\n", txt, re.M))
        if dh_matches:
            txt = re.sub(r"^\s*\[property:\s*DebuggerHidden\]\s*\n", "", txt, flags=re.M)
            stats["debugger_hidden_removed"] += dh_matches

        # 3. Replace [PreserveSig] on extern P/Invoke methods with [DllImport(...)]
        if "[PreserveSig]" in txt:
            rel = os.path.relpath(cs_path, scripts_dir)
            if rel.endswith("GoogleSignInImpl.cs"):
                dll_const = "DllName"
            else:
                dll_const = "IJIIIJIIJJJIJIIIJIJJJIIIIJJJJJJIJIJJJJIJJIJIJIJ"
            ps_matches = txt.count("[PreserveSig]")
            txt = txt.replace("[PreserveSig]", f"[DllImport({dll_const})]")
            stats["preserve_sig_replaced"] += ps_matches

        # 4. Restore implicit operators from obfuscated op_Implicit (IJIJJIJJIJIIIIIJJJJIJJJIIIJJIIIIIIIJIJJJJIIIIIJ)
        op_pattern = r"public\s+static\s+([\w\.<>\[\]]+)\s+IJIJJIJJIJIIIIIJJJJIJJJIIIJJIIIIIIIJIJJJJIIIIIJ\s*\("
        op_matches = len(re.findall(op_pattern, txt))
        if op_matches:
            txt = re.sub(op_pattern, r"public static implicit operator \1(", txt)
            stats["implicit_ops_restored"] += op_matches

        if txt != orig:
            with open(cs_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(txt)
            stats["files_modified"] += 1

    return stats


def install_editor_tools(client_dir: str, repo_root: str) -> None:
    editor_dir = os.path.join(client_dir, "Assets", "Editor")
    os.makedirs(editor_dir, exist_ok=True)
    editor_dir_meta = editor_dir + ".meta"
    if not os.path.exists(editor_dir_meta):
        guid = uuid.uuid5(uuid.NAMESPACE_URL, "BS-decomp/6.5.1/Assets/Editor").hex
        with open(editor_dir_meta, "w", encoding="utf-8", newline="\n") as f:
            f.write(
                f"fileFormatVersion: 2\n"
                f"guid: {guid}\n"
                f"folderAsset: yes\n"
                f"DefaultImporter:\n"
                f"  externalObjects: {{}}\n"
                f"  userData: \n"
                f"  assetBundleName: \n"
                f"  assetBundleVariant: \n"
            )

    src_cs = os.path.join(repo_root, "tools", "unity-editor", "BlockStrikeGeometryRecovery.cs")
    dst_cs = os.path.join(editor_dir, "BlockStrikeGeometryRecovery.cs")
    shutil.copyfile(src_cs, dst_cs)
    dst_meta = dst_cs + ".meta"
    if not os.path.exists(dst_meta):
        guid = uuid.uuid5(uuid.NAMESPACE_URL, "BS-decomp/6.5.1/Assets/Editor/BlockStrikeGeometryRecovery.cs").hex
        with open(dst_meta, "w", encoding="utf-8", newline="\n") as f:
            f.write(
                f"fileFormatVersion: 2\n"
                f"guid: {guid}\n"
                f"MonoImporter:\n"
                f"  externalObjects: {{}}\n"
                f"  serializedVersion: 2\n"
                f"  defaultReferences: []\n"
                f"  executionOrder: 0\n"
                f"  icon: {{instanceID: 0}}\n"
                f"  userData: \n"
                f"  assetBundleName: \n"
                f"  assetBundleVariant: \n"
            )


def ensure_missing_meta_files(client_dir: str) -> tuple[int, int]:
    assets_dir = os.path.join(client_dir, "Assets")
    created_dirs = 0
    created_cs = 0
    for dirpath, _, filenames in os.walk(assets_dir):
        if dirpath != assets_dir:
            dir_meta = dirpath + ".meta"
            if not os.path.exists(dir_meta):
                rel = os.path.relpath(dirpath, client_dir).replace("\\", "/")
                guid = uuid.uuid5(uuid.NAMESPACE_URL, f"BS-decomp/6.5.1/{rel}").hex
                with open(dir_meta, "w", encoding="utf-8", newline="\n") as f:
                    f.write(
                        f"fileFormatVersion: 2\n"
                        f"guid: {guid}\n"
                        f"folderAsset: yes\n"
                        f"DefaultImporter:\n"
                        f"  externalObjects: {{}}\n"
                        f"  userData: \n"
                        f"  assetBundleName: \n"
                        f"  assetBundleVariant: \n"
                    )
                created_dirs += 1
        for fn in filenames:
            if fn.endswith(".meta"):
                continue
            p = os.path.join(dirpath, fn)
            meta_p = p + ".meta"
            if not os.path.exists(meta_p) and fn.endswith(".cs"):
                rel = os.path.relpath(p, client_dir).replace("\\", "/")
                guid = uuid.uuid5(uuid.NAMESPACE_URL, f"BS-decomp/6.5.1/{rel}").hex
                with open(meta_p, "w", encoding="utf-8", newline="\n") as f:
                    f.write(
                        f"fileFormatVersion: 2\n"
                        f"guid: {guid}\n"
                        f"MonoImporter:\n"
                        f"  externalObjects: {{}}\n"
                        f"  serializedVersion: 2\n"
                        f"  defaultReferences: []\n"
                        f"  executionOrder: 0\n"
                        f"  icon: {{instanceID: 0}}\n"
                        f"  userData: \n"
                        f"  assetBundleName: \n"
                        f"  assetBundleVariant: \n"
                    )
                created_cs += 1
    return created_dirs, created_cs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-dir", required=True, help="Path to exported Unity project directory")
    args = parser.parse_args()

    client_dir = os.path.abspath(args.client_dir)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(client_dir, "Assets", "Scripts")

    patch_project_settings(client_dir)
    removed_plugins = patch_plugins(client_dir)
    removed_asm_info = remove_assembly_info(client_dir)
    patch_ingui_atlas(scripts_dir)
    patch_ingui_font(scripts_dir)
    patch_collection_classes(scripts_dir)
    patch_uiwidget(scripts_dir)
    stats = patch_all_scripts(scripts_dir)
    install_editor_tools(client_dir, repo_root)
    created_dirs, created_cs = ensure_missing_meta_files(client_dir)

    print(
        f"Patched Unity 2021.3.45f2 project at {client_dir}: "
        f"removed_plugins={removed_plugins}, removed_assembly_info={removed_asm_info}, "
        f"created_dir_metas={created_dirs}, created_cs_metas={created_cs}, "
        f"stats={stats}"
    )


if __name__ == "__main__":
    main()
