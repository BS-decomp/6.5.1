Shader "MADFINGER/Environment/Cube env map"
{
	Properties
	{
		_MainTex ("Base (RGB) Gloss (A)", 2D) = "white" {}
		_EnvTex ("Cube env tex", Cube) = "black" {}
		_Spread ("Spread", Range(0.1, 0.5)) = 0.5
	}

	SubShader
	{
		Tags { "RenderType"="Opaque" "LightMode"="ForwardBase" }
		LOD 100

		Pass
		{
			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			#include "UnityCG.cginc"

			sampler2D _MainTex;
			samplerCUBE _EnvTex;
			float _Spread;

			struct appdata
			{
				float4 vertex : POSITION;
				float3 normal : NORMAL;
				float2 texcoord : TEXCOORD0;
			};

			struct v2f
			{
				float4 pos : SV_POSITION;
				float2 uv : TEXCOORD0;
				float3 refl : TEXCOORD2;
			};

			v2f vert (appdata v)
			{
				v2f o;
				o.pos = UnityObjectToClipPos(v.vertex);
				o.uv = v.texcoord;
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
				fixed4 c = tex2D(_MainTex, i.uv);
				c.rgb += env * c.a;
				return c;
			}
			ENDCG
		}
	}
}
