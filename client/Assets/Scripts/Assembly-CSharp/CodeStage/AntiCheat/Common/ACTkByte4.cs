using System;
using System.Runtime.InteropServices;

namespace CodeStage.AntiCheat.Common
{
	[Serializable]
	[StructLayout((LayoutKind)0, Size = 4)]
	public struct ACTkByte4
	{
		public byte b1;

		public byte b2;

		public byte b3;

		public byte b4;
	}
}
