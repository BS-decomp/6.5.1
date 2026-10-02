Shader "Vertigo/GaussianBlur"
{
	Properties
	{
		_Color ("Main Color", Color) = (1,1,1,1)
		_blurSizeXY ("BlurSizeXY", Range(0, 10)) = 0
	}

	SubShader
	{
		Tags { "Queue"="Transparent" }

		GrabPass {}

		Pass
		{
			Tags { "Queue"="Transparent" }
			ZWrite Off

			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag_h
			#include "UnityCG.cginc"

			sampler2D _GrabTexture;
			float _blurSizeXY;
			float4 _Color;

			struct appdata
			{
				float4 vertex : POSITION;
			};

			struct v2f
			{
				float4 pos : SV_POSITION;
				float4 uvgrab : TEXCOORD0;
			};

			v2f vert (appdata v)
			{
				v2f o;
				o.pos = UnityObjectToClipPos(v.vertex);
				o.uvgrab = ComputeGrabScreenPos(o.pos);
				return o;
			}

			half4 frag_h (v2f i) : SV_Target
			{
				float2 uv = i.uvgrab.xy / i.uvgrab.w;
				half3 sum = half3(0, 0, 0);
				sum += tex2D(_GrabTexture, float2(uv.x - 4.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.0162162162;
				sum += tex2D(_GrabTexture, float2(uv.x - 3.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.0540540541;
				sum += tex2D(_GrabTexture, float2(uv.x - 2.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.1216216216;
				sum += tex2D(_GrabTexture, float2(uv.x - 1.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.1945945946;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y)).rgb * 0.2270270270;
				sum += tex2D(_GrabTexture, float2(uv.x + 1.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.1945945946;
				sum += tex2D(_GrabTexture, float2(uv.x + 2.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.1216216216;
				sum += tex2D(_GrabTexture, float2(uv.x + 3.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.0540540541;
				sum += tex2D(_GrabTexture, float2(uv.x + 4.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.0162162162;
				return half4(sum, 1.0) * _Color;
			}
			ENDCG
		}

		GrabPass {}

		Pass
		{
			Tags { "Queue"="Transparent" }
			ZWrite Off

			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag_v
			#include "UnityCG.cginc"

			sampler2D _GrabTexture;
			float _blurSizeXY;
			float4 _Color;

			struct appdata
			{
				float4 vertex : POSITION;
			};

			struct v2f
			{
				float4 pos : SV_POSITION;
				float4 uvgrab : TEXCOORD0;
			};

			v2f vert (appdata v)
			{
				v2f o;
				o.pos = UnityObjectToClipPos(v.vertex);
				o.uvgrab = ComputeGrabScreenPos(o.pos);
				return o;
			}

			half4 frag_v (v2f i) : SV_Target
			{
				float2 uv = i.uvgrab.xy / i.uvgrab.w;
				half3 sum = half3(0, 0, 0);
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y - 4.0 * _blurSizeXY * 0.0005)).rgb * 0.0162162162;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y - 3.0 * _blurSizeXY * 0.0005)).rgb * 0.0540540541;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y - 2.0 * _blurSizeXY * 0.0005)).rgb * 0.1216216216;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y - 1.0 * _blurSizeXY * 0.0005)).rgb * 0.1945945946;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y)).rgb * 0.2270270270;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y + 1.0 * _blurSizeXY * 0.0005)).rgb * 0.1945945946;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y + 2.0 * _blurSizeXY * 0.0005)).rgb * 0.1216216216;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y + 3.0 * _blurSizeXY * 0.0005)).rgb * 0.0540540541;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y + 4.0 * _blurSizeXY * 0.0005)).rgb * 0.0162162162;
				return half4(sum, 1.0) * _Color;
			}
			ENDCG
		}

		GrabPass {}

		Pass
		{
			Tags { "Queue"="Transparent" }
			ZWrite Off

			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag_h
			#include "UnityCG.cginc"

			sampler2D _GrabTexture;
			float _blurSizeXY;
			float4 _Color;

			struct appdata
			{
				float4 vertex : POSITION;
			};

			struct v2f
			{
				float4 pos : SV_POSITION;
				float4 uvgrab : TEXCOORD0;
			};

			v2f vert (appdata v)
			{
				v2f o;
				o.pos = UnityObjectToClipPos(v.vertex);
				o.uvgrab = ComputeGrabScreenPos(o.pos);
				return o;
			}

			half4 frag_h (v2f i) : SV_Target
			{
				float2 uv = i.uvgrab.xy / i.uvgrab.w;
				half3 sum = half3(0, 0, 0);
				sum += tex2D(_GrabTexture, float2(uv.x - 4.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.0162162162;
				sum += tex2D(_GrabTexture, float2(uv.x - 3.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.0540540541;
				sum += tex2D(_GrabTexture, float2(uv.x - 2.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.1216216216;
				sum += tex2D(_GrabTexture, float2(uv.x - 1.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.1945945946;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y)).rgb * 0.2270270270;
				sum += tex2D(_GrabTexture, float2(uv.x + 1.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.1945945946;
				sum += tex2D(_GrabTexture, float2(uv.x + 2.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.1216216216;
				sum += tex2D(_GrabTexture, float2(uv.x + 3.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.0540540541;
				sum += tex2D(_GrabTexture, float2(uv.x + 4.0 * _blurSizeXY * 0.0005, uv.y)).rgb * 0.0162162162;
				return half4(sum, 1.0) * _Color;
			}
			ENDCG
		}

		GrabPass {}

		Pass
		{
			Tags { "Queue"="Transparent" }
			ZWrite Off

			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag_v
			#include "UnityCG.cginc"

			sampler2D _GrabTexture;
			float _blurSizeXY;
			float4 _Color;

			struct appdata
			{
				float4 vertex : POSITION;
			};

			struct v2f
			{
				float4 pos : SV_POSITION;
				float4 uvgrab : TEXCOORD0;
			};

			v2f vert (appdata v)
			{
				v2f o;
				o.pos = UnityObjectToClipPos(v.vertex);
				o.uvgrab = ComputeGrabScreenPos(o.pos);
				return o;
			}

			half4 frag_v (v2f i) : SV_Target
			{
				float2 uv = i.uvgrab.xy / i.uvgrab.w;
				half3 sum = half3(0, 0, 0);
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y - 4.0 * _blurSizeXY * 0.0005)).rgb * 0.0162162162;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y - 3.0 * _blurSizeXY * 0.0005)).rgb * 0.0540540541;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y - 2.0 * _blurSizeXY * 0.0005)).rgb * 0.1216216216;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y - 1.0 * _blurSizeXY * 0.0005)).rgb * 0.1945945946;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y)).rgb * 0.2270270270;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y + 1.0 * _blurSizeXY * 0.0005)).rgb * 0.1945945946;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y + 2.0 * _blurSizeXY * 0.0005)).rgb * 0.1216216216;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y + 3.0 * _blurSizeXY * 0.0005)).rgb * 0.0540540541;
				sum += tex2D(_GrabTexture, float2(uv.x, uv.y + 4.0 * _blurSizeXY * 0.0005)).rgb * 0.0162162162;
				return half4(sum, 1.0) * _Color;
			}
			ENDCG
		}
	}
}
