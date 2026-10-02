Shader "Mobile/VertexLit" {
Properties {
 _MainTex ("Base (RGB)", 2D) = "white" { }
}
SubShader { 
 LOD 80
 Tags { "RenderType"="Opaque" }
 Pass {
  Tags { "LIGHTMODE"="Vertex" "RenderType"="Opaque" }
  Material {
   Ambient (1,1,1,1)
   Diffuse (1,1,1,1)
  }
  Lighting On
  SetTexture [_MainTex] { combine texture * primary DOUBLE, texture * primary }
 }
 Pass {
  Tags { "LIGHTMODE"="VertexLM" "RenderType"="Opaque" }
  CGPROGRAM
  #pragma vertex vert_bs
  #pragma fragment frag_bs
  #pragma multi_compile_fog
  #include "UnityCG.cginc"

  sampler2D _MainTex;
  float4 _MainTex_ST;

  struct appdata_bs
  {
   float4 vertex : POSITION;
   float2 uv0 : TEXCOORD0;
   float2 uv1 : TEXCOORD1;
  };

  struct v2f_bs
  {
   float4 pos : SV_POSITION;
   float2 uv : TEXCOORD0;
   float2 lmuv : TEXCOORD1;
   UNITY_FOG_COORDS(2)
  };

  v2f_bs vert_bs(appdata_bs v)
  {
   v2f_bs o;
   o.pos = UnityObjectToClipPos(v.vertex);
   o.uv = TRANSFORM_TEX(v.uv0, _MainTex);
   o.lmuv = v.uv1.xy * unity_LightmapST.xy + unity_LightmapST.zw;
   UNITY_TRANSFER_FOG(o, o.pos);
   return o;
  }

  fixed4 frag_bs(v2f_bs i) : SV_Target
  {
   fixed4 albedo = tex2D(_MainTex, i.uv);
   half3 lm = 2.0h * UNITY_SAMPLE_TEX2D(unity_Lightmap, i.lmuv).rgb;
   fixed4 col = fixed4(albedo.rgb * lm, albedo.a);
   UNITY_APPLY_FOG(i.fogCoord, col);
   return col;
  }
  ENDCG
 }
 Pass {
  Tags { "LIGHTMODE"="VertexLMRGBM" "RenderType"="Opaque" }
  CGPROGRAM
  #pragma vertex vert_bs
  #pragma fragment frag_bs
  #pragma multi_compile_fog
  #include "UnityCG.cginc"

  sampler2D _MainTex;
  float4 _MainTex_ST;

  struct appdata_bs
  {
   float4 vertex : POSITION;
   float2 uv0 : TEXCOORD0;
   float2 uv1 : TEXCOORD1;
  };

  struct v2f_bs
  {
   float4 pos : SV_POSITION;
   float2 uv : TEXCOORD0;
   float2 lmuv : TEXCOORD1;
   UNITY_FOG_COORDS(2)
  };

  v2f_bs vert_bs(appdata_bs v)
  {
   v2f_bs o;
   o.pos = UnityObjectToClipPos(v.vertex);
   o.uv = TRANSFORM_TEX(v.uv0, _MainTex);
   o.lmuv = v.uv1.xy * unity_LightmapST.xy + unity_LightmapST.zw;
   UNITY_TRANSFER_FOG(o, o.pos);
   return o;
  }

  fixed4 frag_bs(v2f_bs i) : SV_Target
  {
   fixed4 albedo = tex2D(_MainTex, i.uv);
   half3 lm = 2.0h * UNITY_SAMPLE_TEX2D(unity_Lightmap, i.lmuv).rgb;
   fixed4 col = fixed4(albedo.rgb * lm, albedo.a);
   UNITY_APPLY_FOG(i.fogCoord, col);
   return col;
  }
  ENDCG
 }
 Pass {
  Name "ShadowCaster"
  Tags { "LIGHTMODE"="SHADOWCASTER" "SHADOWSUPPORT"="true" "RenderType"="Opaque" }
  Cull Off
  Offset 1, 1
  CGPROGRAM
  #pragma vertex vert
  #pragma fragment frag
  #pragma multi_compile_shadowcaster
  #include "UnityCG.cginc"

  struct v2f {
   V2F_SHADOW_CASTER;
   UNITY_VERTEX_OUTPUT_STEREO
  };

  v2f vert( appdata_base v )
  {
   v2f o;
   UNITY_SETUP_INSTANCE_ID(v);
   UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
   TRANSFER_SHADOW_CASTER_NORMALOFFSET(o)
   return o;
  }

  float4 frag( v2f i ) : SV_Target
  {
   SHADOW_CASTER_FRAGMENT(i)
  }
  ENDCG
 }
}
}
