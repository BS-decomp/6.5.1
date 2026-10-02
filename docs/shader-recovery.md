# Block Strike 6.5.1 Shader Recovery Report

All **46** custom project shaders in Block Strike 6.5.1 (which AssetRipper exports as `DummyShaderTextExporter` stubs because Unity 2019.2 strips source ShaderLab text into `SerializedShader` + GLSL ES 3.00 `hlslcc` subprograms) have been reconstructed and verified 1:1 against `tools/shader-extract/`.

Built-in Unity shaders (`Mobile/Unlit (Supports Lightmap)`, `Mobile/VertexLit`, `Mobile/Diffuse`, `Mobile/Particles/*`, `Sprites/Default`, `Skybox/6 Sided`, etc.) reference `Resources/unity_builtin_extra` (`guid: 0000000000000000f000000000000000`) directly in `.mat` files and require no custom `.shader` override.

## Summary by Family

| Family | Count | Location in Project | Notes |
|---|---:|---|---|
| **NGUI** | 25 | `Assets/Resources/shaders/` | 24 classic NGUI shaders + `Unlit/Transparent Colored Cubemap` (new in 6.5.1) |
| **ProBuilder 4.0.5** | 8 | `Assets/Shader/` | `Diffuse Vertex Color`, `Standard Vertex Color`, `Unlit Solid Color`, `UnlitVertexColor`, `EdgePicker`, `FacePicker`, `HideVertices`, `VertexPicker` |
| **MADFINGER** | 6 | `Assets/Shader/` | `Diffuse/Simple`, `Environment/Cube env map`, `Particles/Additive TwoSide`, `Particles/Alpha Blended`, `Transparent/Blinking GodRays`, `Transparent/GodRays` |
| **WarFX (WFX)** | 5 | `Assets/Shader/` | `Additive (Soft) Alpha8`, `Additive Alpha8`, `Multiply Alpha8`, `Scroll/Additive`, `Scroll/Smoke` |
| **Custom** | 2 | `Assets/Shader/` | `Mobile/Unlit/Transparent Color`, `Vertigo/GaussianBlur` |
| **Total** | **46** | | **100% verified against 6.5.1 APK `SerializedShader`** |

## Complete Shader Mapping

