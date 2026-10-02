Shader "Hidden/ProBuilder/VertexPicker"
{
	Properties {}

	SubShader
	{
		Tags
		{
			"RenderType"="Transparent"
			"IgnoreProjector"="True"
			"ProBuilderPicker"="VertexPass"
			"DisableBatching"="True"
		}

		Pass
		{
			Name "Vertices"
			Cull Off
			ZTest LEqual
			ZWrite On
			Lighting Off
			Offset -1, -1

			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			#include "UnityCG.cginc"

			struct appdata
			{
				float4 vertex : POSITION;
				float4 color : COLOR;
				float2 texcoord : TEXCOORD0;
				float2 texcoord1 : TEXCOORD1;
			};

			struct v2f
			{
				float4 pos : SV_POSITION;
				float2 uv : TEXCOORD0;
				float4 color : COLOR;
			};

			v2f vert (appdata v)
			{
				v2f o;
				float4 view = float4(UnityObjectToViewPos(v.vertex), 1.0);
				float ortho = 1.0 - UNITY_MATRIX_P[3][3];
				view.xyz *= lerp(0.99, 0.95, ortho);
				o.pos = mul(UNITY_MATRIX_P, view);
				o.pos.xy /= o.pos.w;
				o.pos.xy = (o.pos.xy * 0.5 + 0.5) * _ScreenParams.xy;
				o.pos.xy += v.texcoord1.xy * 3.5;
				o.pos.xy /= _ScreenParams.xy;
				o.pos.xy = (o.pos.xy - 0.5) * 2.0 * o.pos.w;
				o.pos.z -= 0.0001 * ortho;
				o.uv = v.texcoord.xy;
				o.color = v.color;
				return o;
			}

			float4 frag (v2f i) : COLOR
			{
				return i.color;
			}
			ENDCG
		}
	}
}
