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
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    replacement = "{\n" + "\n".join(indent + line.rstrip() if line else "" for line in body_lines) + "\n\t}"
    return text[:brace] + replacement + text[close + 1 :]


def replace_property(text: str, signature: str, replacement: str) -> str:
    start = text.find(signature)
    if start < 0:
        raise RuntimeError(f"property signature not found: {signature}")
    line_start = text.rfind("\n", 0, start) + 1
    brace = text.find("{", start)
    semi = text.find(";", start)
    replacement = "\t" + replacement.lstrip()
    if semi >= 0 and (brace < 0 or semi < brace):
        line_end = text.find("\n", semi)
        if line_end < 0:
            line_end = len(text)
        return text[:line_start] + replacement + text[line_end:]
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
    return text[:line_start] + replacement + text[close + 1 :]


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
    # OnJoinedRoom (RVA 0x006c3330): the tutorial offline room entered from the
    # GDPR training prompt loads MainTutorial via the verified scene wrapper.
    text = replace_method(
        text,
        "private void OnJoinedRoom()",
        'JIJJJIIJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.JIJJJIIJJIIJIIIJIJIIIJIJIIJIIIJJJJIIIJIJIJIIJII("MainTutorial");',
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


def patch_mplayer_camera(text: str) -> str:
    text = replace_method(
        text,
        "private void Awake()",
        """
        JIIIIJJJJIIJJJIIJIJIIJIIJJIIIIIIIIJJIJIJJJJJJJJ = this;
        IJJJIJJJJIIIIIIJJIJJJJJJIIIIJIIIJIIJIIJIJJIJIJJ = GetComponent<Camera>();
        """,
    )
    return text


def patch_mothers(text: str) -> str:
    text = replace_method(text, "public void ExitGame()", "Application.Quit();")
    text = replace_method(text, "public void ShowOthersGames()", "Application.OpenURL(\"https://play.google.com/store/apps/dev?id=6363329851677974248\");")
    text = replace_method(text, "public void ShowToast(string text)", "UIToast.IIIJIIJJIJJJIIJIIIJIJIJJJIIIJIIIIIJIIIJJJJIJII(text);")
    return text


def patch_create_server(text: str) -> str:
    text = replace_method(text, "private void Start()", "JIIIIJJJJIIJJJIIJIJIIJIIJJIIIIIIIIJJIJIJJJJJJJJ = this;")
    text = replace_method(text, "public void Open()", "JIIIIJJJJIIJJJIIJIJIIJIIJJIIIIIIIIJJIJIJJJJJJJJ = this;")
    text = replace_method(
        text,
        "public void SetMaxPlayer(GameObject go)",
        """
        if (go == null) return;
        IIIJIIIJJJJJJIIJJJIIJJIJIIJIIIJIIIIIIIJJJIJJIJJ = int.Parse(go.name);
        if (IIJIIJJIJIJIJJIJJIIIIIJJIJIJJIJJIIIIIIIJIJIJJJJ != null)
        {
            IIJIIJJIJIJIJJIJJIIIIIJJIJIJJIJJIIIIIIIJIJIJJJJ.transform.localPosition = go.transform.localPosition;
        }
        """,
    )
    return text


def patch_photon_settings(text: str) -> str:
    # All names below are the ground-truth obfuscated 6.5.1 symbols:
    #   JJIJJJIIII...IJIIJ = the real PUN static class ("PhotonNetwork"):
    #     IIIJIIJJII...IJIII() -> bool   connected-check (property JJJIJIIIII... wraps it)
    #     IJIJJJJIJI...JIIJJ()           Disconnect()
    #     JJIJIJIJII...JJIIJI            offline-mode property (getter 0x0049c544
    #                                    reads static+0xb1, setter calls 0x0049c5d0)
    #     IIJJIIIIIJ...JIIJJI            message-queue property (setter 0x0049d840)
    #     IIJJJJJJII...IIIIJ(string)     CreateRoom(name) (0x004a2078)
    #     JIJIIJIJII...JIJJJ(string)     sync scene load (0x004a96ac)
    #     IJJIIJIJJJ...JIIJJ() -> room   current-room getter (0x0049bb98)
    #   JIIIIIJIII...JJIJJ  = game-mode manager (reset 0x00d8d5d8 / set 0x00d8e644)
    #   IIIIIIIJIJ...JJIIJ  = extensions (room.GetGameMode() 0x01475d6c)
    #   IJJJIJJIII...JJJII  = localization (Get(key) 0x016f9c68)
    #   JIJJJIIJJI...IIJII  = scene wrapper (LoadScene 0x013bd5e8, guard flag @+0)

    # CreateServerOffline (RVA 0x0059df28): store the map in the deferred
    # helper, require a logged-in account (AccountManager static bool @+0x04),
    # disconnect an active Photon connection, reset the game-mode manager,
    # show the localized "Loading..." popup and schedule the helper through
    # TimerManager.In(0.2f, ...). Without an account: localized toast
    # "Connection account".
    text = replace_method(
        text,
        "public void CreateServerOffline(string map)",
        """
        JJJJIIIJIIJJIJJIIIJJIJIJIIIJIIIJIJIJIJIJJJIIJIJ deferredCreate = new JJJJIIIJIIJJIJJIIIJJIJIJIIIJIIIJIJIJIJIJJJIIJIJ();
        deferredCreate.JJJIJIJJIIJJIIIJIJJIIJJIIJIIJJIJJIJJJIIIIIIJIJI = map;
        if (AccountManager.JIIJJIJJJJJJJJJJIIIIJJJIJIJJJJIJJIIIIJJIIIJIJJI)
        {
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIIJIIJJIIJIIIIJIIJIIJJJIJJJIIJIIJIIJJIJIIIJIII())
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJJJJIJIJIIJJIIJJIIJIJJIIJIJIJIJIJJJJJIJJIIJJ();
            }
            JIIIIIJIIIJIJIJIIJJJJIIIJIIJIIJJIJJJJIIJJJJJIJJ.IJIIIJIIJJIJIJJJIIJJJJIIIIJIJIIJJIJIJJJJIJJIJJJ();
            mPopUp.JIIJJJJJJIIIIIJIJIIJJJIIJIJJJIJJIIIIJIJIJIJIIIJ(IJJJIJJIIIJJIJJJIIIJIIJIJIJJIIJJIJJIIJJIJJJJJII.IJIIIIIIIIJJIIJIJJIIIIIJIIJIIIIIJIIJJIIIIJIIIJI("Loading") + "...");
            TimerManager.In(0.2f, new Callback(deferredCreate.IJIIJIIIIIIJIIIIJJJIJIIJJIJJJJIIJIJJJIJJJIJIIJI));
        }
        else
        {
            UIToast.IIIJIIJJIJJJIIJIIIJIJIJJJIIIJIIIIIJIIIJJJJIJIIJ(IJJJIJJIIIJJIJJJIIIJIIJIJIJJIIJJIJJIIJJIJJJJJII.IJIIIIIIIIJJIIJIJJIIIIIJIIJIIIIIJIIJJIIIIJIIIJI("Connection account"));
        }
        """,
    )
    # Deferred offline-create helper (RVA 0x0071d948, scheduled by
    # CreateServerOffline): show the "Loading..." popup, store the map into
    # the private static map-name field, enable Photon offline mode, clear
    # the scene-wrapper guard flag and create the offline room.
    text = replace_method(
        text,
        "internal void IJIIJIIIIIIJIIIIJJJIJIIJJIJJJJIIJIJJJIJJJIJIIJI()",
        """
            mPopUp.JIIJJJJJJIIIIIJIJIIJJJIIJIJJJIJJIIIIJIJIJIJIIIJ(IJJJIJJIIIJJIJJJIIIJIIJIJIJJIIJJIJJIIJJIJJJJJII.IJIIIIIIIIJJIIJIJJIIIIIJIIJIIIIIJIIJJIIIIJIIIJI("Loading") + "...");
            JJIJIJIJIJJJJJIIJIIJJIJIJJJJJJIJIJIJJIIJIJIJIJJ = JJJIJIJJIIJJIIIJIJJIIJJIIJIIJJIJJIJJJIIIIIIJIJI;
            JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJIJIJIJIIJIIIJJJJIJIJJJIIJJJJIJIIJJJJJJIJJIIJI = true;
            JIJJJIIJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.IJJIIIIIIJIIIIIJJIIJJIJIJJJIJIJJJJIJJJJJIJJIJIJ = false;
            JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJJJJJJIIJJIIJJJIJIIIJJJJIJJJIIIJIJJJIJIIIIIIJ(JJJIJIJJIIJJIIIJIJJIIJJIIJIIJJIJJIJJJIIIIIIJIJI);
        """,
    )
    # OnJoinedRoom (RVA 0x0059d310): reset the game-mode manager, apply the
    # joined room's game mode, then load the stored map scene directly in
    # offline mode or pause the Photon message queue and sync-load it online.
    text = replace_method(
        text,
        "private void OnJoinedRoom()",
        """
        JIIIIIJIIIJIJIJIIJJJJIIIJIIJIIJJIJJJJIIJJJJJIJJ.IJIIIJIIJJIJIJJJIIJJJJIIIIJIJIIJJIJIJJJJIJJIJJJ();
        JIIIIIJIIIJIJIJIIJJJJIIIJIIJIIJJIJJJJIIJJJJJIJJ.JJJIJIIJJJIIIJIIJJJIIJIJIIIIJIJIIIJJIJIIJIIIIIJ(JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJJIIJIJJJIJJJIIIJJIJIIIJIJIIJIJIJJJIJJJJJJIIJJ().JIJJJJIIIIIJIIJIJJJIJJJIJIIJIIJIIJJIIIIJJJIIIII());
        if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJIJIJIJIIJIIIJJJJIJIJJJIIJJJJIJIIJJJJJJIJJIIJI)
        {
            JIJJJIIJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.JIJJJIIJJIIJIIIJIJIIIJIJIIJIIIJJJJIIIJIJIJIIJII(JJIJIJIJIJJJJJIIJIIJJIJIJJJJJJIJIJIJJIIJIJIJIJJ);
        }
        else
        {
            JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJJIIIIIJJIJIIJIIIIIJIJJJIIJIIJIJIIJIJJIJIIJJI = false;
            JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJIIJIJIIIIJIJJIIJIJIJJIIIJIIJIIIJJJIIJJJIJIJJ(JJIJIJIJIJJJJJIIJIIJJIJIJJJJJJIJIJIJJIIJIJIJIJJ);
        }
        """,
    )
    return text


def patch_networking_peer(text: str) -> str:
    """Obfuscated NetworkingPeer (JJJJJIJJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII).

    global-metadata.dat lists the instance fields at +0xb0/+0xb4/+0xbc as
    `<name>k__BackingField`, i.e. they were public auto-properties in the
    original assembly (PUN 1.x NetworkingPeer.Server/State/lobby).  The script
    export flattened them to private fields, which makes the verified
    PhotonNetwork bodies (CreateRoom 0x004a210c, EnterOfflineRoom 0x004a2628,
    connected 0x0049af18, connectionStateDetailed 0x0049b61c) uncompilable.
    Restore the original (public) accessibility; no names are invented.
    """
    for decl in (
        # +0xb0 ServerConnection Server
        "IIIJIIJJJIJIJIIJIIJJJJJIIIIJJIIJIIJIJIIIJJIJJJJ JJIJIJJJIJIIJIJJIIIIIJJIJIIIJJIIJIIIJIJIJJJJJII;",
        # +0xb4 ClientState State
        "JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ IJJJIIIIJIIJIJIIIIIIJJJJIJIJJJIIIIIIJIJJIIIIIII;",
        # +0xbc TypedLobby lobby
        "IJIJIIJIJJJJIJJIIJIJJIJJIJIJJIJJJJIIJJJJIJJJJJJ IIIIJIIIJIIJJIIJJJIJJJIJIJIIIIIIJJJIIIJIIJJIJJJ;",
    ):
        text = text.replace("private " + decl, "public " + decl)
    # SendMonoMessage (RVA 0x008f8364): in this build the PUN
    # GameObject.SendMessage dispatch was replaced by a 30-entry jump table
    # (switch on PhotonNetworkingMessage, jump table at file offset 0x8f83bc)
    # that invokes the public static delegate fields of the obfuscated
    # PhotonNetwork (+0x18..+0x84).  Case->field mapping, delegate types and
    # parameter unboxing were decoded case-by-case; enum values 17
    # (OnPhotonSerializeView) and 28 (OnPhotonPlayerActivityChanged) jump to
    # the common return (no delegate).
    text = replace_method(
        text,
        "public static void IJIJJJIIJIJIIIJIIJJJIIJIJJJJJIIIIIIIIIJIIIIIIJJ(IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ",
        """
        // RVA 0x008f8364 (verified against libil2cpp.so disassembly; jump
        // table at 0x008f83bc, one static delegate field of the obfuscated
        // PhotonNetwork per PhotonNetworkingMessage value).
        switch (JJIJIJJJIIIIIJIJJJIIJJIJIIIJIJIIJIJIIJJJJJIJJJJ)
        {
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnConnectedToPhoton:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJJJIJIJJIIIIIIIJJIJJJJIJJIJJJIJJIIIIJIJJIJIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJJJIJIJJIIIIIIIJJIJJJJIJJIJJJIJJIIIIJIJJIJIJ();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnLeftRoom:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJJJIJJIJJJIJIIJIJIIJIIIIJIJJIJJJJJJJIIIJJIIJII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJJJIJJIJJJIJIIJIJIIJIIIIJIJJIJJJJJJJIIIJJIIJII();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnMasterClientSwitched:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIIJJJIIJIIIIIJIJJIJJIJIIJIIJIIIJIIJIJIIIJIJIIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIIJJJIIJIIIIIJIJJIJJIJIIJIIJIIIJIIJIJIIIJIJIIJ((JJJJIIJIIIJIIIJIIJIJJJJIJJJJIIIJIJIIJIIJJIIJIII)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonCreateRoomFailed:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJJIJIJIIJJIJIJIIIIJJIJJIJIIIJIJIIJIJIJIIIJJJJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJJIJIJIIJJIJIJIIIIJJIJJIJIIIJIJIIJIJIJIIIJJJJ((short)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0], (string)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[1]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonJoinRoomFailed:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJIIIIJJIJIJJJJJJJIJJIJJIIJJJJIJIJIIJIIJIJJJII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJIIIIJJIJIJJJJJJJIJJIJJIIJJJJIJIJIIJIIJIJJJII((short)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0], (string)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[1]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnCreatedRoom:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJIIIJJIIIIJIIIJJIJJJIIJJIJIIIJJIIIIJIJIIJIIIIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJIIIJJIIIIJIIIJJIJJJIIJJIJIIIJJIIIIJIJIIJIIIIJ();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnJoinedLobby:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJIIIJIJJIIJIIIJJJJJIIIJIJIJJIIJIJIIJIJIJJJJJJJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJIIIJIJJIIJIIIJJJJJIIIJIJIJJIIJIJIIJIJIJJJJJJJ();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnLeftLobby:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJJIJIIIIJIJJJJJJJJJIJJIJJJIIIIJIJJJIIIJJJIIII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJJIJIIIIJIJJJJJJJJJIJJIJJJIIIIJIJJJIIIJJJIIII();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnDisconnectedFromPhoton:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJJJJIJJIIJIIJJJJJIIIJIJJIJIJIIJJIIIJIJIJJIJJJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJJJJIJJIIJIIJJJJJIIIJIJJIJIJIIJJIIIJIJIJJIJJJ();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnConnectionFail:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJJIIJIJJJIJIIIJIIJIIIIJIJJIIJIIIIIJIIIJIIJJJII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJJIIJIJJJIJIIIJIIJIIIIJIJJIIJIIIIIJIIIJIIJJJII((JIJJIJIIJIJJIIIJJIIJIJIIJIJIJIJJIIJIJJIJJIJIIJI)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnFailedToConnectToPhoton:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJIIJIIJIIIIIJIJJJIJJIIJIJIIIJIIJIJIIJJJJIIJIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJIIJIIJIIIIIJIJJJIJJIIJIJIIIJIIJIJIIJJJJIIJIJ((JIJJIJIIJIJJIIIJJIIJIJIIJIJIJIJJIIJIJJIJJIJIIJI)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnReceivedRoomListUpdate:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJIIJIIJIJIJJIJJIIIIIJIIJIJIIIIIJIIIJIJIIIJIJJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJIIJIIJIJIJJIJJIIIIIJIIJIJIIIIIJIIIJIJIIIJIJJ();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnJoinedRoom:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIIJIJIJJJIIIJJIJIJJIJJJIJJJJIIIIIIJJJJJJIJIII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIIJIJIJJJIIIJJIJIJJIJJJIJJJJIIIIIIJJJJJJIJIII();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonPlayerConnected:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJJIJIIIJIJJJIIIIJIIJJIJIIJIIJJIJIIIJIJIIJIJJIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJJIJIIIJIJJJIIIIJIIJJIJIIJIIJJIJIIIJIJIIJIJJIJ((JJJJIIJIIIJIIIJIIJIJJJJIJJJJIIIJIJIIJIIJJIIJIII)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonPlayerDisconnected:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJIIIIIIJIIJJJIIJIIJJIJIJJIJIIIJJJJIIIIJIJIIIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJIIIIIIJIIJJJIIJIIJJIJIJJIJIIIJJJJIIIIJIJIIIJ((JJJJIIJIIIJIIIJIIJIJJJJIJJJJIIIJIJIIJIIJJIIJIII)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonRandomJoinFailed:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJJIIJJJJIJIIJJJJIJIIIJJIJJIJIIJJJJJIJIIJIJJJJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIJJIIJJJJIJIIJJJJIJIIIJJIJJIJIIJJJJJIJIIJIJJJJ((short)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0], (string)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[1]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnConnectedToMaster:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJJIIJJJJIIJIJJIJIIJJJJJJIJIJJIIIJIIIIIJJIJJJIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJJIIJJJJIIJIJJIJIIJJJJJJIJIJJIIIJIIIIIJJIJJJIJ();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonInstantiate:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIIJIIIJIJJJJIIIIIIIIIIIIJJIIIJIIIIJIIIIJJIIJJI != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIIJIIIJIJJJJIIIIIIIIIIIIJJIIIJIIIIJIIIIJJIIJJI(JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonMaxCccuReached:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIIIIJIJJIIJJIJJIJIJIJJJIJIJJIJIIIJJJIJJJJIIIII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIIIIJIJJIIJJIJJIJIJIJJJIJIJJIJIIIJJJIJJJJIIIII();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonCustomRoomPropertiesChanged:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIIIJJIJIIJIJIIIIJIIIIJIJIIIJJJIIJJIJIJIJJIIJJJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IIIIJJIJIIJIJIIIIJIIIIJIJIIIJJJIIJJIJIJIJJIIJJJ((Hashtable)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnPhotonPlayerPropertiesChanged:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJJIIIIIJIIIIJJIJIIIJJIJJIIIJIJJJIIIJJJJJJJIIII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJJIIIIIJIIIIJJIJIIIJJIJJIIIJIJJJIIIJJJJJJJIIII(JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnUpdatedFriendList:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJJIJIIIIIJIIJJJIIJJJJJJIIIIJJIJIJIIJJIIJJIJII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIJJIJIIIIIJIIJJJIIJJJJJJIIIIJJIJIJIIJJIIJJIJII();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnCustomAuthenticationFailed:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJIJIIIJJIIJJJIJIJIIJJJJJIJJIJJJIIJJIJJIJIJIJIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JJIJIIIJJIIJJJIJIJIIJJJJJIJJIJJJIIJJIJJIJIJIJIJ((string)JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ[0]);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnCustomAuthenticationResponse:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJJIIJJJJIIIIJIIJJJJIIIJJJJJJIJIIJIIIIIIJJJJJII != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJJIIJJJJIIIIJIIJJJJIIIJJJJJJIJIIJIIIIIIJJJJJII(JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnWebRpcResponse:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJIJIJJIIIJJIIIJIJIJJJIIIJIJJJIJJJJJJJJIJJJIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJIJIJJIIIJJIIIJIJIJJJIIIJIJJJIJJJJJJJJIJJJIJ(JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnOwnershipRequest:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJJJJIJJJIIJIJIJIIIIJIIIIIIIIJIJJJJIIIJJIIIIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJJJJIJJJIIJIJIJIIIIJIIIIIIIIJIJJJJIIIJJIIIIJ(JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ);
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnLobbyStatisticsUpdate:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIIIIJJJIIIIJJJIJIIJIJIIJJJJIJJIIIIJIJIIIJJJIJJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.JIIIIJJJIIIIJJJIJIIJIJIIJJJJIJJIIIIJIJIIIJJJIJJ();
            }
            break;
        case IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnOwnershipTransfered:
            if (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJJIJIIJIIIIJIIJJIJJIJIIJJIIJJIIIJJJJJJIIJJIJ != null)
            {
                JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.IJIJJIJIIJIIIIJIIJJIJJIJIIJJIIJJIIIJJJJJJIIJJIJ(JIJIJIJIIIIJIJIIIIIIJJIJIJJIIJJIIIJJIIJJIJJIJJJ);
            }
            break;
        }
        """,
    )
    return text


def patch_photon_network(text: str) -> str:
    """Obfuscated PhotonNetwork (JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ).

    Every body below was reconstructed from the ARMv7 disassembly of
    libil2cpp.so (RVAs in the per-method comments); string literals, enum
    constants and field offsets were resolved through global-metadata.dat.
    """
    # connected getter method (RVA 0x0049af18): offlineMode -> true,
    # null peer -> false, else !IsInitialConnect(+0xb8) and
    # State(+0xb4) not in {PeerCreated=1, Disconnecting=14, Disconnected=15}.
    text = replace_method(
        text,
        "public static bool IIIJIIJJIIJIIIIJIIJIIJJJIJJJIIJIIJIIJJIJIIIJIII()",
        """
        // RVA 0x0049af18 (verified against libil2cpp.so disassembly)
        if (JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII)
        {
            return true;
        }
        if (JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI == null)
        {
            return false;
        }
        if (JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IJJJJJIIIIIIIIIIIIIIIJIJIIJIJIJJIIIJJJJJJJJIJII)
        {
            return false;
        }
        JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ state = JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IJJJIIIIJIIJIJIIIIIIJJJJIJIJJJIIIIIIJIJJIIIIIII;
        return state != JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.PeerCreated && state != JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Disconnected && state != JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Disconnecting;
        """,
    )
    # connectionStateDetailed getter method (RVA 0x0049b61c):
    # offline -> Joined(9)/ConnectedToMaster(16), null peer -> Disconnected(15),
    # else networkingPeer.State (+0xb4).
    text = replace_method(
        text,
        "public static JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ JIIJIIJIIJJIIJIIJJJIJJIIJIIJJJJJJJJJJIIJJIIIJII()",
        """
        // RVA 0x0049b61c (verified against libil2cpp.so disassembly)
        if (JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII)
        {
            return (IJJJJIIJIJIIJJJJJJJIJJJJIIJJIIJIJJJJIIJJJJIIJJI != null) ? JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Joined : JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.ConnectedToMaster;
        }
        if (JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI == null)
        {
            return JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Disconnected;
        }
        return JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IJJJIIIIJIIJIJIIIIIIJJJJIJIJJJIIIIIIJIJJIIIIIII;
        """,
    )
    # connectedAndReady getter method (RVA 0x0049b47c): the compiler lowered
    # the state switch to `(0xd2e >> (state-8)) & 1` plus explicit checks for
    # PeerCreated(1)/ConnectingToGameserver(6); decoded false-set:
    # {1, 6, 8, 12, 14, 15, 17, 20}.
    text = replace_method(
        text,
        "public static bool JIJJJJIJJIJJIIJIJIIIIIIIJIIIJIJJJJIIJJIJIIIIIII()",
        """
        // RVA 0x0049b47c (verified against libil2cpp.so disassembly)
        if (!IIIJIIJJIIJIIIIJIIJIIJJJIJJJIIJIIJIIJJIJIIIJIII())
        {
            return false;
        }
        if (JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII)
        {
            return true;
        }
        switch (JIIJIIJIIJJIIJIIJJJIJJIIJIIJJJJJJJJJJIIJJIIIJII())
        {
        case JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.PeerCreated:
        case JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.ConnectingToGameserver:
        case JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Joining:
        case JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.ConnectingToMasterserver:
        case JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Disconnecting:
        case JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Disconnected:
        case JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.ConnectingToNameServer:
        case JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Authenticating:
            return false;
        default:
            return true;
        }
        """,
    )
    # offlineMode getter method (RVA 0x0049c544): returns the static bool at
    # PhotonNetwork static fields +0xb1.
    text = replace_method(
        text,
        "public static bool JJJJJJIJIJJIJIIJJJJJIIJJJIJIIJJJJJJJIJJIJJIIJIJ()",
        """
        // RVA 0x0049c544 (verified against libil2cpp.so disassembly)
        return JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII;
        """,
    )
    # offlineMode setter method (RVA 0x0049c5d0).
    text = replace_method(
        text,
        "public static void IIJIIIJIIIJIJIJJIJJIJIIIIJIJJIIJJIIIJIIJIJIIIJJ(bool",
        """
        // RVA 0x0049c5d0 (verified against libil2cpp.so disassembly)
        if (JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI == JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII)
        {
            return;
        }
        if (JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI && IIIJIIJJIIJIIIIJIIJIIJJJIJJJIIJIIJIIJJIJIIIJIII())
        {
            UnityEngine.Debug.LogError("Can't start OFFLINE mode while connected!");
            return;
        }
        if (JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.PeerState != PeerStateValue.Disconnected)
        {
            JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.Disconnect();
        }
        JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI;
        if (JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
        {
            JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.JIJIJJJJJIIIIIIIIIIIIJJJJIIIJJJIIJJJJJJJJIJIJIJ(-1);
            JJJJJIJJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.IJIJJJIIJIJIIIJIIJJJIIJIJJJJJIIIIIIIIIJIIIIIIJJ(IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnConnectedToMaster, Array.Empty<object>());
        }
        else
        {
            IJJJJIIJIJIIJJJJJJJIJJJJIIJJIIJIJJJJIIJJJJIIJJI = null;
            JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.JIJIJJJJJIIIIIIIIIIIIJJJJIIIJJJIIJJJJJJJJIJIJIJ(-1);
        }
        """,
    )
    # CreateRoom(string) (RVA 0x004a2078): tail-calls the 4-arg overload with
    # null options/lobby/expectedUsers.
    text = replace_method(
        text,
        "public static bool IIJJJJJJIIJJIIJJJIJIIIJJJJIJJJIIIJIJJJIJIIIIIIJ(string IIIJJJJJIJIIJJIIIJJIIJJIJIJIJJJIJJJIIJJIIJJIJIJ)",
        """
        // RVA 0x004a2078 (verified against libil2cpp.so disassembly)
        return IIJJJJJJIIJJIIJJJIJIIIJJJJIJJJIIIJIJJJIJIIIIIIJ(IIIJJJJJIJIIJJIIIJJIIJJIJIJIJJJIJJJIIJJIIJJIJIJ, null, null, null);
        """,
    )
    # CreateRoom(string, RoomOptions, TypedLobby) (RVA 0x004a258c): delegates
    # to the 4-arg overload with null expectedUsers.
    text = replace_method(
        text,
        "public static bool IIJJJJJJIIJJIIJJJIJIIIJJJJIJJJIIIJIJJJIJIIIIIIJ(string IIIJJJJJIJIIJJIIIJJIIJJIJIJIJJJIJJJIIJJIIJJIJIJ, JIIJIIJIIJIJJJJJIIJJJIIJIJJJIIJIIJJJJIIJJJJJJIJ IJJIIIJIJJJJIJIIJIIIJJJIJIJJJJJJIJJJIIJJJIJJIII, IJIJIIJIJJJJIJJIIJIJJIJJIJIJJIJJJJIIJJJJIJJJJJJ JIIIJIIIJJJJIIJJJIJIJJIJJJIJJIJIJIJJIIIIIIJIJJI)",
        """
        // RVA 0x004a258c (verified against libil2cpp.so disassembly)
        return IIJJJJJJIIJJIIJJJIJIIIJJJJIJJJIIIJIJJJIJIIIIIIJ(IIIJJJJJIJIIJJIIIJJIIJJIJIJIJJJIJJJIIJJIIJJIJIJ, IJJIIIJIJJJJIJIIJIIIJJJIJIJJJJJJIJJJIIJJJIJJIII, JIIIJIIIJJJJIIJJJIJIJJIJJJIJJIJIJIJJIIIIIIJIJJI, null);
        """,
    )
    # CreateRoom(string, RoomOptions, TypedLobby, string[]) (RVA 0x004a210c).
    # Offline branch: guard on offlineModeRoom(+0xb4), else EnterOfflineRoom.
    # Online branch: Server(+0xb0) must be MasterServer(0) and
    # connectedAndReady; lobby fallback via insideLobby(+0xb9)/lobby(+0xbc);
    # fills obfuscated EnterRoomParams {+8 name, +0xc options, +0x10 lobby,
    # +0x1c expectedUsers} and tail-calls NetworkingPeer.OpCreateGame
    # (0x008faac0).  String literals verified in global-metadata.dat.
    text = replace_method(
        text,
        "public static bool IIJJJJJJIIJJIIJJJIJIIIJJJJIJJJIIIJIJJJIJIIIIIIJ(string IIIJJJJJIJIIJJIIIJJIIJJIJIJIJJJIJJJIIJJIIJJIJIJ, JIIJIIJIIJIJJJJJIIJJJIIJIJJJIIJIIJJJJIIJJJJJJIJ IJJIIIJIJJJJIJIIJIIIJJJIJIJJJJJJIJJJIIJJJIJJIII, IJIJIIJIJJJJIJJIIJIJJIJJIJIJJIJJJJIIJJJJIJJJJJJ JIIIJIIIJJJJIIJJJIJIJJIJJJIJJIJIJIJJIIIIIIJIJJI, string[] IIJIIIJJIJIJIIIIIIIJIIIJJJJJJIIIIIIJJIIJJIIIIII)",
        """
        // RVA 0x004a210c (verified against libil2cpp.so disassembly)
        if (JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII)
        {
            if (IJJJJIIJIJIIJJJJJJJIJJJJIIJJIIJIJJJJIIJJJJIIJJI != null)
            {
                UnityEngine.Debug.LogError("CreateRoom failed. In offline mode you still have to leave a room to enter another.");
                return false;
            }
            JIIIIJIIJJJJJJIJIJIIJIJIIIJJIIJJIIJIIIJIJIIIIJI(IIIJJJJJIJIIJJIIIJJIIJJIJIJIJJJIJJJIIJJIIJJIJIJ, IJJIIIJIJJJJIJIIJIIIJJJIJIJJJJJJIJJJIIJJJIJJIII, true);
            return true;
        }
        if (JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.JJIJIJJJIJIIJIJJIIIIIJJIJIIIJJIIJIIIJIJIJJJJJII != IIIJIIJJJIJIJIIJIIJJJJJIIIIJJIIJIIJIJIIIJJIJJJJ.MasterServer || !JIJJJJIJJIJJIIJIJIIIIIIIJIIIJIJJJJIIJJIJIIIIIII())
        {
            UnityEngine.Debug.LogError("CreateRoom failed. Client is not on Master Server or not yet ready to call operations. Wait for callback: OnJoinedLobby or OnConnectedToMaster.");
            return false;
        }
        if (JIIIJIIIJJJJIIJJJIJIJJIJJJIJJIJIJIJJIIIIIIJIJJI == null)
        {
            JIIIJIIIJJJJIIJJJIJIJJIJJJIJJIJIJIJJIIIIIIJIJJI = JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IIIIJJJIIJIIIJIIIIJIJIJIJIIIJJIJJJIIJJIJIJIIIJJ ? JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IIIIJIIIJIIJJIIJJJIJJJIJIJIIIIIIJJJIIIJIIJJIJJJ : null;
        }
        IJIJJIJIIJIIIJJJIJIIIIJJJJJIIIJIJIIIJIIJJJIIIJI opParams = new IJIJJIJIIJIIIJJJIJIIIIJJJJJIIIJIJIIIJIIJJJIIIJI();
        opParams.JIIIJIIIJJJIJIIJJJIIIIJJIJJIIIIIJIJJJJIJJJJJIJJ = IIIJJJJJIJIIJJIIIJJIIJJIJIJIJJJIJJJIIJJIIJJIJIJ;
        opParams.JIIJIIJIIJIJJJJJIIJJJIIJIJJJIIJIIJJJJIIJJJJJJIJ = IJJIIIJIJJJJIJIIJIIIJJJIJIJJJJJJIJJJIIJJJIJJIII;
        opParams.IJIIJIIIJIIIJIIJIIIIIIIJIIJJIIIIIIIJIJJJIIIJIII = JIIIJIIIJJJJIIJJJIJIJJIJJJIJJIJIJIJJIIIIIIJIJJI;
        opParams.JIIJIJIJIJIIIJJJJJIIJJIIJJJJJJIJJJJIIJJIIIJIJIJ = IIJIIIJJIJIJIIIIIIIJIIIJJJJJJIIIIIIJJIIJJIIIIII;
        return JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.JJJJIJJJJIIJJIJIJJJJIIJIJJIJJJJIIIIIJIIJIJJIJII(opParams);
        """,
    )
    # EnterOfflineRoom (RVA 0x004a2628): offlineModeRoom = new Room(name,
    # options); ChangeLocalID(1); State = ConnectingToGameserver(6);
    # OnStatusChanged(StatusCode.Connect=1024); masterClientId(+0x28) = 1;
    # SendMonoMessage(OnCreatedRoom=5) when createdRoom, then
    # SendMonoMessage(OnJoinedRoom=12).
    text = replace_method(
        text,
        "private static void JIIIIJIIJJJJJJIJIJIIJIJIIIJJIIJJIIJIIIJIJIIIIJI(string",
        """
        // RVA 0x004a2628 (verified against libil2cpp.so disassembly)
        IJJJJIIJIJIIJJJJJJJIJJJJIIJJIIJIJJJJIIJJJJIIJJI = new IIJIIJIIJIJJIIJIJJJJJJJIIIJJJIIIIIIJJIIIJJJIJII(IIIJJJJJIJIIJJIIIJJIIJJIJIJIJJJIJJJIIJJIIJJIJIJ, IJJIIIJIJJJJIJIIJIIIJJJIJIJJJJJJIJJJIIJJJIJJIII);
        JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.JIJIJJJJJIIIIIIIIIIIIJJJJIIIJJJIIJJJJJJJJIJIJIJ(1);
        JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IJJJIIIIJIIJIJIIIIIIJJJJIJIJJJIIIIIIJIJJIIIIIII = JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.ConnectingToGameserver;
        JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.OnStatusChanged(StatusCode.Connect);
        IJJJJIIJIJIIJJJJJJJIJJJJIIJJIIJIJJJJIIJJJJIIJJI.IJIIJIJIIJIJJJJIIIJJIIJJJIIJJIJJIIJJIIJIIJIIIII = 1;
        if (IJJIIJJIJIIIJJIIIIJIIIIIJIJIIIIIJIJJJJIJJJJJJII)
        {
            JJJJJIJJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.IJIJJJIIJIJIIIJIIJJJIIJIJJJJJIIIIIIIIIJIIIIIIJJ(IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnCreatedRoom, Array.Empty<object>());
        }
        JJJJJIJJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.IJIJJJIIJIJIIIJIIJJJIIJIJJJJJIIIIIIIIIJIIIIIIJJ(IJJIIIJJJIIJIJIJJIJJIJJJIIIJIJJIJIJJJJJIIJJIIIJ.OnJoinedRoom, Array.Empty<object>());
        """,
    )
    # room getter method (RVA 0x0049bb98): offline -> offlineModeRoom(+0xb4),
    # else obfuscated NetworkingPeer.CurrentRoom body (0x008fcbb0).
    text = replace_method(
        text,
        "public static IIJIIJIIJIJJIIJIJJJJJJJIIIJJJIIIIIIJJIIIJJJIJII IJJIIJIJJJIJJJIIIJJIJIIIJIJIIJIJIJJJIJJJJJJIIJJ()",
        """
        // RVA 0x0049bb98 (verified against libil2cpp.so disassembly)
        if (JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII)
        {
            return IJJJJIIJIJIIJJJJJJJIJJJJIIJJIIJIJJJJIIJJJJIIJJI;
        }
        return JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IIIIJIJIJIIJIJIJIJIIIJJJJIIIJJIIJJJIJIIJIJJIJII();
        """,
    )
    # isMessageQueueRunning getter method (RVA 0x0049d7b4): returns the static
    # bool at PhotonNetwork static fields +0xc8.
    text = replace_method(
        text,
        "public static bool JIJJJJIIIIJIJIJIJJJIIIJJIJJIJIJIJIIIIIJIJIJJIIJ()",
        """
        // RVA 0x0049d7b4 (verified against libil2cpp.so disassembly)
        return JJJJJJJJIIIJJJJIIJJJIIIJJIIIIIJIIJIIJIIJJJIIIII;
        """,
    )
    # isMessageQueueRunning setter method (RVA 0x0049d840): true ->
    # PhotonHandler fallback-send-ack starter (0x0063efac); then
    # networkingPeer.IsSendingOnlyAcks(+0x68, canonical PhotonPeer property)
    # = !value and the +0xc8 static = value.
    text = replace_method(
        text,
        "public static void IJJJIJIJJJIIJIIJIIJIIIJIIIIIJIIJIIJJJIJIJIJIJII(bool",
        """
        // RVA 0x0049d840 (verified against libil2cpp.so disassembly)
        if (JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
        {
            PhotonHandler.IJJIIJIIIIIJIIJIIIIIJJIIJIJJIJIIIJIJJJJJIIIJIJJ();
        }
        JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IsSendingOnlyAcks = !JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI;
        JJJJJJJJIIIJJJJIIJJJIIIJJIIIIIJIIJIIJIIJJJIIIII = JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI;
        """,
    )
    # Disconnect (RVA 0x004a1d08): offline -> offlineMode=false,
    # offlineModeRoom=null, State=Disconnecting(14),
    # OnStatusChanged(StatusCode.Disconnect=1025); online -> virtual
    # networkingPeer.Disconnect() (vtable +0xfc) when peer is non-null.
    text = replace_method(
        text,
        "public static void IJIJJJJIJIJIIJJIIJJIIJIJJIIJIJIJIJIJJJJJIJJIIJJ()",
        """
        // RVA 0x004a1d08 (verified against libil2cpp.so disassembly)
        if (JJJJJJJIIIJIJIIIJIJIJJJJIJJJIJJIJIJIIIIIIJJJJII)
        {
            IIJIIIJIIIJIJIJJIJJIJIIIIJIJJIIJJIIIJIIJIJIIIJJ(false);
            IJJJJIIJIJIIJJJJJJJIJJJJIIJJIIJIJJJJIIJJJJIIJJI = null;
            JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IJJJIIIIJIIJIJIIIIIIJJJJIJIJJJIIIIIIJIJJIIIIIII = JJJIJIIJIJIIIJJIIJIJIIIIJIIIJIJJIIJJJIIJIIJJJJJ.Disconnecting;
            JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.OnStatusChanged(StatusCode.Disconnect);
            return;
        }
        if (JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI != null)
        {
            JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.Disconnect();
        }
        """,
    )
    # LoadLevel(string) (RVA 0x004a96ac): clears networkingPeer flag +0x18d,
    # when automaticallySyncScene(+0xbc) forwards to the protected-internal
    # level-props sync (0x00912828, args levelName/true/false), pauses the
    # message queue (0x0049d840 with false), sets
    # loadingLevelAndPausedNetwork(+0x13a)=true and tail-calls the verified
    # scene wrapper (0x013bd5e8).
    text = replace_method(
        text,
        "public static void JIJIIJIJIIIIJIJJIIJIJIJJIIIJIIJIIIJJJIIJJJIJIJJ(string",
        """
        // RVA 0x004a96ac (verified against libil2cpp.so disassembly)
        JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.JJIJJIJIIJJJJJIJIIJIIJIIIIJIJJJJIIJJIJIIJJJIIIJ = false;
        if (IIJJJIJIJIJIIJIJIIIJIIIIIIJJJIIIIIJIJJIIIJIJJJI)
        {
            JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IJJIJIJJIJJJJJIJIJIJJJIIIIIJIJIIIJIJJJIJIIIJIJJ(IIJIIIIIJJIIIIJIJJJJJJJJJIIJJJJIIJJJIJJJJIJJIJJ, true, false);
        }
        IJJJIJIJJJIIJIIJIIJIIIJIIIIIJIIJIIJJJIJIJIJIJII(false);
        JIJJIIIIJIJIIIIIIJIIJIJIJIJJJJIIJIIJJJJIIJJIIJI.IIIJJIIJIIIJIIJJJJJJJIJJJJIIJIIJIIIIIJJIJIJJIII = true;
        JIJJJIIJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.JIJJJIIJJIIJIIIJIJIIIJIJIIJIIIJJJJIIIJIJIJIIJII(IIJIIIIIJJIIIIJIJJJJJJJJJIIJJJJIIJJJIJJJJIJJIJJ);
        """,
    )
    return text


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
    # Obfuscated PhotonNetwork / NetworkingPeer (PUN 1.x offline-mode core).
    patch_file("JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ.cs", patch_photon_network)
    patch_file("JJJJJIJJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII.cs", patch_networking_peer)
    patch_file("mCreateServer.cs", patch_create_server)
    patch_file("mPlayerCamera.cs", patch_mplayer_camera)
    patch_file("mOthers.cs", patch_mothers)
    patch_file("mPanelManager.cs", patch_panel_manager)


if __name__ == "__main__":
    main()
