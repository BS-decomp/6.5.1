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
- `GDPR.OnJoinedRoom` (`0x006c3330`) loads `MainTutorial` through the verified
  scene wrapper once the tutorial offline room is joined.
- The three obfuscated scene wrapper methods at `0x013bce08`, `0x013bd5e8`, and
  `0x013be83c` all call `SceneManager.LoadScene(string)`.
- `UIEventClick` subscribes/unsubscribes to the ground-truth `UICamera` click
  delegate and invokes its serialized `UnityEvent` only for its own GameObject.

- `mPhotonSettings.CreateServerOffline(string)` (`0x0059df28`) — the full verified
  flow (corrected from the earlier simplified reconstruction that referenced a
  non-existent canonical `PhotonNetwork` facade): the map string is stored in the
  nested deferred-create helper (field `+0x08`), the flow requires a logged-in
  account (`AccountManager` static bool `@+0x04`), disconnects an active Photon
  connection (connected-check `0x0049af18` / `Disconnect` `0x004a1d08` on the
  obfuscated PUN static class `JJIJJJIIII...IJIIJ`), resets the game-mode manager
  (`0x00d8d5d8`), shows the localized `"Loading" + "..."` popup (`mPopUp`,
  localization `0x016f9c68`) and schedules the helper via
  `TimerManager.In(0.2f, ...)`. Without an account it shows the localized
  `"Connection account"` toast (`UIToast`).
- The deferred helper (`0x0071d948`) shows the `"Loading..."` popup, stores the
  map into the private static map-name field of `mPhotonSettings` (static `@+0x00`),
  enables Photon offline mode (property setter `0x0049c5d0`, backing static bool
  `@+0xb1` verified through getter `0x0049c544`), clears the scene-wrapper guard
  flag (`JIJJJIIJJI...IIJII` static bool `@+0x00`) and calls the PUN
  `CreateRoom(map)` (`0x004a2078`).
- `mPhotonSettings.OnJoinedRoom` (`0x0059d310`) resets the game-mode manager
  (`0x00d8d5d8`), applies the joined room's game mode
  (`room` getter `0x0049bb98` -> `GetGameMode` extension `0x01475d6c` ->
  mode setter `0x00d8e644`), then: offline mode -> loads the stored map scene via
  the verified scene wrapper (`0x013bd5e8`); online -> pauses the Photon message
  queue (setter `0x0049d840`) and sync-loads the map (`0x004a96ac`).
- `mCreateServer.Start` (`0x007dd1e0`), `Open` (`0x007de300`), and
  `SetMaxPlayer` (`0x007dc64c`) restore the serialized singleton, panel-open state,
  numeric player-limit parse, and selected-limit marker movement.
- `mPlayerCamera.Awake` (`0x0071f138`) restores its singleton and Camera component
  reference; `mOthers.ExitGame`, `ShowOthersGames`, and `ShowToast` restore their
  verified application/URL/toast calls.
