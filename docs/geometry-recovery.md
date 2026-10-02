# Static-Batch Geometry Recovery (`Block Strike 6.5.1`)

## Architecture

In the Unity `2019.2.3f1` release APK (`com.rexetstudio.blockstrike_6.5.1_2492.apk`),
`70` of the `74` scenes in `Assets/Levels/` use static batching:

- **`4,846` static-batched `MeshRenderer` components** store their submesh slices in `m_StaticBatchInfo: {firstSubMesh, subMeshCount}`.
- Their sibling `MeshFilter.m_Mesh` references one of the `70` `Assets/Mesh/Combined Mesh (root_ scene)*.asset` files (`6,192` total submeshes).
- **`3,187` lightmapped static-batched `MeshRenderer`s** have their `lightmapIndex` and `lightmapST` (`scale.xy`, `offset.zw`) stored in the scene's `LightingData*.asset` (`m_LightmappedRendererData` / `m_LightmappedRendererDataIDs`), while their combined mesh `UV1` (`Channel 5`) has `uv1_combined = uv1_local * lightmapST.xy + lightmapST.zw` pre-baked into the vertex stream.
- **`26` `LightingData*.asset` files** also contain uninitialized `NaN` / `Infinity` / `1e+28` floats in `m_BakedAmbientProbeInLinear` (because those scenes use flat ambient color `m_AmbientMode: 3`), which must be sanitized to `0` so Unity `2021.3.45f2` YAML parsing and SH ambient shaders do not produce `NaN` lighting.

## Recovery Pipeline

1. **Audit (`tools/audit_static_batches.py`)**:
   Verifies all `74` scenes and confirms `100%` submesh coverage (`6,192 / 6,192` submeshes across `70` `Combined Mesh` assets, `0` missing `MeshFilter`s, `0` out-of-range submeshes, `0` overlapping submeshes).
2. **Manifest Generation (`tools/build_geometry_manifests.py`)**:
   Emits `tools/geometry-recovery/manifest.json` and `70` per-scene manifests in `tools/geometry-recovery/scenes/<scene_slug>.json` containing exact transform chains, submesh ranges, material GUIDs, `LightingData` `lightmapST` vectors, and deterministic output mesh GUIDs.
3. **Offline Deterministic Mesh & Scene Recovery (`tools/recover_static_meshes.py`)**:
   - Extracts each renderer's `[firstSubMesh, firstSubMesh + subMeshCount)` from the scene's `Combined Mesh (root_ scene)*.asset`.
   - Transforms world-space vertex positions (`Channel 0`) back into the `GameObject`'s local space (`v_local = worldToLocalMatrix * v_world`).
   - Transforms world-space vertex normals (`Channel 1`, `Float32` or `Float16`) into local space via the inverse-transpose matrix (`normalize(transpose(localToWorldMatrix_3x3) * n_world)`).
   - Reverses triangle winding `(i0, i1, i2) -> (i0, i2, i1)` when `det(localToWorldMatrix) < 0` (odd negative scale) so local-space face winding matches Unity's negative-scale rasterizer culling.
   - Un-transforms lightmap `UV1` (`Channel 5`) via `uv1_local = (uv1_combined - lightmapST.zw) / lightmapST.xy` for all lightmapped static-batched renderers, restoring normalized `[0, 1]` chart UVs to within `1 ULP` (`1.69e-7`) of original ProBuilder meshes.
   - Writes `Assets/RecoveredGeometry/<SceneName>/Renderer-<rendererId>.asset` + `.meta`, updates `MeshFilter.m_Mesh`, resets `m_StaticBatchInfo` to `{firstSubMesh: 0, subMeshCount: 0}`, disables the `24` static-batched `MeshAtlas` components (`m_Enabled: 0`), updates `LightingData*.asset` `uvMesh` references, and sanitizes `NaN`/`Inf` SH ambient probes.
