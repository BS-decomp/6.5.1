using System.Collections.Generic;

namespace BestHTTP.Extensions
{
	internal struct BufferStore
	{
		public readonly long Size;

		public List<BufferDesc> buffers;

		public BufferStore(long size)
		{
			Size = 0L;
			buffers = null;
		}

		public BufferStore(long size, byte[] buffer)
		{
			Size = 0L;
			buffers = null;
		}
	}
}
