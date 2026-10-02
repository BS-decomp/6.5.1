# Статус экспорта и аудита Block Strike 6.5.1 (build 2492)

Все данные ниже получены прямым анализом оригинального APK `original/apk/com.rexetstudio.blockstrike_6.5.1_2492.apk` и первичного экспорта AssetRipper 2.0.0 Linux x64.

## 1. Базовые параметры билда
- **Версия игры:** Block Strike `6.5.1` (`versionCode 2492`)
- **Оригинальная версия Unity:** `2019.2.3f1` (`2019.2.0a7` в части встроенных ресурсов)
- **Целевая версия редактора:** `Unity 2021.3.45f2 LTS`
- **Скриптовый бэкенд:** `IL2CPP` (`global-metadata.dat` версии `24.2`, `lib/armeabi-v7a/libil2cpp.so` — 32-bit ARMv7 ELF, 61 617 методов)
- **Обфускация метаданных:** `Beebyte Obfuscator v2.7.1` (`PrivateImplementationDetailsKQPLETG.__BB_OBFUSCATOR_VERSION_2_7_1`)
- **Время полного экспорта через AssetRipper (`LightmapTextureExportFormat = Image`):** ~40 секунд (`LoadFile` 11.0 с + `Export/UnityProject` 29.1 с, всего 8 617 ассетов)

## 2. Сцены (`Assets/Levels/`)
- Всего экспортировано **74 сцены** (`level0`–`level73`).
- **Важное отличие от 3.7.0:** в версии 6.5.1 имена сцен в `ProjectSettings/EditorBuildSettings.asset` **не зашифрованы** DES/PBKDF2 — все 74 пути в `EditorBuildSettings.asset` изначально хранятся в открытом виде:
  - Системные/меню сцены (4): `AwakeScene.unity`, `Logo.unity`, `GDPR.unity`, `Menu.unity`
  - Туториалы (2): `MainTutorial.unity`, `Shooting Range.unity`
  - Карты режимов (68): `Others` (28), `BunnyHop` (9), `DeathRun` (10), `HungerGames` (3), `Hunter` (3), `MiniGames` (8), `Surf` (2), `Zombie` (5).

## 3. Static-batch геометрия карт (`Combined Mesh (root_ scene)*.asset`)
- Из 74 сцен **70 сцен** (все карты и туториалы) используют static batching (`m_StaticBatchInfo` с `subMeshCount > 0` при `m_StaticBatchRoot: {fileID: 0}`).
- Сцены без static-batched рендереров (4): `AwakeScene.unity`, `GDPR.unity`, `Logo.unity`, `Menu.unity`.
- Всего по 70 сценам насчитывается **4 846 static-batched `MeshRenderer`**, ссылающихся на объединённые меши `Assets/Mesh/Combined Mesh (root_ scene)*.asset` (70 ассетов).
- Поскольку `m_StaticBatchRoot` в сериализованных сценах равен `{fileID: 0}`, встроенная опция `EnableStaticMeshSeparation` в AssetRipper их не разделяет — требуется разделение сабмешей по диапазону `[firstSubMesh, firstSubMesh + subMeshCount)` с обратным матричным преобразованием из мировых координат в локальные координаты `Transform` объекта (по аналогии с инструментом геометрии из 3.7.0, адаптированным под YAML-формат `m_StaticBatchInfo` Unity 2019/2021).

## 4. Лайтмапы и освещение (`LightingData.asset`)
- В отличие от Unity 4.7.2 (3.7.0), в Unity 2019.2.3f1 используется нативный ассет `LightingData.asset` (`LightingDataAsset`, classID `1120`), который уже привязан в `LightmapSettings.m_LightingDataAsset` каждой сцены и содержит массив `m_LightmappedRendererData` (`lightmapIndex`, `lightmapST`, `uvMesh`).
- При экспорте с `LightmapTextureExportFormat = Image` все **73 текстуры лайтмап** (`Lightmap-*_comp_light.png`) экспортируются в PNG и автоматически связываются с `74` файлами `LightingData.asset` (`type: 3`).