4. **Unity 2021.3.45f2 Editor Tool (`client/Assets/Editor/BlockStrikeGeometryRecovery.cs`)**:
   Provides `Tools/Block Strike/Geometry Recovery/Recover All Scenes` and `Verify Recovered Scenes` inside the Unity Editor.

## Scene Manifest Index

| Scene | Manifest | Static Renderers | SubMeshes | Lightmapped |
|---|---|---:|---:|---:|
| `Better` | `tools/geometry-recovery/scenes/better.json` | 177 | 342 | 175 |
| `Eazy` | `tools/geometry-recovery/scenes/eazy.json` | 7 | 7 | 4 |
| `Fall` | `tools/geometry-recovery/scenes/fall.json` | 5 | 5 | 3 |
| `Harder` | `tools/geometry-recovery/scenes/harder.json` | 6 | 6 | 3 |
| `Jumpout` | `tools/geometry-recovery/scenes/jumpout.json` | 8 | 8 | 6 |
| `Speed` | `tools/geometry-recovery/scenes/speed.json` | 81 | 83 | 79 |
| `Stronger` | `tools/geometry-recovery/scenes/stronger.json` | 101 | 276 | 97 |
| `Trainer` | `tools/geometry-recovery/scenes/trainer.json` | 251 | 505 | 249 |
| `Various` | `tools/geometry-recovery/scenes/various.json` | 217 | 311 | 185 |
| `Ciald` | `tools/geometry-recovery/scenes/ciald.json` | 47 | 63 | 43 |
| `Delay` | `tools/geometry-recovery/scenes/delay.json` | 48 | 71 | 40 |
| `Firati` | `tools/geometry-recovery/scenes/firati.json` | 38 | 48 | 36 |
| `Fractal` | `tools/geometry-recovery/scenes/fractal.json` | 24 | 30 | 22 |
| `Grade` | `tools/geometry-recovery/scenes/grade.json` | 13 | 20 | 10 |
| `Jacuda` | `tools/geometry-recovery/scenes/jacuda.json` | 16 | 22 | 13 |
| `Journey` | `tools/geometry-recovery/scenes/journey.json` | 61 | 75 | 56 |
| `Long` | `tools/geometry-recovery/scenes/long.json` | 28 | 29 | 25 |
| `Simple` | `tools/geometry-recovery/scenes/simple.json` | 74 | 114 | 64 |
| `Stander` | `tools/geometry-recovery/scenes/stander.json` | 24 | 34 | 22 |
| `Coliseum` | `tools/geometry-recovery/scenes/coliseum.json` | 151 | 176 | 124 |
| `Labyrinth` | `tools/geometry-recovery/scenes/labyrinth.json` | 139 | 141 | 96 |
| `Pyramids` | `tools/geometry-recovery/scenes/pyramids.json` | 216 | 266 | 210 |
| `Hill` | `tools/geometry-recovery/scenes/hill.json` | 45 | 47 | 39 |
| `Military Range` | `tools/geometry-recovery/scenes/military_range.json` | 36 | 38 | 30 |
| `Rise` | `tools/geometry-recovery/scenes/rise.json` | 53 | 55 | 51 |
| `100Traps` | `tools/geometry-recovery/scenes/100traps.json` | 3 | 4 | 1 |
| `50Traps` | `tools/geometry-recovery/scenes/50traps.json` | 3 | 4 | 1 |
| `BlockParty` | `tools/geometry-recovery/scenes/blockparty.json` | 4 | 5 | 1 |
| `Football` | `tools/geometry-recovery/scenes/football.json` | 4 | 11 | 2 |
| `Hot Knife` | `tools/geometry-recovery/scenes/hot_knife.json` | 55 | 73 | 53 |
| `Push` | `tools/geometry-recovery/scenes/push.json` | 225 | 226 | 1 |
| `Spleef` | `tools/geometry-recovery/scenes/spleef.json` | 736 | 737 | 1 |
| `Tennis` | `tools/geometry-recovery/scenes/tennis.json` | 38 | 47 | 21 |
| `100HP` | `tools/geometry-recovery/scenes/100hp.json` | 50 | 66 | 45 |
| `3000` | `tools/geometry-recovery/scenes/3000.json` | 27 | 27 | 18 |
| `Aim` | `tools/geometry-recovery/scenes/aim.json` | 19 | 25 | 16 |
| `Apache` | `tools/geometry-recovery/scenes/apache.json` | 21 | 29 | 18 |
| `Cache` | `tools/geometry-recovery/scenes/cache.json` | 67 | 77 | 62 |
| `Carnage` | `tools/geometry-recovery/scenes/carnage.json` | 20 | 28 | 17 |
| `Casta` | `tools/geometry-recovery/scenes/casta.json` | 18 | 18 | 13 |
| `Compact` | `tools/geometry-recovery/scenes/compact.json` | 20 | 25 | 17 |
| `District` | `tools/geometry-recovery/scenes/district.json` | 57 | 71 | 52 |
| `Dust` | `tools/geometry-recovery/scenes/dust.json` | 67 | 79 | 64 |
| `Dust 2` | `tools/geometry-recovery/scenes/dust_2.json` | 49 | 56 | 45 |
| `Dust 2x2` | `tools/geometry-recovery/scenes/dust_2x2.json` | 54 | 65 | 52 |
| `Factory` | `tools/geometry-recovery/scenes/factory.json` | 40 | 46 | 35 |
| `India` | `tools/geometry-recovery/scenes/india.json` | 19 | 25 | 17 |
| `Lenstown` | `tools/geometry-recovery/scenes/lenstown.json` | 13 | 19 | 12 |
| `Mirage` | `tools/geometry-recovery/scenes/mirage.json` | 93 | 109 | 87 |
| `Nauts` | `tools/geometry-recovery/scenes/nauts.json` | 57 | 63 | 53 |
| `Office` | `tools/geometry-recovery/scenes/office.json` | 71 | 71 | 65 |
| `Pool` | `tools/geometry-recovery/scenes/pool.json` | 17 | 20 | 15 |
| `Range` | `tools/geometry-recovery/scenes/range.json` | 18 | 20 | 15 |
| `Rast` | `tools/geometry-recovery/scenes/rast.json` | 19 | 24 | 17 |
| `Sector` | `tools/geometry-recovery/scenes/sector.json` | 42 | 50 | 39 |
| `Skyline` | `tools/geometry-recovery/scenes/skyline.json` | 43 | 56 | 38 |
| `Storage` | `tools/geometry-recovery/scenes/storage.json` | 31 | 31 | 24 |
| `Tecaza` | `tools/geometry-recovery/scenes/tecaza.json` | 23 | 26 | 19 |
| `Turbine` | `tools/geometry-recovery/scenes/turbine.json` | 36 | 36 | 29 |
| `Upload` | `tools/geometry-recovery/scenes/upload.json` | 17 | 21 | 14 |
| `Villa` | `tools/geometry-recovery/scenes/villa.json` | 43 | 50 | 32 |
| `Deep` | `tools/geometry-recovery/scenes/deep.json` | 37 | 38 | 35 |
| `Jet` | `tools/geometry-recovery/scenes/jet.json` | 232 | 258 | 74 |
| `MainTutorial` | `tools/geometry-recovery/scenes/maintutorial.json` | 22 | 26 | 10 |
| `Shooting Range` | `tools/geometry-recovery/scenes/shooting_range.json` | 97 | 160 | 94 |
| `Battleforce` | `tools/geometry-recovery/scenes/battleforce.json` | 65 | 91 | 35 |
| `Cord (Beta)` | `tools/geometry-recovery/scenes/cord_beta.json` | 110 | 143 | 79 |
| `Escape` | `tools/geometry-recovery/scenes/escape.json` | 70 | 83 | 28 |
| `Playground` | `tools/geometry-recovery/scenes/playground.json` | 171 | 219 | 120 |
| `Upland` | `tools/geometry-recovery/scenes/upland.json` | 57 | 62 | 19 |
