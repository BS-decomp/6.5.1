using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using UnityEngine;

namespace CodeStage.AntiCheat.ObscuredTypes
{
	[Serializable]
	[StructLayout((LayoutKind)0, Size = 40)]
	public struct ObscuredQuaternion
	{
		[Serializable]
		[StructLayout((LayoutKind)0, Size = 16)]
		public struct RawEncryptedQuaternion
		{
			public int x;

			public int y;

			public int z;

			public int w;
		}

		private static int cryptoKey;

		private static readonly Quaternion initialFakeValue;

		[SerializeField]
		private int currentCryptoKey;

		[SerializeField]
		private RawEncryptedQuaternion hiddenValue;

		[SerializeField]
		private Quaternion fakeValue;

		[SerializeField]
		private bool inited;
		public static ObscuredQuaternion IJJJJIJIJIJIIJIJJJJIIJIJIIIIJJJIIIJJJIIIIIJJIIJ(Quaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
		{
			return default;
		}

		public static RawEncryptedQuaternion IIJIIJIJIJJIJJJIIIJIIJIJIJIIIIIIIJJJIIIIIIJIIJJ(Quaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
		{
			return default;
		}

		public void JJIIJJIIIIIIJIJIJJIJIJJIJIJIIJJJIIJJIIIJJIIJJII()
		{
		}

		public void JIIJJIIIJJIIIIIIJJIJIJJJIJJIIIJJIIIJIIIJIJIJJJJ()
		{
		}

		public RawEncryptedQuaternion JJJJJJIIIJJIIIJJJJJJJJJJJIIJIJJIIIJIIIJIJJJJJII()
		{
			return default;
		}

		private ObscuredQuaternion(RawEncryptedQuaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
		{
			currentCryptoKey = 0;
			hiddenValue = default;
			fakeValue = default;
			inited = false;
		}

		public void JJJIIJIJJJIIJJJJJIJJIJIIJJJIJJIIJIJJJIJJJIIJJJI(RawEncryptedQuaternion JIJIIJJJJJJJIJIJJJJIIJJIJIIIIJJJIIJIIIIJJIIIJII)
		{
		}

		private bool JIJIJJJJIIIIIIIJIJIIJIIIJIIJJIJJIIJIJJIJIIJIIJI(Quaternion IIJJIIIIIJIJJIJIJIJJJJIIIIJIIIIJIIIJJJJJJIJJIIJ, Quaternion JIJJJIIJIJIIIIJIJIIJJJJJIIJIIIIIIIIIIIJJJJIJJII)
		{
			return false;
		}

		private Quaternion IJIJJJIJJJIIIJJJIJIIIIIIIJIIIJJJIIJIJIIJJJIJJJJ()
		{
			return default;
		}

		public void JIJIIJJJJIIJJJIIIIIJIJJIIIJIIJJIIJJJIIJJJIJJIJI()
		{
		}

		public void IIIJJJIJIIIIIJIJIIJIJJJIJJJIJJJJIIJJJIIIIIJJIJJ()
		{
		}
		public static implicit operator Quaternion(ObscuredQuaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
		{
			return default;
		}

		public static Quaternion IIIIIJIIIJIJIIJJIIIIJJIIJJJIIIIJJIIJIJIJIJJIJIJ(RawEncryptedQuaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
		{
			return default;
		}

		public string JJJJIJJIIJJIIIIJJJIIJJIJIIJJJJIJJJJJIIJIJJIJIII()
		{
			return null;
		}

		public void JJIJJIJJJIJJJJJIJIJIIJJJIJIIIIIIJJJIIIJJJJIJJJJ(RawEncryptedQuaternion JIJIIJJJJJJJIJIJJJJIIJJIJIIIIJJJIIJIIIIJJIIIJII)
		{
		}

		public static Quaternion IJIJJJJJIIJJJJJIIJIJJJJIJIJJJIJJIJIIJJIJJIIJIIJ(RawEncryptedQuaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI, int IIIJIJJJIIIIJJIIJJJIJJJIIIJJIJIIJJIJIJJJIIJIJIJ)
		{
			return default;
		}

		private Quaternion JIJJIIIJJJIJIIJIJJIIIIJJJIIJIIJIIIJIIJIIJIIIIIJ()
		{
			return default;
		}

		public static RawEncryptedQuaternion JIIJJJJIJIJIJIIIJJJJIIJIIJIJJJJIJJJIIIJJIJJJIII(Quaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI, int IIIJIJJJIIIIJJIIJJJIJJJIIIJJIJIIJJIJIJJJIIJIJIJ)
		{
			return default;
		}

		public void IJJIIIJIJIIJIIJIJIIJJIJJIIIJJJJIJIIJIJJIJIIIIJI(RawEncryptedQuaternion JIJIIJJJJJJJIJIJJJJIIJJIJIIIIJJJIIJIIIIJJIIIJII)
		{
		}

		public static void IJIJJJIJJIIIIIIIJIJIJJIIIIIIJIIIIIIJIIIJJJJJJIJ(int JJJIIIIJJJIIJIIJIJIJJIIIIJIIJIIIIJJIIIJJJJJJIIJ)
		{
		}

		public void JJJJJIIJJJJJIIJJJJJJJJIIJIIIJJIIJIJIIJIJIJIJJJI()
		{
		}

		private bool IJJJIJJIJIIJIIJJIJIIIIIIIJIJJIIJJIIJJJJJJIJJIIJ(Quaternion IIJJIIIIIJIJJIJIJIJJJJIIIIJIIIIJIIIJJJJJJIJJIIJ, Quaternion JIJJJIIJIJIIIIJIJIIJJJJJIIJIIIIIIIIIIIJJJJIJJII)
		{
			return false;
		}

		public string JIJJJIJJIJIIIIIJIIIJJJIIJIJIIIIJIJJIIJJIIIJIJJJ(string JJJJJIIJIJJIJJIJIJIIJIJJJIIIJJIJJIIIIIIJJIIIJJI)
		{
			return null;
		}
		public static implicit operator ObscuredQuaternion(Quaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
		{
			return default;
		}

		public static Quaternion IJIJJJJJIIJJJJJIIJIJJJJIJIJJJIJJIJIIJJIJJIIJIIJ(RawEncryptedQuaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
		{
			return default;
		}

		public override int GetHashCode()
		{
			return 0;
		}

		public string IJJIJIJJIJIIIJJIJJIIJJIIIJJIIIJJIIIJJIJIIIIJJIJ(string JJJJJIIJIJJIJJIJIJIIJIJJJIIIJJIJJIIIIIIJJIIIJJI)
		{
			return null;
		}

		public static RawEncryptedQuaternion JIIJJJJIJIJIJIIIJJJJIIJIIJIJJJJIJJJIIIJJIJJJIII(Quaternion JIIJJIIJIIJIJJJJIJIIIJIIIIJJJIIIIJIJIIJJIIJIIJI)
		{
			return default;
		}

		public override string ToString()
		{
			return null;
		}

		private Quaternion IIIJJIJJJJJJJIIIJIIIJIJJIJJIJIIJJIIIIJJIJIJIJJJ()
		{
			return default;
		}
	}
}