| # | Shader Name | Family | Project Asset Path | Canonical Source | APK Ground Truth |
|---:|---|---|---|---|---|
| 1 | `Hidden/ProBuilder/EdgePicker` | ProBuilder | `Assets/Shader/Hidden_ProBuilder_EdgePicker.shader` | `tools/shader-canonical/probuilder/EdgePicker.shader` | `tools/shader-extract/shader_32_Hidden_ProBuilder_EdgePicker.txt` |
| 2 | `Hidden/ProBuilder/FacePicker` | ProBuilder | `Assets/Shader/Hidden_ProBuilder_FacePicker.shader` | `tools/shader-canonical/probuilder/FacePicker.shader` | `tools/shader-extract/shader_45_Hidden_ProBuilder_FacePicker.txt` |
| 3 | `Hidden/ProBuilder/HideVertices` | ProBuilder | `Assets/Shader/Hidden_ProBuilder_HideVertices.shader` | `tools/shader-canonical/probuilder/pb_HideVertices.shader` | `tools/shader-extract/shader_47_Hidden_ProBuilder_HideVertices.txt` |
| 4 | `Hidden/ProBuilder/VertexPicker` | ProBuilder | `Assets/Shader/Hidden_ProBuilder_VertexPicker.shader` | `tools/shader-canonical/probuilder/VertexPicker.shader` | `tools/shader-extract/shader_43_Hidden_ProBuilder_VertexPicker.txt` |
| 5 | `Hidden/Unlit/Premultiplied Colored (TextureClip)` | NGUI | `Assets/Resources/shaders/unlit - premultiplied colored (textureclip).shader` | `tools/shader-canonical/ngui/Unlit - Premultiplied Colored (TextureClip).shader` | `tools/shader-extract/shader_29_Hidden_Unlit_Premultiplied_Colored_TextureClip.txt` |
| 6 | `Hidden/Unlit/Premultiplied Colored 1` | NGUI | `Assets/Resources/shaders/unlit - premultiplied colored 1.shader` | `tools/shader-canonical/ngui/Unlit - Premultiplied Colored 1.shader` | `tools/shader-extract/shader_35_Hidden_Unlit_Premultiplied_Colored_1.txt` |
| 7 | `Hidden/Unlit/Premultiplied Colored 2` | NGUI | `Assets/Resources/shaders/unlit - premultiplied colored 2.shader` | `tools/shader-canonical/ngui/Unlit - Premultiplied Colored 2.shader` | `tools/shader-extract/shader_24_Hidden_Unlit_Premultiplied_Colored_2.txt` |
| 8 | `Hidden/Unlit/Premultiplied Colored 3` | NGUI | `Assets/Resources/shaders/unlit - premultiplied colored 3.shader` | `tools/shader-canonical/ngui/Unlit - Premultiplied Colored 3.shader` | `tools/shader-extract/shader_23_Hidden_Unlit_Premultiplied_Colored_3.txt` |
| 9 | `Hidden/Unlit/Text (TextureClip)` | NGUI | `Assets/Resources/shaders/unlit - text (textureclip).shader` | `tools/shader-canonical/ngui/Unlit - Text (TextureClip).shader` | `tools/shader-extract/shader_53_Hidden_Unlit_Text_TextureClip.txt` |
| 10 | `Hidden/Unlit/Text 1` | NGUI | `Assets/Resources/shaders/unlit - text 1.shader` | `tools/shader-canonical/ngui/Unlit - Text 1.shader` | `tools/shader-extract/shader_37_Hidden_Unlit_Text_1.txt` |
| 11 | `Hidden/Unlit/Text 2` | NGUI | `Assets/Resources/shaders/unlit - text 2.shader` | `tools/shader-canonical/ngui/Unlit - Text 2.shader` | `tools/shader-extract/shader_22_Hidden_Unlit_Text_2.txt` |
| 12 | `Hidden/Unlit/Text 3` | NGUI | `Assets/Resources/shaders/unlit - text 3.shader` | `tools/shader-canonical/ngui/Unlit - Text 3.shader` | `tools/shader-extract/shader_18_Hidden_Unlit_Text_3.txt` |
| 13 | `Hidden/Unlit/Transparent Colored (TextureClip)` | NGUI | `Assets/Resources/shaders/unlit - transparent colored (textureclip).shader` | `tools/shader-canonical/ngui/Unlit - Transparent Colored (TextureClip).shader` | `tools/shader-extract/shader_25_Hidden_Unlit_Transparent_Colored_TextureClip.txt` |
| 14 | `Hidden/Unlit/Transparent Colored 1` | NGUI | `Assets/Resources/shaders/unlit - transparent colored 1.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Colored 1.shader` | `tools/shader-extract/shader_46_Hidden_Unlit_Transparent_Colored_1.txt` |
| 15 | `Hidden/Unlit/Transparent Colored 2` | NGUI | `Assets/Resources/shaders/unlit - transparent colored 2.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Colored 2.shader` | `tools/shader-extract/shader_12_Hidden_Unlit_Transparent_Colored_2.txt` |
| 16 | `Hidden/Unlit/Transparent Colored 3` | NGUI | `Assets/Resources/shaders/unlit - transparent colored 3.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Colored 3.shader` | `tools/shader-extract/shader_30_Hidden_Unlit_Transparent_Colored_3.txt` |
| 17 | `Hidden/Unlit/Transparent Masked 1` | NGUI | `Assets/Resources/shaders/unlit - transparent masked 1.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Masked 1.shader` | `tools/shader-extract/shader_20_Hidden_Unlit_Transparent_Masked_1.txt` |
| 18 | `Hidden/Unlit/Transparent Masked 2` | NGUI | `Assets/Resources/shaders/unlit - transparent masked 2.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Masked 2.shader` | `tools/shader-extract/shader_44_Hidden_Unlit_Transparent_Masked_2.txt` |
| 19 | `Hidden/Unlit/Transparent Masked 3` | NGUI | `Assets/Resources/shaders/unlit - transparent masked 3.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Masked 3.shader` | `tools/shader-extract/shader_16_Hidden_Unlit_Transparent_Masked_3.txt` |
| 20 | `Hidden/Unlit/Transparent Packed 1` | NGUI | `Assets/Resources/shaders/unlit - transparent packed 1.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Packed 1.shader` | `tools/shader-extract/shader_14_Hidden_Unlit_Transparent_Packed_1.txt` |
| 21 | `Hidden/Unlit/Transparent Packed 2` | NGUI | `Assets/Resources/shaders/unlit - transparent packed 2.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Packed 2.shader` | `tools/shader-extract/shader_56_Hidden_Unlit_Transparent_Packed_2.txt` |
| 22 | `Hidden/Unlit/Transparent Packed 3` | NGUI | `Assets/Resources/shaders/unlit - transparent packed 3.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Packed 3.shader` | `tools/shader-extract/shader_49_Hidden_Unlit_Transparent_Packed_3.txt` |
| 23 | `MADFINGER/Diffuse/Simple` | MADFINGER | `Assets/Shader/MADFINGER_Diffuse_Simple.shader` | `tools/shader-canonical/madfinger/MADFINGER-diffuse-simple.shader` | `tools/shader-extract/shader_54_MADFINGER_Diffuse_Simple.txt` |
| 24 | `MADFINGER/Environment/Cube env map` | MADFINGER | `Assets/Shader/MADFINGER_Environment_Cube env map.shader` | `tools/shader-canonical/madfinger/MADFINGER-cube-env-map.shader` | `tools/shader-extract/shader_58_MADFINGER_Environment_Cube_env_map.txt` |
| 25 | `MADFINGER/Particles/Additive TwoSide` | MADFINGER | `Assets/Shader/MADFINGER_Particles_Additive TwoSide.shader` | `tools/shader-canonical/madfinger/MADFINGER-particles-additive-twoside.shader` | `tools/shader-extract/shader_48_MADFINGER_Particles_Additive_TwoSide.txt` |
| 26 | `MADFINGER/Particles/Alpha Blended` | MADFINGER | `Assets/Shader/MADFINGER_Particles_Alpha Blended.shader` | `tools/shader-canonical/madfinger/MADFINGER-particles-alpha-blended.shader` | `tools/shader-extract/shader_36_MADFINGER_Particles_Alpha_Blended.txt` |
| 27 | `MADFINGER/Transparent/Blinking GodRays` | MADFINGER | `Assets/Shader/MADFINGER_Transparent_Blinking GodRays.shader` | `tools/shader-canonical/madfinger/MADFINGER-blinking-god-rays.shader` | `tools/shader-extract/shader_60_MADFINGER_Transparent_Blinking_GodRays.txt` |
| 28 | `MADFINGER/Transparent/GodRays` | MADFINGER | `Assets/Shader/MADFINGER_Transparent_GodRays.shader` | `tools/shader-canonical/madfinger/MADFINGER-god-rays.shader` | `tools/shader-extract/shader_61_MADFINGER_Transparent_GodRays.txt` |
| 29 | `Mobile/Unlit/Transparent Color` | Custom | `Assets/Shader/Mobile_Unlit_Transparent Color.shader` | `tools/shader-canonical/custom/Mobile-Unlit-Transparent-Color.shader` | `tools/shader-extract/shader_42_Mobile_Unlit_Transparent_Color.txt` |
| 30 | `ProBuilder/Diffuse Vertex Color` | ProBuilder | `Assets/Shader/ProBuilder_Diffuse Vertex Color.shader` | `tools/shader-canonical/probuilder/DiffuseVertexColor.shader` | `tools/shader-extract/shader_33_ProBuilder_Diffuse_Vertex_Color.txt` |
| 31 | `ProBuilder/Standard Vertex Color` | ProBuilder | `Assets/Shader/ProBuilder_Standard Vertex Color.shader` | `tools/shader-canonical/probuilder/StandardVertexColor.shader` | `tools/shader-extract/shader_15_ProBuilder_Standard_Vertex_Color.txt` |
| 32 | `ProBuilder/Unlit Solid Color` | ProBuilder | `Assets/Shader/ProBuilder_Unlit Solid Color.shader` | `tools/shader-canonical/probuilder/UnlitSolidColor.shader` | `tools/shader-extract/shader_17_ProBuilder_Unlit_Solid_Color.txt` |
| 33 | `ProBuilder/UnlitVertexColor` | ProBuilder | `Assets/Shader/ProBuilder_UnlitVertexColor.shader` | `tools/shader-canonical/probuilder/pb_UnlitVertexColor.shader` | `tools/shader-extract/shader_21_ProBuilder_UnlitVertexColor.txt` |
| 34 | `Unlit/Premultiplied Colored` | NGUI | `Assets/Resources/shaders/unlit - premultiplied colored.shader` | `tools/shader-canonical/ngui/Unlit - Premultiplied Colored.shader` | `tools/shader-extract/shader_52_Unlit_Premultiplied_Colored.txt` |
| 35 | `Unlit/Text` | NGUI | `Assets/Resources/shaders/unlit - text.shader` | `tools/shader-canonical/ngui/Unlit - Text.shader` | `tools/shader-extract/shader_28_Unlit_Text.txt` |
| 36 | `Unlit/Transparent Colored` | NGUI | `Assets/Resources/shaders/unlit - transparent colored.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Colored.shader` | `tools/shader-extract/shader_51_Unlit_Transparent_Colored.txt` |
| 37 | `Unlit/Transparent Colored (Packed) (TextureClip)` | NGUI | `Assets/Resources/shaders/unlit - transparent colored (packed) (textureclip).shader` | `tools/shader-canonical/ngui/Unlit - Transparent Colored (Packed) (TextureClip).shader` | `tools/shader-extract/shader_50_Unlit_Transparent_Colored_Packed_TextureClip.txt` |
| 38 | `Unlit/Transparent Colored Cubemap` | NGUI | `Assets/Resources/shaders/unlit - transparent colored cubemap.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Colored Cubemap.shader` | `tools/shader-extract/shader_11_Unlit_Transparent_Colored_Cubemap.txt` |
| 39 | `Unlit/Transparent Masked` | NGUI | `Assets/Resources/shaders/unlit - transparent masked.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Masked.shader` | `tools/shader-extract/shader_34_Unlit_Transparent_Masked.txt` |
| 40 | `Unlit/Transparent Packed` | NGUI | `Assets/Resources/shaders/unlit - transparent packed.shader` | `tools/shader-canonical/ngui/Unlit - Transparent Packed.shader` | `tools/shader-extract/shader_55_Unlit_Transparent_Packed.txt` |
| 41 | `Vertigo/GaussianBlur` | Custom | `Assets/Shader/Vertigo_GaussianBlur.shader` | `tools/shader-canonical/custom/Vertigo-GaussianBlur.shader` | `tools/shader-extract/shader_59_Vertigo_GaussianBlur.txt` |
| 42 | `WFX/Additive (Soft) Alpha8` | WarFX | `Assets/Shader/WFX_Additive (Soft) Alpha8.shader` | `tools/shader-canonical/wfx/WFX-Additive-Soft-Alpha8.shader` | `tools/shader-extract/shader_31_WFX_Additive_Soft_Alpha8.txt` |
| 43 | `WFX/Additive Alpha8` | WarFX | `Assets/Shader/WFX_Additive Alpha8.shader` | `tools/shader-canonical/wfx/WFX-Additive-Alpha8.shader` | `tools/shader-extract/shader_27_WFX_Additive_Alpha8.txt` |
| 44 | `WFX/Multiply Alpha8` | WarFX | `Assets/Shader/WFX_Multiply Alpha8.shader` | `tools/shader-canonical/wfx/WFX-Multiply-Alpha8.shader` | `tools/shader-extract/shader_19_WFX_Multiply_Alpha8.txt` |
| 45 | `WFX/Scroll/Additive` | WarFX | `Assets/Shader/WFX_Scroll_Additive.shader` | `tools/shader-canonical/wfx/WFX-Scroll-Additive.shader` | `tools/shader-extract/shader_26_WFX_Scroll_Additive.txt` |
| 46 | `WFX/Scroll/Smoke` | WarFX | `Assets/Shader/WFX_Scroll_Smoke.shader` | `tools/shader-canonical/wfx/WFX-Scroll-Smoke.shader` | `tools/shader-extract/shader_13_WFX_Scroll_Smoke.txt` |
