# 6.5.1 script reconstruction status

`tools/reconstruct_651_scripts.py` applies the first verified runtime slice from the
6.5.1 ARMv7 IL2CPP binary. It is deliberately conservative: it only writes behavior
that has a matching method RVA/disassembly note in the reconstruction log and leaves
unresolved methods visible rather than inventing behavior.

## Verified in `libil2cpp.so`

- `AndroidPermissions.Start` (`0x0100b594`) enters `Logo`.
- `Logo.Start` (`0x00773560`) starts the loading coroutine. The coroutine's state
  machine contains the observed `0.01f` wait and the progress sequence `0%`, `50%`,
  `90%`, `100%`, then loads `GDPR`.
- `GDPR.Start` (`0x006c3a6c`) reads `PlayerPrefs.GetInt("GDPR", 0)` and loads
  `Menu` when accepted; otherwise it activates the GDPR panel.
- `GDPR.OnAccept` (`0x006c3248`) hides the GDPR panel, shows the training panel,
  and writes `PlayerPrefs.SetInt("GDPR", 1)`.
- `GDPR.OnClickTraining` (`0x006c36c8`) hides the training panel and loads either
  `MainTutorial` or `Menu`.
- The three obfuscated scene wrapper methods at `0x013bce08`, `0x013bd5e8`, and
  `0x013be83c` all call `SceneManager.LoadScene(string)`.
- `UIEventClick` subscribes/unsubscribes to the ground-truth `UICamera` click
  delegate and invokes its serialized `UnityEvent` only for its own GameObject.

- `mPhotonSettings.CreateServerOffline(string)` (`0x0059df28`) follows the verified
offline launch branch: disconnect an existing Photon connection, enable Photon
offline mode, and create the room from the supplied map string.
- `mCreateServer.Start` (`0x007dd1e0`), `Open` (`0x007de300`), and
  `SetMaxPlayer` (`0x007dc64c`) restore the serialized singleton, panel-open state,
  numeric player-limit parse, and selected-limit marker movement.
- `mPlayerCamera.Awake` (`0x0071f138`) restores its singleton and Camera component
  reference; `mOthers.ExitGame`, `ShowOthersGames`, and `ShowToast` restore their
  verified application/URL/toast calls.

The atlas, sprite, texture, label, and localization changes restore serialized NGUI
state access (material, texture, atlas, sprite name, text, and CSV localization).
They are not a claim that every NGUI rendering or input method has already been
recovered; remaining methods must continue to be matched against the binary before
being changed.

## Prioritized worklist

`tools/build_method_inventory.py` produces the deterministic IL2CPP method/body
inventory used to drive further reconstruction: it classifies every exported C#
body against the actual ARMv7 machine code, computes static reachability from
scene/prefab roots, and ranks the reachable lost implementations in
`tools/method-inventory/priorities.json` (report: `docs/method-inventory.md`).
Restored bodies listed in `tools/method-inventory/restored_methods.json` are
guarded against stub regression by `tools/verify_client_project.py`.

## Reproducible checks

```text
python3 tools/reconstruct_651_scripts.py
python3 tools/build_method_inventory.py
python3 tools/verify_client_project.py --client-dir client
```

The verifier expects the 46 recovered APK shaders plus the three canonical mobile
lightmap shaders. Arena's sparse checkout may omit `Assets/RecoveredGeometry`; a full
checkout still validates all 4,846 recovered meshes.