- Obfuscated `PhotonNetwork` (`JJIJJJIIIIJJJIJIJIJIIJIJJJIIIIIJJIIJJIIIIJIJIIJ`,
  statics: `+0x0c` networkingPeer, `+0xb1` isOfflineMode, `+0xb4` offlineModeRoom) —
  offline-mode core, every body decoded instruction-by-instruction:
  - `connected` getter method (`0x0049af18`): offline -> true; null peer -> false;
    else `!IsInitialConnect(+0xb8)` and `State(+0xb4)` not in
    {PeerCreated, Disconnecting, Disconnected}.
  - `connectionStateDetailed` getter method (`0x0049b61c`): offline ->
    `offlineModeRoom != null ? Joined : ConnectedToMaster`; null peer ->
    `Disconnected`; else `networkingPeer.State`.
  - `connectedAndReady` getter method (`0x0049b47c`): `connected()` guard,
    offline -> true, then a state switch the compiler lowered to
    `(0xd2e >> (state-8)) & 1` plus explicit `PeerCreated`/`ConnectingToGameserver`
    checks; decoded false-set {1,6,8,12,14,15,17,20} matches the restored switch
    case-for-case.
  - `offlineMode` get/set methods (`0x0049c544` / `0x0049c5d0`): setter verifies
    no-change, rejects enabling while connected
    (`"Can't start OFFLINE mode while connected!"`), disconnects a non-idle peer
    via canonical `PhotonPeer.PeerState`/`Disconnect()`, then
    `ChangeLocalID(-1)` (`0x008fee9c`) and, when enabling,
    `SendMonoMessage(OnConnectedToMaster=16)` (`0x008f8364`); when disabling also
    clears `offlineModeRoom`.
  - `CreateRoom` overloads (`0x004a2078` string; `0x004a258c` +options+lobby;
    `0x004a210c` +expectedUsers): 1/3-arg delegate to the 4-arg body. Offline:
    guard `offlineModeRoom != null`
    (`"CreateRoom failed. In offline mode you still have to leave a room to enter
    another."`) else `EnterOfflineRoom(name, options, true)`. Online: requires
    `networkingPeer.Server(+0xb0) == MasterServer` and `connectedAndReady`
    (`"CreateRoom failed. Client is not on Master Server or ..."`), lobby fallback
    through `insideLobby(+0xb9)`/`lobby(+0xbc)`, fills the obfuscated
    `EnterRoomParams` (`IJIJJIJIIJIIIJJJIJIIIIJJJJJIIIJIJIIIJIIJJJIIIJI`:
    `+8` RoomName, `+0xc` RoomOptions, `+0x10` Lobby, `+0x1c` ExpectedUsers) and
    tail-calls obfuscated `NetworkingPeer.OpCreateGame` (`0x008faac0`).
  - `EnterOfflineRoom` (`0x004a2628`): `offlineModeRoom = new Room(name, options)`
    (ctor `0x00e38d68`); `ChangeLocalID(1)`;
    `networkingPeer.State = ConnectingToGameserver(6)`;
    `OnStatusChanged(StatusCode.Connect=1024)` (`0x00906544`);
    `masterClientId(+0x28) = 1`; `SendMonoMessage(OnCreatedRoom=5)` when
    `createdRoom`; `SendMonoMessage(OnJoinedRoom=12)`.
  - `room` getter method (`0x0049bb98`): offline -> `offlineModeRoom(+0xb4)`,
    else the obfuscated `NetworkingPeer` current-room body (`0x008fcbb0`).
  - `isMessageQueueRunning` get/set methods (`0x0049d7b4` / `0x0049d840`):
    getter returns the static bool at `+0xc8`; setter starts the
    `PhotonHandler` fallback-send-ack thread (`0x0063efac`) when enabling,
    then `networkingPeer.IsSendingOnlyAcks(+0x68)` (canonical `PhotonPeer`
    property) `= !value` and the `+0xc8` static `= value`.
  - `Disconnect` (`0x004a1d08`): offline -> `offlineMode = false` (setter
    `0x0049c5d0`), `offlineModeRoom = null`, `State = Disconnecting(14)`,
    `OnStatusChanged(StatusCode.Disconnect=1025)`; online -> virtual
    `networkingPeer.Disconnect()` (vtable `+0xfc`) when the peer is non-null.
  - `LoadLevel(string)` (`0x004a96ac`): clears the `networkingPeer` flag
    `+0x18d`; when `automaticallySyncScene(+0xbc)` is set forwards to the
    protected-internal level-props sync (`0x00912828`, args
    `levelName/true/false`); pauses the message queue (`0x0049d840` with
    `false`); sets `loadingLevelAndPausedNetwork(+0x13a) = true` and
    tail-calls the verified scene wrapper (`0x013bd5e8`).
- Obfuscated `NetworkingPeer.SendMonoMessage` (`0x008f8364`): this build
  replaced the PUN `GameObject.SendMessage` dispatch with a 30-entry jump
  table (at `0x008f83bc`) over `PhotonNetworkingMessage`; each case invokes a
  public static delegate field of the obfuscated `PhotonNetwork`
  (`+0x18..+0x84`, one per message, decoded case-by-case with its delegate
  type and parameter unboxing: `()` / `(PhotonPlayer)` / `(short, string)` /
  `(DisconnectCause)` / `(Hashtable)` / `(string)` / `(object[])`). Enum
  values 17 (`OnPhotonSerializeView`) and 28 (`OnPhotonPlayerActivityChanged`)
  jump straight to the common return — no delegate field exists for them.
- Obfuscated `NetworkingPeer`
  (`JJJJJIJJJIIJIIIJIJIIIJIIIIJIIIJJJJJIIJIJIJIIJII`): the instance fields at
  `+0xb0`/`+0xb4`/`+0xbc` are recorded in `global-metadata.dat` as
  `<name>k__BackingField`, i.e. originally public auto-properties
  (PUN 1.x `Server`/`State`/`lobby`). The export flattened them to `private`
  fields; `tools/reconstruct_651_scripts.py` restores the public accessibility so
  the verified PhotonNetwork bodies compile. No identifiers were invented.

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
