using UnityEngine;

[ExecuteAlways]
[DisallowMultipleComponent]
public sealed class LegacyLightmapBinder : MonoBehaviour
{
    public Texture2D lightmapColor;
    public Texture2D[] lightmapColors;
    public MeshRenderer[] renderers;
    public int[] lightmapIndexes;
    public Vector4[] lightmapScaleOffsets;

    private void OnEnable()
    {
        Apply();
    }

    private void Awake()
    {
        Apply();
    }

    private void Start()
    {
        Apply();
    }

    private void OnValidate()
    {
        Apply();
    }

    [ContextMenu("Apply Legacy Lightmaps")]
    public void Apply()
    {
        if (lightmapColors != null && lightmapColors.Length > 0)
        {
            var data = new LightmapData[lightmapColors.Length];
            for (var i = 0; i < lightmapColors.Length; i++)
            {
                data[i] = new LightmapData
                {
                    lightmapColor = lightmapColors[i]
                };
            }
            LightmapSettings.lightmapsMode = LightmapsMode.NonDirectional;
            LightmapSettings.lightmaps = data;
        }
        else if (lightmapColor != null)
        {
            var data = new LightmapData[1];
            data[0] = new LightmapData
            {
                lightmapColor = lightmapColor
            };
            LightmapSettings.lightmapsMode = LightmapsMode.NonDirectional;
            LightmapSettings.lightmaps = data;
        }

        if (renderers == null || renderers.Length == 0)
        {
            return;
        }

        for (var i = 0; i < renderers.Length; i++)
        {
            var renderer = renderers[i];
            if (renderer == null)
            {
                continue;
            }

            var lightmapIndex = 0;
            if (lightmapIndexes != null && i < lightmapIndexes.Length)
            {
                lightmapIndex = lightmapIndexes[i];
            }

            renderer.lightmapIndex = lightmapIndex;
            if (lightmapScaleOffsets != null && i < lightmapScaleOffsets.Length)
            {
                renderer.lightmapScaleOffset = lightmapScaleOffsets[i];
            }
        }
    }
}
