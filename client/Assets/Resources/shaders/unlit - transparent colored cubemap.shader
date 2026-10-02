Shader "Unlit/Transparent Colored Cubemap"
{
	Properties
	{
		_MainTex ("Base (RGB), Alpha (A)", 2D) = "black" {}
		_EnvTex ("Cube env tex", Cube) = "black" {}
	}

	SubShader
	{
		LOD 200

		Tags
		{
			"Queue" = "Transparent"
			"IgnoreProjector" = "True"
			"RenderType" = "Transparent"
		}

		Pass
		{
			Cull Off
			Lighting Off
			ZWrite Off
			Fog { Mode Off }
			Offset -1, -1
			Blend SrcAlpha OneMinusSrcAlpha

			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			#include "UnityCG.cginc"

			sampler2D _MainTex;
			samplerCUBE _EnvTex;

			struct appdata_t
			{
				float4 vertex : POSITION;
				float3 normal : NORMAL;
				float2 texcoord : TEXCOORD0;
				fixed4 color : COLOR;
			};

			struct v2f
			{
				float4 vertex : SV_POSITION;
				half2 texcoord : TEXCOORD0;
				fixed4 color : COLOR;
				float3 refl : TEXCOORD2;
			};

			v2f vert (appdata_t v)
			{
				v2f o;
				o.vertex = UnityObjectToClipPos(v.vertex);
				o.texcoord = v.texcoord;
				o.color = v.color;
				float3 worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
				float3 viewDir = _WorldSpaceCameraPos.xyz - worldPos;
				float3 worldNormal = mul((float3x3)unity_ObjectToWorld, v.normal);
				float3 r = reflect(-viewDir, worldNormal);
				r.x = -r.x;
				o.refl = r;
				return o;
			}

			fixed4 frag (v2f i) : SV_Target
			{
				fixed3 env = texCUBE(_EnvTex, i.refl).rgb;
				fixed4 col = tex2D(_MainTex, i.texcoord) * i.color;
				col.rgb += env * col.a;
				return col;
			}
			ENDCG
		}
	}

	SubShader
	{
		LOD 100

		Tags
		{
			"Queue" = "Transparent"
			"IgnoreProjector" = "True"
			"RenderType" = "Transparent"
		}

		Pass
		{
			Cull Off
			Lighting Off
			ZWrite Off
			Fog { Mode Off }
			Offset -1, -1
			ColorMask RGB
			Blend SrcAlpha OneMinusSrcAlpha
			ColorMaterial AmbientAndDiffuse

			SetTexture [_MainTex]
			{
				Combine Texture * Primary
			}
		}
	}
}
