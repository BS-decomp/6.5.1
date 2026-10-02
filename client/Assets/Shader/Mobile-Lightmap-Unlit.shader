Shader "Mobile/Unlit (Supports Lightmap)" {
Properties {
 _MainTex ("Base (RGB)", 2D) = "white" { }
}
SubShader { 
 LOD 100
 Tags { "RenderType"="Opaque" }
 Pass {
  Tags { "LIGHTMODE"="Vertex" "RenderType"="Opaque" }
  SetTexture [_MainTex] { combine texture }
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
  Name "Meta"
  Tags { "LIGHTMODE"="Meta" "RenderType"="Opaque" }
  Cull Off
  CGPROGRAM
  #pragma vertex vert_meta
  #pragma fragment frag_meta
  #include "UnityCG.cginc"
  #include "UnityMetaPass.cginc"

  sampler2D _MainTex;
  float4 _MainTex_ST;

  struct v2f
  {
   float4 pos : SV_POSITION;
   float2 uv : TEXCOORD0;
  };

  v2f vert_meta(appdata_full v)
  {
   v2f o;
   o.pos = UnityMetaVertexPosition(v.vertex, v.texcoord1.xy, v.texcoord2.xy, unity_LightmapST, unity_DynamicLightmapST);
   o.uv = TRANSFORM_TEX(v.texcoord, _MainTex);
   return o;
  }

  float4 frag_meta(v2f i) : SV_Target
  {
   UnityMetaInput metaIN;
   UNITY_INITIALIZE_OUTPUT(UnityMetaInput, metaIN);
   metaIN.Albedo = tex2D(_MainTex, i.uv).rgb;
   metaIN.Emission = 0;
   return UnityMetaFragment(metaIN);
  }
  ENDCG
 }
}
}
