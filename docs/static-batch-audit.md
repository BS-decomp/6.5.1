# Static-Batch Geometry Audit (`Block Strike 6.5.1`)

## Overview

- **Source APK Unity Version**: `2019.2.3f1`
- **Target Unity Editor Version**: `2021.3.45f2`
- **Total Scenes (`Assets/Levels/**/*.unity`)**: `74`
- **Scenes with Static-Batched Geometry**: `70`
- **Scenes without Static-Batched Geometry**: `4` (`Assets/Levels/AwakeScene.unity, Assets/Levels/GDPR.unity, Assets/Levels/Logo.unity, Assets/Levels/Menu.unity`)
- **Total `Combined Mesh (root_ scene)*.asset` Files**: `70`
- **Total Static-Batched `MeshRenderer`s**: `4846`
- **Total Submeshes in Combined Meshes**: `6192` (`6192` referenced)
- **Lightmapped Static-Batched `MeshRenderer`s**: `3187`
- **Static-Batched `GameObject`s with Original `pb_Mesh` on `MeshCollider`**: `1226`
- **Static-Batched `GameObject`s with `MeshAtlas`**: `24`
- **Missing `MeshFilter` Components**: `0`
- **Out-of-Range Submeshes**: `0`
- **Overlapping Submeshes**: `0`

## Per-Scene Static Batch Summary

