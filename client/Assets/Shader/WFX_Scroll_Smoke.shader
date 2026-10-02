Shader "WFX/Scroll/Smoke"
{
	Properties
	{
		_TintColor ("Tint Color", Color) = (0.5, 0.5, 0.5, 0.5)
		_MainTex ("Texture", 2D) = "white" {}
		_ScrollSpeed ("Scroll Speed", Float) = 2.0
	}

	Category
	{
		Tags { "Queue"="Transparent" "IgnoreProjector"="True" "RenderType"="Transparent" }
		Blend DstColor SrcAlpha
		Cull Off
		Lighting Off
		ZWrite Off

		SubShader
		{
			Pass
			{
				CGPROGRAM
				#pragma vertex vert
				#pragma fragment frag
				#include "UnityCG.cginc"

				sampler2D _MainTex;
				fixed4 _TintColor;
				float _ScrollSpeed;

				struct appdata_t
				{
					float4 vertex : POSITION;
					half2 texcoord : TEXCOORD0;
					fixed4 color : COLOR;
				};

				struct v2f
				{
					float4 vertex : SV_POSITION;
					float2 texcoord : TEXCOORD0;
					fixed4 color : COLOR;
				};

				v2f vert (appdata_t v)
				{
					v2f o;
					o.vertex = UnityObjectToClipPos(v.vertex);
					o.texcoord = v.texcoord;
					o.color = v.color;
					return o;
				}

				fixed4 frag (v2f i) : SV_Target
				{
					float2 scrolledUV = i.texcoord - float2(0.0, fmod(_Time.x * _ScrollSpeed, 1.0));
					fixed4 col;
					col.rgb = tex2D(_MainTex, scrolledUV).rgb * i.color.rgb * _TintColor.rgb;
					col.a = tex2D(_MainTex, i.texcoord).a * i.color.a;
					col = lerp(fixed4(0.5, 0.5, 0.5, 0.5), col, col.a);
					return col;
				}
				ENDCG
			}
		}
	}
}
