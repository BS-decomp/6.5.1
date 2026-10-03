# IL2CPP method/body inventory (Block Strike 6.5.1, build 2492)

Generated deterministically by `python3 tools/build_method_inventory.py` from
`lib/armeabi-v7a/libil2cpp.so` + `global-metadata.dat` of the ground-truth APK
and the exported C# sources in `client/Assets`. Outputs:
`tools/method-inventory/inventory.json` (full per-method inventory) and
`tools/method-inventory/priorities.json` (ranked lost-implementation worklist).

## Summary

- Methods in all 61 images: **61617**
- Methods in `Assembly-CSharp` + `Assembly-CSharp-firstpass`: **24373**
- Scene/prefab-referenced script classes: **306**
- Static call-graph edges decoded from ARMv7 code: **139381**
- Reachability roots (engine/NGUI/Photon messages, UnityEvent `m_MethodName`, AnimationEvent `functionName`, serialized ctors): **1228**
- Exported stubs verified as genuine no-ops in the binary: **2167**
- **Reachable lost implementations (stub in C#, substantive in binary): 6128**

## Binary body classification (game assemblies)

| kind | count |
| --- | --- |
| `empty` | 351 |
| `no_code` | 518 |
| `ret_const_0` | 23 |
| `ret_const_1` | 16 |
| `ret_const_2` | 2 |
| `ret_const_254` | 1 |
| `substantive` | 20303 |
| `tiny` | 3159 |

## Exported C# body classification (game assemblies)

| kind | count |
| --- | --- |
| `None` | 4067 |
| `body` | 329 |
| `empty` | 14187 |
| `mixed` | 102 |
| `ret_default` | 698 |
| `ret_false` | 1368 |
| `ret_null` | 2463 |
| `ret_zero` | 1159 |

## Reachability (from APK-confirmed entry points)

| tier | count |
| --- | --- |
| `by_name` (exact string-literal name dispatch (SendMessage/Invoke style)) | 1133 |
| `direct` (BL/B/function-pointer/MethodRef chain from scene roots) | 4679 |
| `none` (not reachable through any decoded edge (includes dead code)) | 16030 |
| `virtual` (adds RTA-style vtable closure over TypeInfo-referenced game types) | 2531 |

## Top 100 ranked lost implementations

Full list: `tools/method-inventory/priorities.json`.

| # | type | method | reach | scene | size | RVA |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `UICamera` | `JIIJIJJJJJJJJIIIIIIIJIJIIJIJIIJIJJIJI...` | direct | x | 8432 | `0x00666410` |
| 2 | `mVersionManager` | `JIJIIJIIJJJJIJJJJIIJIJJJIJIIIIIJIIIII...` | direct | x | 6556 | `0x00AFAFD4` |
| 3 | `mChangeName` | `JIIJIIJJIJIIIJIIIJIIJIJIJIIIJIIIJJJJI...` | direct | x | 6452 | `0x00E8F598` |
| 4 | `UIInput` | `Update` | direct | x | 6092 | `0x00E27924` |
| 5 | `UICamera` | `JJIIIIJIIJIJIIJIJIIIJIJIIJIIIJJIIIJII...` | direct | x | 5776 | `0x0066BFE8` |
| 6 | `UICamera` | `JIJIIJJJJJJJJIIJIJIJJJIJIIIJJJJIJIIJJ...` | direct | x | 5548 | `0x006688AC` |
| 7 | `mFriendsElement` | `IJIIJJJIIJJIJJIIIJIIJJIJIIIIJJJIIJJJI...` | direct | x | 5068 | `0x007E1140` |
| 8 | `UICenterOnChild` | `IIJIIJIIJJJJJJJJJJJIIJJIJIIIIIJIIJJJI...` | direct | x | 4972 | `0x00C58968` |
| 9 | `PlayerWeapons` | `IJJJJIJIIIJIIJIIJJJIJJIIIIIJJIIIIIJII...` | direct | x | 4732 | `0x005FAE40` |
| 10 | `UIAnchor` | `Update` | direct | x | 4720 | `0x013FEC7C` |
| 11 | `UIInput` | `IIJIIJJJIIIJJJIJJIJJIJIJJJIIJIJJJIJII...` | direct | x | 4712 | `0x00E22CF8` |
| 12 | `UIDeathScreen` | `IIIJIIJJIJJJIIJIIIJIJIJJJIIIJIIIIIJII...` | direct | x | 4640 | `0x00A85F1C` |
| 13 | `PlayerWeapons` | `JJJJIJIIIJJJIIJIIIJJJJIJJJJIJIJJIIJIJ...` | direct | x | 4592 | `0x005FDE18` |
| 14 | `FPWeaponShooter` | `IIJIIIIIIJJIIIIIIJIJJIJIIIJJIJJJJJJII...` | direct | x | 4496 | `0x004C4230` |
| 15 | `mFriendsManager` | `UpdateList` | direct | x | 4452 | `0x007EADD8` |
| 16 | `mCaseSkinInfoManager` | `IIIJIJIJJJIIJJJJIJJIJJIIIIIIJIIJJIIJI...` | direct | x | 4444 | `0x013D8844` |
| 17 | `mPhotonSettings` | `IJIJIIIJJJIIIIIJJJJIJIJJIJIIJJJJJIJII...` | direct | x | 4428 | `0x0058C20C` |
| 18 | `mFriendsManager` | `JIJIIJJIIJJJJJIJJJJJIIJJIJIIJJJJIIJJI...` | direct | x | 4320 | `0x007E0060` |
| 19 | `UICamera` | `JJJJIJJIIJIJIJJJIJIIIJIIIIIIIJJIIIJIJ...` | direct | x | 4308 | `0x0066533C` |
| 20 | `UIPlayerStatistics` | `JJJJJIJIIIIIJJIIIJIIJJJJJIIJIJIIJIJII...` | direct | x | 4264 | `0x00A4BFE8` |
| 21 | `mAddonMenu` | `IJIJIJIJIIIJJIJJIIIIJIIIIJIIJIJJIIJII...` | direct | x | 4264 | `0x005199A4` |
| 22 | `vp_FPCamera` | `Awake` | direct | x | 4112 | `0x00B0E2E4` |
| 23 | `UIWeaponManager` | `JIJIJIJIIIJJIIIJIJJIJJIJJJJIJJIJIJJIJ...` | direct | x | 4104 | `0x007516E4` |
| 24 | `UILabel` | `JJIIJIJJIIJJJIJIJIIIJIIIIJJJJJIJIIJJJ...` | direct | x | 4092 | `0x00A17400` |
| 25 | `mCaseSkinManager` | `IIJIJJIJJIJJJIJIJJIIIIIIIIIJIIIIJJJJI...` | direct | x | 4072 | `0x013E3B0C` |
| 26 | `UIWeaponManager` | `JIJJIIJIIIJJIJJIJJIIIJJJIIJIJJIIIJJJJ...` | direct | x | 4044 | `0x00753230` |
| 27 | `mClanChat` | `IIJIJJJIJIJIIIIIIIJJJJJIIIIIIJIIIJIIJ...` | direct | x | 3948 | `0x00E9FF1C` |
| 28 | `UIStretch` | `Update` | direct | x | 3944 | `0x00F52744` |
| 29 | `nBoxCollider` | `IIIJIJJJJJIJJIIIIIJJJIJIJJIJJIJIIJIII...` | direct | x | 3856 | `0x00AB9798` |
| 30 | `GrenadeObject` | `JJJIIJJJJJJJJIIIIJJIJIIIJIJJIJIIIJIIJ...` | direct | x | 3836 | `0x00954BCC` |
| 31 | `mInventoryElement` | `IJIIJJJIIJJIJJIIIJIIJJIJIIIIJJJIIJJJI...` | direct | x | 3728 | `0x00984454` |
| 32 | `mMarketplaceElement` | `IJIIJJJIIJJIJJIIIJIIJJIJIIIIJJJIIJJJI...` | direct | x | 3708 | `0x0099DCD8` |
| 33 | `PlayerInput` | `JIIIIIJIIJIJJJJIJJIIJIJJIJJIJIIJIJJJJ...` | direct | x | 3612 | `0x005E35FC` |
| 34 | `TicTacToe` | `JIIJIIJJJJJIJIJJIIIIIIJIJJIJIJJIJJIJJ...` | direct | x | 3608 | `0x006E529C` |
| 35 | `TicTacToe` | `JJIIJJJJIJJIJIIIJIJIIJJIIIIIJIIJJJJII...` | direct | x | 3608 | `0x006E2A94` |
| 36 | `mCraftingElement` | `IJIIJJJIIJJIJJIIIJIIJJIJIIIIJJJIIJJJI...` | direct | x | 3548 | `0x007D2918` |
| 37 | `BombMode2` | `JJJJJIIJIIJJJIIJIIJIJIJJJIIIIJIJJIJJJ...` | direct | x | 3400 | `0x00A9767C` |
| 38 | `mCaseSkinInfoManager` | `IIJIIJIJJJJIIJJJJIJJIJIIIJIIIJIJIJIII...` | direct | x | 3392 | `0x013D7B04` |
| 39 | `DecalsManager` | `JJJIJIJIIIIIIJJIIJJIJJIJJJJJIIIJJIIII...` | direct | x | 3356 | `0x00871E38` |
| 40 | `mPanelManager` | `IIIJIIJJIJJJIIJIIIJIJIJJJIIIJIIIIIJII...` | direct | x | 3336 | `0x005919F0` |
| 41 | `ControllerManager` | `Awake` | direct | x | 3296 | `0x0080463C` |
| 42 | `UIPlayerStatisticsElement` | `IJIIJJJIIJJIJJIIIJIIJJIJIIIIJJJIIJJJI...` | direct | x | 3276 | `0x00A4D4BC` |
| 43 | `mCaseSkinInfoManager` | `IIIIIJJIIJJIJIJIJJJJIIJJJIIIIJIIIIJII...` | direct | x | 3176 | `0x013D5DC8` |
| 44 | `UIToggle` | `JJIJJJIJIJIIIIIIIJJJJIJJJIIIJJIIIIIJJ...` | direct | x | 3012 | `0x0073E21C` |
| 45 | `UIScrollView` | `IJIIJIIIIIIIIIJIIIIJIIIJIIJJIIIIJJJII...` | direct | x | 2932 | `0x00CDB7D0` |
| 46 | `UIScore` | `JIIJJIIIIIJIIJJIJJJJJIJJJIJIJJJIIIJIJ...` | direct | x | 2904 | `0x00CC8F60` |
| 47 | `CameraFirstPerson` | `JJIIJJJIJJJIIJJJJIIJIIJIJJIIIJIIJIJJJ...` | direct | x | 2880 | `0x005A5734` |
| 48 | `UICrosshair` | `IJJIIJIJIJJIJIJJIIIJIJIJIIIIJIIJIIJIJ...` | direct | x | 2880 | `0x00A75FC8` |
| 49 | `UICamera` | `JJIIIJIJJJJJIIJJIIIJIJJJIIIIIJJJIJIIJ...` | direct | x | 2812 | `0x0066301C` |
| 50 | `vp_FPWeapon` | `Start` | direct | x | 2760 | `0x00B1DAF8` |
| 51 | `UICamera` | `IIIIJJJJIJJIIJJJJJIIIIIJJJIIIJJJJIIJI...` | direct | x | 2704 | `0x0065F51C` |
| 52 | `BombManager` | `IJIJIJIIIIJJIJIJJJIJJJIIIIIIJJIJJIIJJ...` | direct | x | 2696 | `0x00709EF8` |
| 53 | `PlayerWeapons` | `IIJJJIIJJIJJIIJJJIJJIIJJIIIJJJJJJJJIJ...` | direct | x | 2696 | `0x005F8750` |
| 54 | `mCaseStickerElement` | `JIJIIJIIIIIJJIIJIIIJJIIJJIIJJJJIJIIIJ...` | direct | x | 2680 | `0x013E8BA8` |
| 55 | `vp_FPWeapon` | `Awake` | direct | x | 2676 | `0x00B290DC` |
| 56 | `BombMode2` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2632 | `0x00A9AEE0` |
| 57 | `BunnyHopTop` | `JJIJIJJIJJIJIJJJIIJIIIIJJJIIJJIIIIJIJ...` | direct | x | 2608 | `0x00AAA338` |
| 58 | `EscortMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2588 | `0x004B3ABC` |
| 59 | `DeathRun` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2580 | `0x0085EAEC` |
| 60 | `InputJoystick` | `Update` | direct | x | 2572 | `0x00D82264` |
| 61 | `BombAudio` | `Update` | direct | x | 2564 | `0x00706810` |
| 62 | `UICamera` | `JJIIJJIJJJIIJIJJJIJIIJJJIIIJIIIIJIIJJ...` | direct | x | 2560 | `0x00660124` |
| 63 | `MurderMode` | `IIJJJIIJJJJIJIJJJIIIIJJIJIJIIJIIIIJJJ...` | direct | x | 2540 | `0x009F7550` |
| 64 | `PlayerInput` | `JIIJIIIJJJIJJIIJIIIIIIJJIIJJIJJIJJIJI...` | direct | x | 2524 | `0x005E2BF4` |
| 65 | `TennisMode` | `JJJJIJJJJIIJJIJIIIJJJJIJJJIIJJJJIJJJJ...` | direct | x | 2524 | `0x006DA478` |
| 66 | `BunnyHopTop` | `UpdateData` | direct | x | 2520 | `0x00AA90E4` |
| 67 | `UIScrollView` | `LateUpdate` | direct | x | 2484 | `0x00CD7A0C` |
| 68 | `VIPMode` | `JIIIIIJIIIJJJJJJJJIJJJIJIIIIIIJIIIIIJ...` | direct | x | 2476 | `0x0052BEDC` |
| 69 | `TennisMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2464 | `0x006DCF38` |
| 70 | `ZombieMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2460 | `0x00507E24` |
| 71 | `CheckManager` | `IIJIIJJJIIIJIIIJJIJIJIJJJIIIJIJIJJIIJ...` | direct | x | 2456 | `0x005C1074` |
| 72 | `mPhotonSettings` | `JJIJIIIIJIIIIJJIIJIJIJJIIIJJIIJIJJIII...` | direct | x | 2456 | `0x0058A3C8` |
| 73 | `mQuickPlay` | `IJIJIJJJIIIJIJIJJJIIIJIIJIJJIJIJIIIJI...` | direct | x | 2456 | `0x00730548` |
| 74 | `FPWeaponShooter` | `IJJIIJIJJJIJJIIIJIIJIIIIIIIIIJIJIJIIJ...` | direct | x | 2452 | `0x004C6DBC` |
| 75 | `ZombieMode` | `JJJJIJJJJIIJJIJIIIJJJJIJJJIIJJJJIJJJJ...` | direct | x | 2452 | `0x00503060` |
| 76 | `BombMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2444 | `0x00A8DD18` |
| 77 | `BombMode2` | `JIIIIIJIIIJJJJJJJJIJJJIJIIIIIIJIIIIIJ...` | direct | x | 2440 | `0x00A9A558` |
| 78 | `UIWeaponManager` | `SelectWeapon` | direct | x | 2440 | `0x00752810` |
| 79 | `JuggernautMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2412 | `0x0088B99C` |
| 80 | `VIPMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2368 | `0x00530940` |
| 81 | `HungerGames` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2360 | `0x00C023F0` |
| 82 | `UISettings` | `IIJJJIIIIJIJJJJIIJIJJJJJJIJJIIIIIIJJI...` | direct | x | 2360 | `0x00B75F44` |
| 83 | `ZombieMode` | `Start` | direct | x | 2360 | `0x00509304` |
| 84 | `ClassicMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2356 | `0x010EC2F4` |
| 85 | `Deathmatch` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2356 | `0x00868B50` |
| 86 | `JuggernautMode` | `JIIIIIJIIIJJJJJJJJIJJJIJIIIIIIJIIIIIJ...` | direct | x | 2348 | `0x0088A5F8` |
| 87 | `GrenadeMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2344 | `0x0095142C` |
| 88 | `mClanChat` | `IIJJIIJJJIIIIIIJJJIJIJIJJIIJJIJJIIIII...` | direct | x | 2320 | `0x00E9F60C` |
| 89 | `mMarketFilter` | `Open` | direct | x | 2312 | `0x00995DA0` |
| 90 | `HunterMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2300 | `0x00C0E828` |
| 91 | `UILabel` | `IIIJIJIIIJIJIIIJJIJIJIIIIJIIIJIIIJIII...` | direct | x | 2300 | `0x00A1982C` |
| 92 | `BombManager` | `IIIIJIIIIIJIIIIIIJJIIIJIJJIJJJIJIIIIJ...` | direct | x | 2296 | `0x00710BB0` |
| 93 | `BombManager` | `IJIIIIJJJJIIJIIIIIIJIIIIJIIIIJIJJJIII...` | direct | x | 2256 | `0x0070B0D8` |
| 94 | `UIHealth` | `JIJIJJIJIIJIJIJIIIIIIIJIIJJIIIIIJJJII...` | direct | x | 2256 | `0x00E19D7C` |
| 95 | `mCaseWheelManager` | `JJIJJJIJJJJJJJJIIJIIJIIJIIIJIJIJIJJII...` | direct | x | 2236 | `0x00E8E378` |
| 96 | `UIPlayerStatistics` | `JIJJJIJIJIIJJIJJJJIIJIIJJJIIIJIIIIIJI...` | direct | x | 2216 | `0x00A4B740` |
| 97 | `HotKnifeMode` | `JIJIJIJJIIIJIIJIJIJJJIIIJJJJJIIIJIJII...` | direct | x | 2212 | `0x00BF73C4` |
| 98 | `UIWarningToast` | `IIIJIIJJIJJJIIJIIIJIJIJJJIIIJIIIIIJII...` | direct | x | 2212 | `0x0074DDFC` |
| 99 | `mMarketplaceManager` | `JIJJIIIIIJIJIIJIIJJJIJJIJIIIJIIJJJIJI...` | direct | x | 2200 | `0x0057F6D4` |
| 100 | `BombMode` | `JIIIIIJIIIJJJJJJJJIJJJIJIIIIIIJIIIIIJ...` | direct | x | 2196 | `0x00A8B8B4` |

## Methodology and limitations

- **Binary classification** decodes the actual ARMv7 words: `bx lr` = `empty`,
  `mov r0, #imm; bx lr` = `ret_const_imm`, ≤16 bytes = `tiny`, otherwise `substantive`.
  Method sizes are estimated as the distance to the next method start inside the
  executable `PT_LOAD` segment, so trailing literal pools are included in `size`.
- **Call edges** cover BL/conditional-BL, cross-method unconditional B (tail calls),
  raw function-pointer literal words, and `Il2CppMetadataUsage` MethodRef slots.
  Virtual/interface dispatch is over-approximated per RTA: when reachable game code
  references a game type's TypeInfo, that type's metadata vtable slots and
  `.ctor`/`.cctor` become reachable. Generic-method vtable entries (kind 6) and
  reflection beyond exact-name string literals are not modeled; `none` therefore
  means *no decoded evidence of reachability*, not proven-dead.
- **Source classification** parses the exported client sources; only literal
  `{ }`, `return false/true/null/0/default` bodies count as stubs. A stub whose
  binary body is also trivial is counted as a verified no-op, not a loss.
- Everything is recomputed from the APK on each run; no cached or invented data.