## 5. Шейдеры (`Assets/Resources/shaders/` и `Assets/Shader/`)
- Встроенные шейдеры карт (`Mobile/Unlit (Supports Lightmap)`, `Mobile/VertexLit`, `Mobile/Diffuse`, `Mobile/Particles/*`) в 6.5.1 ссылаются напрямую на `unity_builtin_extra` (`guid: 0000000000000000f000000000000000`), поэтому подхватываются редактором Unity нативно.
- Все **46 проектных `.shader` файлов** экспортированы AssetRipper как заглушки `DummyShaderTextExporter`:
  - `25` шейдеров NGUI в `Assets/Resources/shaders/` (24 классических из 3.7.0 + `Unlit/Transparent Colored Cubemap`)
  - `8` шейдеров ProBuilder (`Hidden/ProBuilder/*`, `ProBuilder/Diffuse Vertex Color`, `ProBuilder/Standard Vertex Color`, `ProBuilder/Unlit Solid Color`, `ProBuilder/UnlitVertexColor`)
  - `6` шейдеров MADFINGER (`Diffuse/Simple`, `Environment/Cube env map`, `Particles/Additive TwoSide`, `Particles/Alpha Blended`, `Transparent/Blinking GodRays`, `Transparent/GodRays`)
  - `5` шейдеров WarFX (`WFX/Additive (Soft) Alpha8`, `WFX/Additive Alpha8`, `WFX/Multiply Alpha8`, `WFX/Scroll/Additive`, `WFX/Scroll/Smoke`)
  - `2` специальных шейдера (`Mobile/Unlit/Transparent Color`, `Vertigo/GaussianBlur`)
- Скрипт `tools/extract_apk_shader_texts.py` извлекает из APK 6.5.1 полные структуры `SerializedShader` (`Properties`, `Tags`, `Pass` state) и скомпилированные `GLES3` (`#version 300 es`, `hlslcc`) вертексные и фрагментные программы для всех 61 шейдеров в `tools/shader-extract/`.

## 6. Скрипты (`Assets/Scripts/Assembly-CSharp` и `Assets/Plugins/Assembly-CSharp-firstpass`)
- Экспортировано **892 `.cs` файла** в `Assembly-CSharp` (652 с читаемыми именами классов, 240 с `I`/`J`-обфусцированными именами `Beebyte Obfuscator`) и **15 `.cs` файлов** в `Assembly-CSharp-firstpass` (`Prime31`).
- Имена всех `MonoBehaviour`-классов и сериализуемых полей в `.cs` файлах полностью совпадают с YAML-сценами и префабами (включая `I`/`J`-поля, сериализованные по порядку полей из `global-metadata.dat`).
- **Важный технический факт по телам методов IL2CPP ARMv7:**
  - В APK 6.5.1 присутствует только 32-битная библиотека `lib/armeabi-v7a/libil2cpp.so`.
  - И AssetRipper (`Level2`), и `Cpp2IL` (`ArmV7InstructionSet.GetIsilFromMethod` возвращает пустой список `[]`) для 32-bit ARMv7 генерируют пустые тела-заглушки (`{ }`, `return default;`).
  - Для работы `[ExecuteInEditMode]` компонентов в редакторе Unity (`UIRoot`, `UIPanel`, `UIWidget`, `UISprite`, `UILabel`, `UIDrawCall`, `MeshAtlas`, `SkinnedMeshAtlas`) и игровой логики требуется восстановление тел методов по дизассемблеру `lib/armeabi-v7a/libil2cpp.so` + `global-metadata.dat` и референсным исходникам общих подсистем (NGUI, UFPS `vp_*`, `MeshAtlas`, `TimerManager`, `EventManager` и др.) при строгом сохранении сериализованных имён полей 6.5.1.