| Scene | Path | Combined Mesh Asset | Static Renderers | SubMeshes (Ref / Total) | Lightmapped | MeshCollider | MeshAtlas |
|---|---|---|---:|---:|---:|---:|---:|
| `Better` | `Assets/Levels/Maps/BunnyHop/Better/Better.unity` | `Combined Mesh (root_ scene)_44.asset` | 177 | 342 / 342 | 175 | 20 | 0 |
| `Eazy` | `Assets/Levels/Maps/BunnyHop/Eazy/Eazy.unity` | `Combined Mesh (root_ scene)_43.asset` | 7 | 7 / 7 | 4 | 3 | 0 |
| `Fall` | `Assets/Levels/Maps/BunnyHop/Fall/Fall.unity` | `Combined Mesh (root_ scene)_42.asset` | 5 | 5 / 5 | 3 | 0 | 0 |
| `Harder` | `Assets/Levels/Maps/BunnyHop/Harder/Harder.unity` | `Combined Mesh (root_ scene)_41.asset` | 6 | 6 / 6 | 3 | 2 | 0 |
| `Jumpout` | `Assets/Levels/Maps/BunnyHop/Jumpout/Jumpout.unity` | `Combined Mesh (root_ scene)_40.asset` | 8 | 8 / 8 | 6 | 3 | 0 |
| `Speed` | `Assets/Levels/Maps/BunnyHop/Speed/Speed.unity` | `Combined Mesh (root_ scene)_39.asset` | 81 | 83 / 83 | 79 | 2 | 0 |
| `Stronger` | `Assets/Levels/Maps/BunnyHop/Stronger/Stronger.unity` | `Combined Mesh (root_ scene)_37.asset` | 101 | 276 / 276 | 97 | 9 | 0 |
| `Trainer` | `Assets/Levels/Maps/BunnyHop/Trainer/Trainer.unity` | `Combined Mesh (root_ scene)_36.asset` | 251 | 505 / 505 | 249 | 12 | 0 |
| `Various` | `Assets/Levels/Maps/BunnyHop/Various/Various.unity` | `Combined Mesh (root_ scene)_35.asset` | 217 | 311 / 311 | 185 | 33 | 0 |
| `Ciald` | `Assets/Levels/Maps/DeathRun/Ciald/Ciald.unity` | `Combined Mesh (root_ scene)_34.asset` | 47 | 63 / 63 | 43 | 26 | 0 |
| `Delay` | `Assets/Levels/Maps/DeathRun/Delay/Delay.unity` | `Combined Mesh (root_ scene)_33.asset` | 48 | 71 / 71 | 40 | 14 | 0 |
| `Firati` | `Assets/Levels/Maps/DeathRun/Firati/Firati.unity` | `Combined Mesh (root_ scene)_32.asset` | 38 | 48 / 48 | 36 | 11 | 0 |
| `Fractal` | `Assets/Levels/Maps/DeathRun/Fractal/Fractal.unity` | `Combined Mesh (root_ scene)_31.asset` | 24 | 30 / 30 | 22 | 10 | 0 |
| `Grade` | `Assets/Levels/Maps/DeathRun/Grade/Grade.unity` | `Combined Mesh (root_ scene)_30.asset` | 13 | 20 / 20 | 10 | 2 | 0 |
| `Jacuda` | `Assets/Levels/Maps/DeathRun/Jacuda/Jacuda.unity` | `Combined Mesh (root_ scene)_29.asset` | 16 | 22 / 22 | 13 | 7 | 0 |
| `Journey` | `Assets/Levels/Maps/DeathRun/Journey/Journey.unity` | `Combined Mesh (root_ scene)_28.asset` | 61 | 75 / 75 | 56 | 25 | 0 |
| `Long` | `Assets/Levels/Maps/DeathRun/Long/Long.unity` | `Combined Mesh (root_ scene)_26.asset` | 28 | 29 / 29 | 25 | 14 | 0 |
| `Simple` | `Assets/Levels/Maps/DeathRun/Simple/Simple.unity` | `Combined Mesh (root_ scene)_25.asset` | 74 | 114 / 114 | 64 | 35 | 0 |
| `Stander` | `Assets/Levels/Maps/DeathRun/Stander/Stander.unity` | `Combined Mesh (root_ scene)_24.asset` | 24 | 34 / 34 | 22 | 12 | 0 |
| `Coliseum` | `Assets/Levels/Maps/HungerGames/Coliseum/Coliseum.unity` | `Combined Mesh (root_ scene)_23.asset` | 151 | 176 / 176 | 124 | 65 | 0 |
| `Labyrinth` | `Assets/Levels/Maps/HungerGames/Labyrinth/Labyrinth.unity` | `Combined Mesh (root_ scene)_22.asset` | 139 | 141 / 141 | 96 | 51 | 0 |
| `Pyramids` | `Assets/Levels/Maps/HungerGames/Pyramids/Pyramids.unity` | `Combined Mesh (root_ scene)_21.asset` | 216 | 266 / 266 | 210 | 78 | 0 |
| `Hill` | `Assets/Levels/Maps/Hunter/Hill/Hill.unity` | `Combined Mesh (root_ scene)_20.asset` | 45 | 47 / 47 | 39 | 2 | 4 |
| `Military Range` | `Assets/Levels/Maps/Hunter/Military Range/Military Range.unity` | `Combined Mesh (root_ scene)_19.asset` | 36 | 38 / 38 | 30 | 2 | 4 |
| `Rise` | `Assets/Levels/Maps/Hunter/Rise/Rise.unity` | `Combined Mesh (root_ scene)_18.asset` | 53 | 55 / 55 | 51 | 7 | 0 |
| `100Traps` | `Assets/Levels/Maps/MiniGames/100Traps/100Traps.unity` | `Combined Mesh (root_ scene)_15.asset` | 3 | 4 / 4 | 1 | 1 | 0 |
| `50Traps` | `Assets/Levels/Maps/MiniGames/50Traps/50Traps.unity` | `Combined Mesh (root_ scene)_17.asset` | 3 | 4 / 4 | 1 | 1 | 0 |
| `BlockParty` | `Assets/Levels/Maps/MiniGames/BlockParty/BlockParty.unity` | `Combined Mesh (root_ scene)_14.asset` | 4 | 5 / 5 | 1 | 1 | 0 |
| `Football` | `Assets/Levels/Maps/MiniGames/Football/Sunshine/Football.unity` | `Combined Mesh (root_ scene)_13.asset` | 4 | 11 / 11 | 2 | 1 | 0 |
| `Hot Knife` | `Assets/Levels/Maps/MiniGames/Hot Knife/Hot Knife.unity` | `Combined Mesh (root_ scene)_12.asset` | 55 | 73 / 73 | 53 | 51 | 0 |
| `Push` | `Assets/Levels/Maps/MiniGames/Push/Push.unity` | `Combined Mesh (root_ scene)_11.asset` | 225 | 226 / 226 | 1 | 1 | 0 |
| `Spleef` | `Assets/Levels/Maps/MiniGames/Spleef/Spleef.unity` | `Combined Mesh (root_ scene)_10.asset` | 736 | 737 / 737 | 1 | 1 | 0 |
| `Tennis` | `Assets/Levels/Maps/MiniGames/Tennis/Tennis.unity` | `Combined Mesh (root_ scene)_9.asset` | 38 | 47 / 47 | 21 | 3 | 0 |
| `100HP` | `Assets/Levels/Maps/Others/100HP/100HP.unity` | `Combined Mesh (root_ scene).asset` | 50 | 66 / 66 | 45 | 23 | 0 |
| `3000` | `Assets/Levels/Maps/Others/3000/3000.unity` | `Combined Mesh (root_ scene)_68.asset` | 27 | 27 / 27 | 18 | 12 | 0 |
| `Aim` | `Assets/Levels/Maps/Others/Aim/Aim.unity` | `Combined Mesh (root_ scene)_67.asset` | 19 | 25 / 25 | 16 | 11 | 0 |
| `Apache` | `Assets/Levels/Maps/Others/Apache/Apache.unity` | `Combined Mesh (root_ scene)_66.asset` | 21 | 29 / 29 | 18 | 11 | 0 |
| `Cache` | `Assets/Levels/Maps/Others/Cache/Cache.unity` | `Combined Mesh (root_ scene)_65.asset` | 67 | 77 / 77 | 62 | 27 | 0 |
| `Carnage` | `Assets/Levels/Maps/Others/Carnage/Carnage.unity` | `Combined Mesh (root_ scene)_64.asset` | 20 | 28 / 28 | 17 | 9 | 0 |
| `Casta` | `Assets/Levels/Maps/Others/Casta/Casta.unity` | `Combined Mesh (root_ scene)_63.asset` | 18 | 18 / 18 | 13 | 5 | 0 |
| `Compact` | `Assets/Levels/Maps/Others/Compact/Compact.unity` | `Combined Mesh (root_ scene)_62.asset` | 20 | 25 / 25 | 17 | 4 | 0 |
| `District` | `Assets/Levels/Maps/Others/District/District.unity` | `Combined Mesh (root_ scene)_61.asset` | 57 | 71 / 71 | 52 | 18 | 0 |
| `Dust` | `Assets/Levels/Maps/Others/Dust/Dust.unity` | `Combined Mesh (root_ scene)_16.asset` | 67 | 79 / 79 | 64 | 27 | 0 |
| `Dust 2` | `Assets/Levels/Maps/Others/Dust 2/Dust 2.unity` | `Combined Mesh (root_ scene)_5.asset` | 49 | 56 / 56 | 45 | 9 | 0 |
| `Dust 2x2` | `Assets/Levels/Maps/Others/Dust 2x2/Dust 2x2.unity` | `Combined Mesh (root_ scene)_0.asset` | 54 | 65 / 65 | 52 | 19 | 0 |
| `Factory` | `Assets/Levels/Maps/Others/Factory/Factory.unity` | `Combined Mesh (root_ scene)_60.asset` | 40 | 46 / 46 | 35 | 15 | 0 |
| `India` | `Assets/Levels/Maps/Others/India/India.unity` | `Combined Mesh (root_ scene)_59.asset` | 19 | 25 / 25 | 17 | 7 | 0 |
| `Lenstown` | `Assets/Levels/Maps/Others/Lenstown/Lenstown.unity` | `Combined Mesh (root_ scene)_58.asset` | 13 | 19 / 19 | 12 | 7 | 0 |
| `Mirage` | `Assets/Levels/Maps/Others/Mirage/Mirage.unity` | `Combined Mesh (root_ scene)_57.asset` | 93 | 109 / 109 | 87 | 34 | 0 |
| `Nauts` | `Assets/Levels/Maps/Others/Nauts/Nauts.unity` | `Combined Mesh (root_ scene)_56.asset` | 57 | 63 / 63 | 53 | 15 | 0 |
| `Office` | `Assets/Levels/Maps/Others/Office/Office.unity` | `Combined Mesh (root_ scene)_55.asset` | 71 | 71 / 71 | 65 | 23 | 0 |
| `Pool` | `Assets/Levels/Maps/Others/Pool/Pool.unity` | `Combined Mesh (root_ scene)_54.asset` | 17 | 20 / 20 | 15 | 8 | 0 |
| `Range` | `Assets/Levels/Maps/Others/Range/Range.unity` | `Combined Mesh (root_ scene)_53.asset` | 18 | 20 / 20 | 15 | 6 | 0 |
| `Rast` | `Assets/Levels/Maps/Others/Rast/Rast.unity` | `Combined Mesh (root_ scene)_52.asset` | 19 | 24 / 24 | 17 | 7 | 0 |
| `Sector` | `Assets/Levels/Maps/Others/Sector/Sector.unity` | `Combined Mesh (root_ scene)_51.asset` | 42 | 50 / 50 | 39 | 10 | 0 |
| `Skyline` | `Assets/Levels/Maps/Others/Skyline/Skyline.unity` | `Combined Mesh (root_ scene)_50.asset` | 43 | 56 / 56 | 38 | 19 | 0 |
| `Storage` | `Assets/Levels/Maps/Others/Storage/Storage.unity` | `Combined Mesh (root_ scene)_49.asset` | 31 | 31 / 31 | 24 | 14 | 0 |
| `Tecaza` | `Assets/Levels/Maps/Others/Tecaza/Tecaza.unity` | `Combined Mesh (root_ scene)_48.asset` | 23 | 26 / 26 | 19 | 11 | 0 |
| `Turbine` | `Assets/Levels/Maps/Others/Turbine/Turbine.unity` | `Combined Mesh (root_ scene)_47.asset` | 36 | 36 / 36 | 29 | 21 | 0 |
| `Upload` | `Assets/Levels/Maps/Others/Upload/Upload.unity` | `Combined Mesh (root_ scene)_46.asset` | 17 | 21 / 21 | 14 | 6 | 0 |
| `Villa` | `Assets/Levels/Maps/Others/Villa/Villa.unity` | `Combined Mesh (root_ scene)_45.asset` | 43 | 50 / 50 | 32 | 14 | 0 |
| `Deep` | `Assets/Levels/Maps/Surf/Deep/Deep.unity` | `Combined Mesh (root_ scene)_7.asset` | 37 | 38 / 38 | 35 | 35 | 0 |
| `Jet` | `Assets/Levels/Maps/Surf/Jet/Jet.unity` | `Combined Mesh (root_ scene)_8.asset` | 232 | 258 / 258 | 74 | 50 | 0 |
| `MainTutorial` | `Assets/Levels/Maps/Tutorials/MainTutorial/MainTutorial.unity` | `Combined Mesh (root_ scene)_38.asset` | 22 | 26 / 26 | 10 | 2 | 0 |
| `Shooting Range` | `Assets/Levels/Maps/Tutorials/ShootingRange/Shooting Range.unity` | `Combined Mesh (root_ scene)_27.asset` | 97 | 160 / 160 | 94 | 65 | 4 |
| `Battleforce` | `Assets/Levels/Maps/Zombie/Battleforce/Battleforce.unity` | `Combined Mesh (root_ scene)_6.asset` | 65 | 91 / 91 | 35 | 24 | 0 |
| `Cord (Beta)` | `Assets/Levels/Maps/Zombie/Cord (Beta)/Cord (Beta).unity` | `Combined Mesh (root_ scene)_4.asset` | 110 | 143 / 143 | 79 | 56 | 0 |
| `Escape` | `Assets/Levels/Maps/Zombie/Escape/Escape.unity` | `Combined Mesh (root_ scene)_3.asset` | 70 | 83 / 83 | 28 | 10 | 0 |
| `Playground` | `Assets/Levels/Maps/Zombie/Playground/Playground.unity` | `Combined Mesh (root_ scene)_2.asset` | 171 | 219 / 219 | 120 | 68 | 12 |
| `Upland` | `Assets/Levels/Maps/Zombie/Upland/Upland.unity` | `Combined Mesh (root_ scene)_1.asset` | 57 | 62 / 62 | 19 | 19 | 0 |
