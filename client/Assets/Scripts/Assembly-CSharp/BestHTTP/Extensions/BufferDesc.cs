using System;

namespace BestHTTP.Extensions
{
	internal struct BufferDesc
	{
		public static readonly BufferDesc Empty;

		public byte[] buffer;

		public DateTime released;

		public BufferDesc(byte[] buff)
		{
			buffer = null;
			released = default;
		}
	}
}
