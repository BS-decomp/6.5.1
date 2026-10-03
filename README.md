# BS-decomp / Block Strike 6.5.1

Complete 1:1 Unity project reconstruction of **Block Strike 6.5.1** (`com.rexetstudio.blockstrike`, versionCode `2492`), originally built on Unity `2019.2.3f1` (ARMv7 IL2CPP) and ported to **Unity 2021.3.45f2 LTS**.

## Repository Structure

- `client/` — Full reconstructed Unity project (`Unity 2021.3.45f2 LTS`). Open this directory directly in Unity Hub / Unity Editor.
- `original/apk/` — Ground-truth Android package (`com.rexetstudio.blockstrike_6.5.1_2492.apk`, on `main`).
- `tools/` — Deterministic recovery, patching, and verification scripts:
  - `extract_apk_shader_texts.py` & `shader-extract/` — Ground-truth `SerializedShader` and GLSL ES 3.00 (`#version 300 es`) subprogram dumps from the 6.5.1 APK.
  - `shader-canonical/` & `build_shader_recovery.py` — 46 canonical ShaderLab `.shader` sources verified 1:1 against APK shader metadata (`tools/shader-recovery/inventory.json`).
  - `audit_static_batches.py` & `build_geometry_manifests.py` — Scene-by-scene static batching audit and recovery manifests (`tools/geometry-recovery/`).
  - `recover_static_meshes.py` — Offline static-batch mesh separator (`4,846` local-space meshes across `70` scenes in `client/Assets/RecoveredGeometry/`), `LightingData` `uvMesh` updater, `MeshAtlas` disabler, and `NaN`/`Inf` SH ambient probe sanitizer.
  - `fix_scripts_for_unity2021.py` — Unity `2021.3.45f2 LTS` Roslyn compatibility patcher for IL2CPP + Beebyte Obfuscator 2.7.1 decompiled scripts and plugins.
  - `il2cpp_inspect.py` — Fast ARMv7 IL2CPP disassembler & metadata resolver for `libil2cpp.so` + `global-metadata.dat` (types, fields, method RVAs, metadata-usage annotation).
  - `build_method_inventory.py` — Deterministic IL2CPP method/body inventory: ARMv7 body classification, static call graph (BL/B/fnptr/MethodRef/TypeInfo closure), scene-root reachability, exported-C#-stub detection, and a ranked lost-implementation worklist (`tools/method-inventory/`, [`docs/method-inventory.md`](docs/method-inventory.md)).
  - `reconstruct_651_scripts.py` — Verified runtime-slice reconstruction of decompiled method bodies (boot chain, GDPR, offline room flow, NGUI serialized-state accessors), guarded against stub regression by `tools/method-inventory/restored_methods.json`.
  - `verify_client_project.py` — End-to-end integrity verifier for `client/` (including the restored-method regression guard).
  - `unity-editor/BlockStrikeGeometryRecovery.cs` — In-Editor menu commands (`Tools/Block Strike/Geometry Recovery/...`).
- `docs/` — Technical audits and recovery reports:
  - [`docs/export-status.md`](docs/export-status.md)
  - [`docs/method-inventory.md`](docs/method-inventory.md)
  - [`docs/script-reconstruction.md`](docs/script-reconstruction.md)
  - [`docs/shader-recovery.md`](docs/shader-recovery.md)
  - [`docs/static-batch-audit.md`](docs/static-batch-audit.md)
  - [`docs/geometry-recovery.md`](docs/geometry-recovery.md)

## Recovery Summary

| Area | Status | Details |
| --- | --- | --- |
| **Target Editor** | `2021.3.45f2 LTS` | Configured in `client/ProjectSettings/ProjectVersion.txt` and `client/Packages/manifest.json` (`com.unity.ugui: 1.0.0`). |
| **Scenes & Maps** | `74 / 74` | All 4 core scenes (`AwakeScene`, `GDPR`, `Logo`, `Menu`) and 70 playable maps in `client/Assets/Levels/`. |
| **Static-Batch Geometry** | `4,846 / 4,846` | 100% (`6,192 / 6,192` submeshes) separated from `Combined Mesh (root: scene)` into local-space `.asset` meshes (`client/Assets/RecoveredGeometry/<Scene>/Renderer-<id>.asset`) with UV1 un-transformed (`1.69e-7` max error vs `pb_Mesh` colliders). |
| **Lightmaps & LightingData** | `73 PNGs / 100 Assets` | Lightmaps exported as `.png` (`LightmapTextureExportFormat=Image`), `3,187` `LightingData` `uvMesh` links rewired, and `26` `NaN`/`Inf` SH ambient probes sanitized. |
| **Custom Shaders** | `46 / 46` | All 25 NGUI (`Assets/Resources/shaders/`), 8 ProBuilder 4.0.5, 6 MADFINGER, 5 WarFX, and 2 custom shaders (`Assets/Shader/`) restored; `0` `DummyShaderTextExporter` stubs remain. |
| **Scripts & Plugins** | `907 C# / 17 DLLs` | Patched for Unity `2021.3.45f2` Roslyn (`[SpecialName]`, `[PreserveSig]` -> `[DllImport]`, `op_Implicit`, `INGUIAtlas`/`INGUIFont`/`UIRect`/`IList`/`IDictionary` decompilation fixes; legacy `UnityEngine.UI.dll` removed while keeping `Unity.ProBuilder.dll` for `3,750` `ProBuilderMesh` instances). |

## Verification

To run the offline verification suite against `client/`:

```bash
python3 tools/verify_client_project.py --client-dir client
```
