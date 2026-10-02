Shader "Mobile/VertexLit (Only Directional Lights)" {
Properties {
 _MainTex ("Base (RGB)", 2D) = "white" {}
}
SubShader {
 Tags { "RenderType"="Opaque" }
 LOD 80

 Pass {
  Name "FORWARD"
  Tags { "LightMode" = "ForwardBase" }
  CGPROGRAM
  #pragma vertex vert_surf
  #pragma fragment frag_surf
  #pragma target 2.0
  #pragma multi_compile_fwdbase
  #pragma multi_compile_fog
  #include "HLSLSupport.cginc"
  #include "UnityCG.cginc"
  #include "Lighting.cginc"
  #include "AutoLight.cginc"

  inline float3 LightingLambertVS (float3 normal, float3 lightDir)
  {
   fixed diff = max (0, dot (normal, lightDir));
   return _LightColor0.rgb * diff;
  }

  sampler2D _MainTex;
  float4 _MainTex_ST;

  struct v2f_surf {
   float4 pos : SV_POSITION;
   float2 pack0 : TEXCOORD0;
   #ifndef LIGHTMAP_ON
   fixed3 normal : TEXCOORD1;
   fixed3 vlight : TEXCOORD2;
   SHADOW_COORDS(3)
   UNITY_FOG_COORDS(4)
   #else
   float2 lmap : TEXCOORD1;
   SHADOW_COORDS(2)
   UNITY_FOG_COORDS(3)
   #endif
   UNITY_VERTEX_INPUT_INSTANCE_ID
   UNITY_VERTEX_OUTPUT_STEREO
  };

  v2f_surf vert_surf (appdata_full v)
  {
   v2f_surf o;
   UNITY_INITIALIZE_OUTPUT(v2f_surf,o);
   UNITY_SETUP_INSTANCE_ID(v);
   UNITY_TRANSFER_INSTANCE_ID(v,o);
   UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
   o.pos = UnityObjectToClipPos(v.vertex);
   o.pack0.xy = TRANSFORM_TEX(v.texcoord, _MainTex);
   #ifdef LIGHTMAP_ON
   o.lmap.xy = v.texcoord1.xy * unity_LightmapST.xy + unity_LightmapST.zw;
   #else
   float3 worldN = UnityObjectToWorldNormal(v.normal);
   o.normal = worldN;
   o.vlight = ShadeSH9 (float4(worldN,1.0));
   o.vlight += LightingLambertVS (worldN, _WorldSpaceLightPos0.xyz);
   #endif
   TRANSFER_SHADOW(o);
   UNITY_TRANSFER_FOG(o,o.pos);
   return o;
  }

  fixed4 frag_surf (v2f_surf IN) : SV_Target
  {
   UNITY_SETUP_INSTANCE_ID(IN);
   fixed4 albedo = tex2D(_MainTex, IN.pack0.xy);
   fixed atten = SHADOW_ATTENUATION(IN);
   fixed4 c = 0;
   #ifndef LIGHTMAP_ON
   c.rgb = albedo.rgb * IN.vlight * atten;
   #else
   half3 lm = 2.0h * UNITY_SAMPLE_TEX2D(unity_Lightmap, IN.lmap.xy).rgb;
   #ifdef SHADOWS_SCREEN
   c.rgb = albedo.rgb * min(lm, atten * 2.0h);
   #else
   c.rgb = albedo.rgb * lm;
   #endif
   #endif
   c.a = albedo.a;
   UNITY_APPLY_FOG(IN.fogCoord, c);
   UNITY_OPAQUE_ALPHA(c.a);
   return c;
  }
  ENDCG
 }
 Pass {
  Name "ShadowCaster"
  Tags { "LightMode" = "ShadowCaster" }
  ZWrite On ZTest LEqual

  CGPROGRAM
  #pragma vertex vert_surf
  #pragma fragment frag_surf
  #pragma target 2.0
  #pragma multi_compile_shadowcaster
  #include "HLSLSupport.cginc"
  #include "UnityCG.cginc"
  #include "Lighting.cginc"

  struct v2f_surf {
   V2F_SHADOW_CASTER;
   UNITY_VERTEX_INPUT_INSTANCE_ID
   UNITY_VERTEX_OUTPUT_STEREO
  };

  v2f_surf vert_surf (appdata_full v)
  {
   v2f_surf o;
   UNITY_INITIALIZE_OUTPUT(v2f_surf,o);
   UNITY_SETUP_INSTANCE_ID(v);
   UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
   TRANSFER_SHADOW_CASTER_NORMALOFFSET(o)
   return o;
  }

  fixed4 frag_surf (v2f_surf IN) : SV_Target
  {
   SHADOW_CASTER_FRAGMENT(IN)
  }
  ENDCG
 }
}
FallBack "Mobile/VertexLit"
}
