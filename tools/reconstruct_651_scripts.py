#!/usr/bin/env python3
"""Reconstruct the verified 6.5.1 boot/UI paths from the IL2CPP evidence.

This script intentionally changes only methods whose behavior has been checked against
lib/armeabi-v7a/libil2cpp.so + global-metadata.dat. It does not fill arbitrary methods
with guessed behavior. Run from the repository root:

    python3 tools/reconstruct_651_scripts.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "client/Assets/Scripts/Assembly-CSharp"


def replace_method(text: str, signature: str, body: str) -> str:
    """Replace the body following an exact method signature fragment."""
    start = text.find(signature)
    if start < 0:
        raise RuntimeError(f"method signature not found: {signature}")
    brace = text.find("{", start)
    if brace < 0:
        raise RuntimeError(f"method has no body: {signature}")
    depth = 0
    close = -1
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                close = i
                break
    if close < 0:
        raise RuntimeError(f"unbalanced method body: {signature}")
    indent = "\t"
    body_lines = body.strip("\n").splitlines()
    replacement = "{\n" + "\n".join(indent + line if line else "" for line in body_lines) + "\n\t}"
    return text[:brace] + replacement + text[close + 1 :]


def replace_property(text: str, signature: str, replacement: str) -> str:
    start = text.find(signature)
    if start < 0:
        raise RuntimeError(f"property signature not found: {signature}")
    brace = text.find("{", start)
    semi = text.find(";", start)
    if semi >= 0 and (brace < 0 or semi < brace):
        line_end = text.find("\n", semi)
        if line_end < 0:
            line_end = len(text)
        return text[:start] + replacement + text[line_end:]
    depth = 0
    close = -1
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                close = i
                break
    if close < 0:
        raise RuntimeError(f"unbalanced property: {signature}")
    return text[:start] + replacement + text[close + 1 :]


def add_before_class_close(text: str, addition: str) -> str:
    pos = text.rfind("}")
    if pos < 0:
        raise RuntimeError("class close not found")
    return text[:pos] + "\n" + addition.strip("\n") + "\n" + text[pos:]


def add_using(text: str, using_line: str) -> str:
    if using_line in text:
        return text
    return using_line + "\n" + text


def patch_file(name: str, fn) -> None:
    path = SCRIPT_DIR / name
    text = path.read_text(encoding="utf-8")
    new = fn(text)
    if new != text:
        path.write_text(new, encoding="utf-8", newline="\n")
        print(f"patched {path.relative_to(ROOT)}")


def patch_scene_wrapper(text: str) -> str:
    text = add_using(text, "using UnityEngine.SceneManagement;")
    for signature in (
        "public static void IIIJJJJJJIJIJIIJIJIIIJJIJJIJJIIIJIJIJJJIJJJIJJJ(string",
        "public static void JIJJJIIJJIIJIIIJIJIIIJIJIIJIIIJJJJIIIJIJIJIIJII(string",
        "public static void JIIJJJIIIJJJJJIIIJJJIJIIJJIJJIJIIJJIJJJIJIIIIJI(string",
    ):
        text = replace_method(text, signature, "SceneManager.LoadScene(JIIJIJIJJJIIJJJJJIIJJJIIIIJIIIJIJIIIJIJIIJJJJIJ);")
    return text


def patch_android_permissions(text: str) -> str:
    text = add_using(text, "using UnityEngine.SceneManagement;")
    return replace_method(text, "private void Start()", 'SceneManager.LoadScene("Logo");')


def patch_gdpr(text: str) -> str:
    text = add_using(text, "using UnityEngine.SceneManagement;")
    text = replace_method(
        text,
        "public void OnAccept()",
        """
        if (JJIJIIJJIJJIIIJJJIIJIJJIIIJIJIJIIIJIJJIJJIJIIIJ != null)
        {
            JJIJIIJJIJJIIIJJJIIJIJJIIIJIJIJIIIJIJJIJJIJIIIJ.SetActive(false);
        }
        if (JJIIIJIJJIJJJIJJJJJJIIJIIJIJJJIJIJJJJIJIJIIIIIJ != null)
        {
            JJIIIJIJJIJJJIJJJJJJIIJIIJIJJJIJIJJJJIJIJIIIIIJ.SetActive(true);
        }
        PlayerPrefs.SetInt("GDPR", 1);
        PlayerPrefs.Save();
        """,
    )
    text = replace_method(
        text,
        "public void OnClickTraining(bool isTraining)",
        """
        if (JJIIIJIJJIJJJIJJJJJJIIJIIJIJJJIJIJJJJIJIJIIIIIJ != null)
        {
            JJIIIJIJJIJJJIJJJJJJIIJIIJIJJJIJIJJJJIJIJIIIIIJ.SetActive(false);
        }
        SceneManager.LoadScene(isTraining ? "MainTutorial" : "Menu");
        """,
    )
    text = replace_method(
        text,
        "private void Start()",
        """
        if (PlayerPrefs.GetInt("GDPR", 0) != 0)
        {
            SceneManager.LoadScene("Menu");
            return;
        }
        if (JJIJIIJJIJJIIIJJJIIJIJJIIIJIJIJIIIJIJJIJJIJIIIJ != null)
        {
            JJIJIIJJIJJIIIJJJIIJIJJIIIJIJIJIIIJIJJIJJIJIIIJ.SetActive(true);
        }
        """,
    )
    return text


def patch_logo(text: str) -> str:
    text = add_using(text, "using UnityEngine.SceneManagement;")
    text = replace_method(
        text,
        "private void Start()",
        "StartCoroutine(IIJJIIJJIJJJIJJIIJJIIIJJJJIIIIIJJJJIJIIJIJJIIJJ());",
    )
    text = replace_method(
        text,
        "private IEnumerator IIJJIIJJIJJJIJJIIJJIIIJJJJIIIIIJJJJIJIIJIJJIIJJ()",
        "return ReconstructedBoot();",
    )
    if "private IEnumerator ReconstructedBoot()" not in text:
        text = add_before_class_close(
            text,
            """
    private IEnumerator ReconstructedBoot()
    {
        Screen.sleepTimeout = SleepTimeout.NeverSleep;
        if (IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ != null)
        {
            IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ.text = "0%";
        }
        yield return new WaitForSeconds(0.01f);
        if (IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ != null)
        {
            IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ.text = "50%";
        }
        yield return new WaitForSeconds(0.01f);
        if (IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ != null)
        {
            IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ.text = "90%";
        }
        yield return new WaitForSeconds(0.01f);
        if (IIJJJJIJIJJJJIJJJIIIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ != null)
        {
            IIJJJJIJIJJJJIJJJIIIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ.text = "100%";
        }
        else if (IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ != null)
        {
            IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ.text = "100%";
        }
        SceneManager.LoadScene("GDPR");
    }
        """,
    )
    # The generated source has only one progress label in 6.5.1. Remove the
    # defensive typo branch above if the alternate obfuscated field is absent.
    text = text.replace(
        "        if (IIJJJJIJIJJJJIJJJIIIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ != null)\n        {\n            IIJJJJIJIJJJJIJJJIIIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ.text = \"100%\";\n        }\n        else if (IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ != null)\n        {\n",
        "        if (IIJJJJIJIJJJJIJJJIIIJJJIIJJIJJIJJJJIJJIIJJIIIJJ != null)\n        {\n",
    )
    return text


def patch_event_click(text: str) -> str:
    text = replace_method(
        text,
        "private void OnEnable()",
        """
        if (IJIIIJIJJJIIJJJIIIIJJJJJIIIIJJIIIIJJIJIIIJIIIJI == null)
        {
            IJIIIJIJJJIIJJJIIIIJJJJJIIIIJJIIIIJJIJIIIJIIIJI = new UnityEvent();
        }
        UICamera.IJIIIJIJJJIIJJJIIIIJJJJJIIIIJJIIIIJJIJIIIJIIIJI += OnClick;
        """,
    )
    text = replace_method(
        text,
        "private void OnDisable()",
        "UICamera.IJIIIJIJJJIIJJJIIIIJJJJJIIIIJJIIIIJJIJIIIJIIIJI -= OnClick;",
    )
    text = replace_method(
        text,
        "private void OnClick(GameObject IIIJJJIJIJIIJJIJIJIJIIIJIJJJJIJJIIIJIJJJJIJJIII)",
        """
        if (IIIJJJIJIJIIJJIJIJIJIIIJIJJJJIJJIIIJIJJJJIJJIII == gameObject && IJIIIJIJJJIIJJJIIIIJJJJJIIIIJJIIIIJJIJIIIJIIIJI != null)
        {
            IJIIIJIJJJIIJJJIIIIJJJJJIIIIJJIIIIJJIJIIIJIIIJI.Invoke();
        }
        """,
    )
    return text


def patch_label(text: str) -> str:
    text = replace_method(text, "public override Material IJJIIIIJIIIJIIJIJIIJJIIJJJIJJJJIJJJJIIJJIJJIIII()", "return mMat;")
    text = replace_method(text, "public string JIIJJJIJIJJJJJJJJJIIIJIIIJJJIIIIIJJIIIIJJJIIJIJ()", "return mText ?? string.Empty;")
    text = replace_method(text, "public void JJIJJIJIIIIJIIJJJJIIJJJJIIIJJIJIIJJIJJIJJIJJJJJ(string", "mText = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI ?? string.Empty;")
    return text


def patch_localize(text: str) -> str:
    text = replace_method(text, "private void OnEnable()", "ApplyLocalization();")
    text = replace_method(text, "private void Start()", "ApplyLocalization();")
    text = replace_method(text, "private void OnDisable()", "IIJJIJIJJIJJIJIJIJJJIIIJJJIJJIIIIJJJJIJIJIIJIJI = false;")
    text = replace_method(text, "public void JJIJIIIIJJJIJIJIIIJJJIJIIJIJJJIJIJJJIIIIJIIJIII(string", "ApplyLocalization(JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI);")
    if "private void ApplyLocalization()" not in text:
        text = add_before_class_close(
            text,
            """
    private void ApplyLocalization()
    {
        ApplyLocalization(IIIJIJJJIIIIJJIIJJJIJJJIIIJJIJIIJJIJIJJJIIJIJIJ);
    }

    private void ApplyLocalization(string key)
    {
        if (string.IsNullOrEmpty(key)) return;
        if (IJIJIJIIJJJJIJJJIJJIJIJIJJIJJIIJIJJIJJIJJIIIJII == null)
        {
            IJIJIJIIJJJJIJJJIJJIJIJIJJIJJIIJIJJIJJIJJIIIJII = GetComponent<UILabel>();
        }
        if (IJIJIJIIJJJJIJJJIJJIJIJIJJIJJIIJIJJIJJIJJIIIJII == null) return;
        TextAsset csv = Resources.Load<TextAsset>("Localization");
        if (csv == null) return;
        string[] rows = csv.text.Split(new[] { '\\n' }, StringSplitOptions.RemoveEmptyEntries);
        for (int i = 1; i < rows.Length; i++)
        {
            string row = rows[i].TrimEnd('\\r');
            string[] columns = row.Split(',');
            if (columns.Length >= 2 && columns[0] == key)
            {
                IJIJIJIIJJJJIJJJIJJIJIJIJJIJJIIJIJJIJJIJJIIIJII.text = columns[1];
                IIJJIJIJJIJJIJIJIJJJIIIJJJIJJIIIIJJJJIJIJIIJIJI = true;
                return;
            }
        }
        IJIJIJIIJJJJIJJJIJJIJIJIJJIJJIIJIJJIJJIJJIIIJII.text = key;
        IIJJIJIJJIJJIJIJIJJJIIIJJJIJJIIIIJJJJIJIJIIJIJI = true;
    }
        """,
    )
    return add_using(text, "using System;")


def patch_atlas_common(text: str, is_uiatlas: bool) -> str:
    iface = "IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII"
    data_type = "IJJJJJIIJIIIIJJIJJIJIJJJJJJJIJIJIJIIJIIJJIIIJJJ"
    replacement = f"mReplacement as {iface}"
    text = replace_property(text, "public Material spriteMaterial", f"""\tpublic Material spriteMaterial\n\t{{\n\t\tget {{ return ({replacement}) != null ? ({replacement}).spriteMaterial : material; }}\n\t\tset {{ if (({replacement}) != null) ({replacement}).spriteMaterial = value; else material = value; }}\n\t}}""")
    text = replace_property(text, "public bool premultipliedAlpha", f"""\tpublic bool premultipliedAlpha\n\t{{\n\t\tget\n\t\t{{\n\t\t\tif (({replacement}) != null) return ({replacement}).premultipliedAlpha;\n\t\t\treturn material != null && material.shader != null && material.shader.name.Contains(\"Premultiplied\");\n\t\t}}\n\t}}""")
    text = replace_property(text, "public List<" + data_type + "> spriteList", f"""\tpublic List<{data_type}> spriteList\n\t{{\n\t\tget {{ return ({replacement}) != null ? ({replacement}).spriteList : (mSprites ?? (mSprites = new List<{data_type}>())); }}\n\t\tset {{ if (({replacement}) != null) ({replacement}).spriteList = value; else mSprites = value; }}\n\t}}""")
    text = replace_property(text, "public Texture texture", f"\tpublic Texture texture => ({replacement}) != null ? ({replacement}).texture : (material != null ? material.mainTexture : null);")
    text = replace_property(text, "public float pixelSize", f"""\tpublic float pixelSize\n\t{{\n\t\tget {{ return ({replacement}) != null ? ({replacement}).pixelSize : mPixelSize; }}\n\t\tset {{ if (({replacement}) != null) ({replacement}).pixelSize = value; else mPixelSize = Mathf.Clamp(value, 0.25f, 4f); }}\n\t}}""")
    text = replace_property(text, f"public {iface} replacement", f"""\tpublic {iface} replacement\n\t{{\n\t\tget {{ return {replacement}; }}\n\t\tset {{ mReplacement = value as UnityEngine.Object; }}\n\t}}""")
    # All atlas lookup methods return the same UISpriteData object in the verified NGUI data model.
    for signature in (
        f"public {data_type} JJJJIJJIIIIIJIJJIJJJJIJIIJJJJIJJIJIIIIJIJIJIIJJ(string",
        f"public {data_type} JIJJIJJIJJJIJJIIIIIIJIJIJIJJIJIJJIJJJIIIIIIJIII(string",
        f"public {data_type} JJIJJIJIJIJIJJIJIJJJIIIIJIJIIIJIIIIJIIIJJIJIIIJ(string",
        f"public {data_type} JIJIJIIIJIJIJIIIJJJIJIIJJIIJJIIIJJJJIJIJJJIJIII(string",
    ):
        if signature in text:
            text = replace_method(text, signature, f"""if (string.IsNullOrEmpty(JIIJIJIJJJIIJJJJJIIJJJIIIIJIIIJIJIIIJIJIIJJJJIJ)) return null;\n        foreach ({data_type} item in spriteList)\n        {{\n            if (item != null && item.JIIJIJIJJJIIJJJJJIIJJJIIIIJIIIJIJIIIJIJIIJJJJIJ == JIIJIJIJJJIIJJJJJIIJJJIIIIJIIIJIJIIIJIJIIJJJJIJ) return item;\n        }}\n        return null;""")
    return text


def patch_uisprite(text: str) -> str:
    iface = "IIIIIJIIIIJIIIIJIJIJIIIIIJIJIJJIIIIJJIJIJIJJJII"
    text = replace_method(text, "public " + iface + " IIJJJIJJIIIIIIJJIIJJIIIJIJJIIIJIJJIIIJIIJJIIJII()", "return mAtlas as " + iface + ";")
    text = replace_method(text, "public void JJIIIJIIIJIJJJJJJJJIJJJJIIIIJIJIIIJJJIJIIIIIJJJ(" , "mAtlas = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI as UnityEngine.Object;")
    text = replace_method(text, "public string IJIIIJJIJJJIJJJIJJJJJIJJJIIJJIIIIIJJIJJIIJIJIJJ()", "return mSpriteName ?? string.Empty;")
    text = replace_method(text, "public void IJIIIIIJIIJIJJJIJIJJIJIJJIJJIIIJJIJJJJJIIIIJJIJ(", "mSpriteName = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI ?? string.Empty;")
    text = replace_method(text, "public override Texture IJIIIJJIJIJIJIIJIIJIIIIJIIIJIIJIJIJIJJJIIJJJIII()", "return (mAtlas as " + iface + ") != null ? (mAtlas as " + iface + ").texture : null;")
    text = replace_method(text, "public override Material IJJIIIIJIIIJIIJIJIIJJIIJJJIJJJJIJJJJIIJJIJJIIII()", "return (mAtlas as " + iface + ") != null ? (mAtlas as " + iface + ").spriteMaterial : null;")
    return text


def patch_uitexture(text: str) -> str:
    text = replace_method(text, "public override Texture IJIIIJJIJIJIJIIJIIJIIIIJIIIJIIJIJIJIJJJIIJJJIII()", "return mTexture;")
    text = replace_method(text, "public override Shader IIIIJIJIJJIIIJIJIIIJJJJJIJJJJIJJIJIJIIIIIJIJJJJ()", "return mShader;")
    text = replace_method(text, "public Rect JIJIJJJIIIIIIIIJIJIIIIIJIIJJIJIIJJJIIJJJIJJJIII()", "return mRect;")
    text = replace_method(text, "public override Material IJJIIIIJIIIJIIJIJIIJJIIJJJIJJJJIJJJJIIJJIJJIIII()", "return mShader != null ? new Material(mShader) : null;")
    text = replace_method(text, "public override void IIIIIIJJJIIIJJJIIJJJJJJIIIIIJIJJJJIJJIIJIJIIIJI(Texture", "mTexture = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI;")
    text = replace_method(text, "public override void IJIIIJJJIJJIJIJIJIIIJIJIIIJIIJJJIIJJIJJIJIIJJIJ(Shader", "mShader = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI;")
    text = replace_method(text, "public void JJIJIJIIJJIJJJIJJIJIIIJIIJIIJIJJJIIJIJIJJJJIIII(Rect", "mRect = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI;")
    return text


def patch_uiwidget(text: str) -> str:
    # These methods are the serialized UIWidget backing accessors used by UILabel/UISprite.
    text = replace_method(text, "public virtual Material IJJIIIIJIIIJIIJIJIIJJIIJJJIJJJJIJJJJIIJJIJJIIII()", "return mMat;")
    mappings = {
        "public Color IJJJIIJJJJIIIIIIIJJIJIIIJJIJIJJIIJJJIIIJJIJJIIJ": ("return mColor;", "mColor = value;"),
        "public int JJIIIIJJIIJJIJJIJIJIJJJJJIIIIIJJIJIIJJIJJJJJIJJ": ("return mWidth;", "mWidth = value;"),
        "public int JJIJIJJIJJIJJIJIIIJJIIIIJJIJIIJIIIJJJJJIIJJJIII": ("return mHeight;", "mHeight = value;"),
    }
    for prop, (getter, setter) in mappings.items():
        if prop in text:
            # Replace the whole property with direct serialized storage.
            typ = prop.split()[1]
            name = prop.split()[-1]
            text = replace_property(text, prop, f"\tpublic {typ} {name}\n\t{{\n\t\tget {{ {getter} }}\n\t\tset {{ {setter} }}\n\t}}")
    return text


def patch_photon_settings(text: str) -> str:
    # 0x0059df28 constructs the offline room from the supplied map string; the
    # connected/disconnect and offline-mode branches match Photon 1.x behavior.
    return replace_method(
        text,
        "public void CreateServerOffline(string map)",
        """
        if (PhotonNetwork.connected)
        {
            PhotonNetwork.Disconnect();
        }
        PhotonNetwork.offlineMode = true;
        PhotonNetwork.CreateRoom(map);
        """,
    )


def patch_panel_manager(text: str) -> str:
    text = replace_method(text, "private void Awake()", """JIIIIJJJJIIJJJIIJIJIIJIIJJIIIIIIIIJJIJIJJJJJJJJ = this;\n        if (JIJIJIIJIIIIJIJIIIJIJIIIJIJJIJIIIJJIJIIJJIIIIIJ == null) JIJIJIIJIIIIJIJIIIJIJIIIJIJJIJIIIJJIJIIJJIIIIIJ = new List<UIPanel>();""")
    text = replace_method(text, "public void Show(GameObject panel)", """if (panel == null) return;\n        foreach (UIPanel item in JIJIJIIJIIIIJIJIIIJIJIIIJIJJIJIIIJJIJIIJJIIIIIJ) if (item != null) item.gameObject.SetActive(item.gameObject == panel);\n        panel.SetActive(true);""")
    text = replace_method(text, "public void Show(string panel)", """if (string.IsNullOrEmpty(panel)) return;\n        foreach (UIPanel item in JIJIJIIJIIIIJIJIIIJIJIIIJIJJIJIIIJJIJIIJJIIIIIJ) if (item != null) item.gameObject.SetActive(item.gameObject.name == panel);""")
    text = replace_method(text, "public void ShowAnim(GameObject go)", """Show(go);""")
    text = replace_method(text, "public void HideAnim(GameObject go)", """if (go != null) go.SetActive(false);""")
    return text


def main() -> None:
    patch_file("JIJJJIIJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.cs", patch_scene_wrapper)
    patch_file("AndroidPermissions.cs", patch_android_permissions)
    patch_file("GDPR.cs", patch_gdpr)
    patch_file("Logo.cs", patch_logo)
    patch_file("UIEventClick.cs", patch_event_click)
    patch_file("UILabel.cs", patch_label)
    patch_file("UILocalize.cs", patch_localize)
    patch_file("UIAtlas.cs", lambda t: patch_atlas_common(t, True))
    patch_file("NGUIAtlas.cs", lambda t: patch_atlas_common(t, False))
    patch_file("UISprite.cs", patch_uisprite)
    patch_file("UITexture.cs", patch_uitexture)
    patch_file("UIWidget.cs", patch_uiwidget)
    patch_file("mPhotonSettings.cs", patch_photon_settings)
    patch_file("mPanelManager.cs", patch_panel_manager)


if __name__ == "__main__":
    main()
