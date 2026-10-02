using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace BlockStrike.EditorTools
{
    public static class BlockStrikeGeometryRecovery
    {
        private const string ManifestRelativePath = "../tools/geometry-recovery/manifest.json";

        [Serializable]
        private class RecoveryIndexManifest
        {
            public string unityVersion;
            public string targetEditorVersion;
            public int sceneCount;
            public int totalStaticRenderers;
            public int totalReferencedSubMeshes;
            public int totalLightmappedStaticRenderers;
            public SceneIndexEntry[] scenes;
        }

        [Serializable]
        private class SceneIndexEntry
        {
            public string sceneName;
            public string sceneSlug;
            public string scenePath;
            public string manifestPath;
            public int staticRendererCount;
            public int referencedSubMeshCount;
            public int lightmappedRendererCount;
        }

        [Serializable]
        private class SceneRecoveryManifest
        {
            public string sceneName;
            public string sceneSlug;
            public string scenePath;
            public int staticRendererCount;
            public int referencedSubMeshCount;
            public int lightmappedRendererCount;
            public RendererEntry[] renderers;
        }

        [Serializable]
        private class LightmapInfoEntry
        {
            public string lightingDataAsset;
            public int lightmapIndex;
            public float[] lightmapST;
        }

        [Serializable]
        private class RendererEntry
        {
            public long rendererId;
            public long gameObjectId;
            public string gameObjectName;
            public long transformId;
            public long meshFilterId;
            public string hierarchyPath;
            public string combinedMeshGuid;
            public string combinedMeshAssetPath;
            public int firstSubMesh;
            public int subMeshCount;
            public int[] subMeshIndices;
            public string[] materialGuids;
            public LightmapInfoEntry lightmapInfo;
            public string outputAssetPath;
            public string outputAssetGuid;
        }

        [MenuItem("Tools/Block Strike/Geometry Recovery/Verify Recovered Scenes")]
        public static void VerifyRecoveredScenesMenu()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string repoRoot = Path.GetFullPath(Path.Combine(projectRoot, ".."));
            string indexPath = Path.Combine(repoRoot, "tools/geometry-recovery/manifest.json");
            if (!File.Exists(indexPath))
            {
                Debug.LogError("[BlockStrikeGeometryRecovery] Missing manifest: " + indexPath);
                return;
            }

            RecoveryIndexManifest index = JsonUtility.FromJson<RecoveryIndexManifest>(File.ReadAllText(indexPath));
            int verifiedMeshes = 0;
            int missingMeshes = 0;

            foreach (SceneIndexEntry entry in index.scenes)
            {
                string sceneManifestPath = Path.Combine(repoRoot, entry.manifestPath);
                if (!File.Exists(sceneManifestPath))
                {
                    Debug.LogWarning("[BlockStrikeGeometryRecovery] Missing scene manifest: " + sceneManifestPath);
                    continue;
                }

                SceneRecoveryManifest sceneManifest = JsonUtility.FromJson<SceneRecoveryManifest>(
                    File.ReadAllText(sceneManifestPath)
                );
                foreach (RendererEntry renderer in sceneManifest.renderers)
                {
                    Mesh mesh = AssetDatabase.LoadAssetAtPath<Mesh>(renderer.outputAssetPath);
                    if (mesh != null && mesh.vertexCount > 0)
                    {
                        verifiedMeshes++;
                    }
                    else
                    {
                        missingMeshes++;
                        Debug.LogWarning("[BlockStrikeGeometryRecovery] Missing or empty mesh: " + renderer.outputAssetPath);
                    }
                }
            }

            Debug.Log(
                string.Format(
                    "[BlockStrikeGeometryRecovery] Verified {0} recovered meshes across {1} scenes (missing: {2}).",
                    verifiedMeshes,
                    index.sceneCount,
                    missingMeshes
                )
            );
        }

        [MenuItem("Tools/Block Strike/Geometry Recovery/Recover Active Scene")]
        public static void RecoverActiveSceneMenu()
        {
            Scene activeScene = SceneManager.GetActiveScene();
            if (!activeScene.IsValid() || string.IsNullOrEmpty(activeScene.path))
            {
                Debug.LogError("[BlockStrikeGeometryRecovery] No valid active scene is open.");
                return;
            }

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string repoRoot = Path.GetFullPath(Path.Combine(projectRoot, ".."));
            string indexPath = Path.Combine(repoRoot, "tools/geometry-recovery/manifest.json");
            if (!File.Exists(indexPath))
            {
                Debug.LogError("[BlockStrikeGeometryRecovery] Missing manifest: " + indexPath);
                return;
            }

            RecoveryIndexManifest index = JsonUtility.FromJson<RecoveryIndexManifest>(File.ReadAllText(indexPath));
            foreach (SceneIndexEntry entry in index.scenes)
            {
                if (string.Equals(entry.scenePath, activeScene.path, StringComparison.OrdinalIgnoreCase))
                {
                    string sceneManifestPath = Path.Combine(repoRoot, entry.manifestPath);
                    SceneRecoveryManifest sceneManifest = JsonUtility.FromJson<SceneRecoveryManifest>(
                        File.ReadAllText(sceneManifestPath)
                    );
                    RecoverLoadedScene(activeScene, sceneManifest);
                    return;
                }
            }

            Debug.Log("[BlockStrikeGeometryRecovery] Active scene has no static-batch manifest entries: " + activeScene.path);
        }

        [MenuItem("Tools/Block Strike/Geometry Recovery/Recover All Scenes")]
        public static void RecoverAllScenesMenu()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string repoRoot = Path.GetFullPath(Path.Combine(projectRoot, ".."));
            string indexPath = Path.Combine(repoRoot, "tools/geometry-recovery/manifest.json");
            if (!File.Exists(indexPath))
            {
                Debug.LogError("[BlockStrikeGeometryRecovery] Missing manifest: " + indexPath);
                return;
            }

            RecoveryIndexManifest index = JsonUtility.FromJson<RecoveryIndexManifest>(File.ReadAllText(indexPath));
            int recoveredScenes = 0;
            try
            {
                for (int i = 0; i < index.scenes.Length; i++)
                {
                    SceneIndexEntry entry = index.scenes[i];
                    EditorUtility.DisplayProgressBar(
                        "Block Strike Geometry Recovery",
                        string.Format("Recovering {0} ({1}/{2})", entry.sceneName, i + 1, index.scenes.Length),
                        (float)i / Math.Max(1, index.scenes.Length)
                    );
                    string sceneManifestPath = Path.Combine(repoRoot, entry.manifestPath);
                    if (!File.Exists(sceneManifestPath))
                    {
                        continue;
                    }

                    SceneRecoveryManifest sceneManifest = JsonUtility.FromJson<SceneRecoveryManifest>(
                        File.ReadAllText(sceneManifestPath)
                    );
                    Scene scene = EditorSceneManager.OpenScene(entry.scenePath, OpenSceneMode.Single);
                    RecoverLoadedScene(scene, sceneManifest);
                    recoveredScenes++;
                }
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[BlockStrikeGeometryRecovery] Completed recovery for " + recoveredScenes + " scenes.");
        }

        private static void RecoverLoadedScene(Scene scene, SceneRecoveryManifest manifest)
        {
            Dictionary<long, MeshRenderer> renderersById = new Dictionary<long, MeshRenderer>();
            foreach (GameObject root in scene.GetRootGameObjects())
            {
                foreach (MeshRenderer mr in root.GetComponentsInChildren<MeshRenderer>(true))
                {
                    GlobalObjectId gid = GlobalObjectId.GetGlobalObjectIdSlow(mr);
                    renderersById[(long)gid.targetObjectId] = mr;
                }
            }

            int updatedCount = 0;
            foreach (RendererEntry entry in manifest.renderers)
            {
                MeshRenderer mr;
                if (!renderersById.TryGetValue(entry.rendererId, out mr) || mr == null)
                {
                    continue;
                }

                Mesh recoveredMesh = AssetDatabase.LoadAssetAtPath<Mesh>(entry.outputAssetPath);
                if (recoveredMesh == null)
                {
                    recoveredMesh = BuildMeshFromCombined(mr.transform, entry);
                    if (recoveredMesh == null)
                    {
                        continue;
                    }
                    EnsureFolderExists(Path.GetDirectoryName(entry.outputAssetPath));
                    AssetDatabase.CreateAsset(recoveredMesh, entry.outputAssetPath);
                }

                MeshFilter mf = mr.GetComponent<MeshFilter>();
                if (mf == null)
                {
                    mf = mr.gameObject.AddComponent<MeshFilter>();
                }
                mf.sharedMesh = recoveredMesh;

                SerializedObject so = new SerializedObject(mr);
                SerializedProperty batchInfo = so.FindProperty("m_StaticBatchInfo");
                if (batchInfo != null)
                {
                    SerializedProperty firstSub = batchInfo.FindPropertyRelative("firstSubMesh");
                    SerializedProperty subCount = batchInfo.FindPropertyRelative("subMeshCount");
                    if (firstSub != null) firstSub.intValue = 0;
                    if (subCount != null) subCount.intValue = 0;
                }
                SerializedProperty batchRoot = so.FindProperty("m_StaticBatchRoot");
                if (batchRoot != null)
                {
                    batchRoot.objectReferenceValue = null;
                }
                so.ApplyModifiedPropertiesWithoutUndo();

                Behaviour meshAtlas = mr.GetComponent("MeshAtlas") as Behaviour;
                if (meshAtlas != null)
                {
                    meshAtlas.enabled = false;
                }

                updatedCount++;
            }

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            Debug.Log(
                string.Format(
                    "[BlockStrikeGeometryRecovery] Scene '{0}': linked {1}/{2} static-batched renderers.",
                    manifest.sceneName,
                    updatedCount,
                    manifest.renderers.Length
                )
            );
        }

        private static Mesh BuildMeshFromCombined(Transform targetTransform, RendererEntry entry)
        {
            Mesh combinedMesh = AssetDatabase.LoadAssetAtPath<Mesh>(entry.combinedMeshAssetPath);
            if (combinedMesh == null)
            {
                return null;
            }

            Vector3[] srcVertices = combinedMesh.vertices;
            Vector3[] srcNormals = combinedMesh.normals;
            Color32[] srcColors = combinedMesh.colors32;
            Vector2[] srcUv0 = combinedMesh.uv;
            Vector2[] srcUv1 = combinedMesh.uv2;

            Matrix4x4 localToWorld = targetTransform.localToWorldMatrix;
            Matrix4x4 worldToLocal = targetTransform.worldToLocalMatrix;
            bool invertWinding = localToWorld.determinant < 0f;

            bool hasNormals = srcNormals != null && srcNormals.Length == srcVertices.Length;
            bool hasColors = srcColors != null && srcColors.Length == srcVertices.Length;
            bool hasUv0 = srcUv0 != null && srcUv0.Length == srcVertices.Length;
            bool hasUv1 = srcUv1 != null && srcUv1.Length == srcVertices.Length;

            List<Vector3> outVertices = new List<Vector3>();
            List<Vector3> outNormals = new List<Vector3>();
            List<Color32> outColors = new List<Color32>();
            List<Vector2> outUv0 = new List<Vector2>();
            List<Vector2> outUv1 = new List<Vector2>();
            List<int[]> outSubmeshTris = new List<int[]>();

            for (int s = 0; s < entry.subMeshIndices.Length; s++)
            {
                int subIdx = entry.subMeshIndices[s];
                int[] tris = combinedMesh.GetTriangles(subIdx);
                Dictionary<int, int> remap = new Dictionary<int, int>();
                int[] localTris = new int[tris.Length];

                for (int i = 0; i < tris.Length; i++)
                {
                    int oldV = tris[i];
                    int newV;
                    if (!remap.TryGetValue(oldV, out newV))
                    {
                        newV = outVertices.Count;
                        remap[oldV] = newV;
                        outVertices.Add(worldToLocal.MultiplyPoint3x4(srcVertices[oldV]));
                        if (hasNormals)
                        {
                            Vector3 n = localToWorld.transpose.MultiplyVector(srcNormals[oldV]).normalized;
                            outNormals.Add(n);
                        }
                        if (hasColors) outColors.Add(srcColors[oldV]);
                        if (hasUv0) outUv0.Add(srcUv0[oldV]);
                        if (hasUv1)
                        {
                            Vector2 uv1 = srcUv1[oldV];
                            if (entry.lightmapInfo != null &&
                                entry.lightmapInfo.lightmapST != null &&
                                entry.lightmapInfo.lightmapST.Length == 4 &&
                                Mathf.Abs(entry.lightmapInfo.lightmapST[0]) > 1e-7f &&
                                Mathf.Abs(entry.lightmapInfo.lightmapST[1]) > 1e-7f)
                            {
                                uv1.x = (uv1.x - entry.lightmapInfo.lightmapST[2]) / entry.lightmapInfo.lightmapST[0];
                                uv1.y = (uv1.y - entry.lightmapInfo.lightmapST[3]) / entry.lightmapInfo.lightmapST[1];
                            }
                            outUv1.Add(uv1);
                        }
                    }
                    localTris[i] = newV;
                }

                if (invertWinding)
                {
                    for (int i = 0; i + 2 < localTris.Length; i += 3)
                    {
                        int tmp = localTris[i + 1];
                        localTris[i + 1] = localTris[i + 2];
                        localTris[i + 2] = tmp;
                    }
                }
                outSubmeshTris.Add(localTris);
            }

            Mesh mesh = new Mesh();
            mesh.name = "Renderer-" + entry.rendererId;
            mesh.indexFormat = IndexFormat.UInt16;
            mesh.SetVertices(outVertices);
            if (hasNormals) mesh.SetNormals(outNormals);
            if (hasColors) mesh.SetColors(outColors);
            if (hasUv0) mesh.SetUVs(0, outUv0);
            if (hasUv1) mesh.SetUVs(1, outUv1);
            mesh.subMeshCount = outSubmeshTris.Count;
            for (int s = 0; s < outSubmeshTris.Count; s++)
            {
                mesh.SetTriangles(outSubmeshTris[s], s, false);
            }
            mesh.RecalculateBounds();
            return mesh;
        }

        private static void EnsureFolderExists(string assetFolderPath)
        {
            if (string.IsNullOrEmpty(assetFolderPath))
            {
                return;
            }
            assetFolderPath = assetFolderPath.Replace('\\', '/');
            if (AssetDatabase.IsValidFolder(assetFolderPath))
            {
                return;
            }
            string parent = Path.GetDirectoryName(assetFolderPath).Replace('\\', '/');
            string folderName = Path.GetFileName(assetFolderPath);
            if (!AssetDatabase.IsValidFolder(parent))
            {
                EnsureFolderExists(parent);
            }
            AssetDatabase.CreateFolder(parent, folderName);
        }
    }
}
