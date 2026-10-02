using System.IO;

namespace BestHTTP.Extensions
{
	public sealed class BufferPoolMemoryStream : Stream
	{
		private bool canWrite;

		private bool allowGetBuffer;

		private int capacity;

		private int length;

		private byte[] internalBuffer;

		private int initialIndex;

		private bool expandable;

		private bool streamClosed;

		private int position;

		private int dirty_bytes;

		public override bool CanRead => false;

		public override bool CanSeek => false;

		public override bool CanWrite => false;

		public int Capacity
		{
			get
			{
				return 0;
			}
			set
			{
			}
		}

		public override long Length => 0L;

		public override long Position
		{
			get
			{
				return 0L;
			}
			set
			{
			}
		}

		public BufferPoolMemoryStream()
		{
		}

		public BufferPoolMemoryStream(int capacity)
		{
		}

		public BufferPoolMemoryStream(byte[] buffer)
		{
		}

		public BufferPoolMemoryStream(byte[] buffer, bool writable)
		{
		}

		public BufferPoolMemoryStream(byte[] buffer, int index, int count)
		{
		}

		public BufferPoolMemoryStream(byte[] buffer, int index, int count, bool writable)
		{
		}

		public BufferPoolMemoryStream(byte[] buffer, int index, int count, bool writable, bool publiclyVisible)
		{
		}

		private void InternalConstructor(byte[] buffer, int index, int count, bool writable, bool publicallyVisible)
		{
		}

		private void CheckIfClosedThrowDisposed()
		{
		}

		protected override void Dispose(bool disposing)
		{
		}

		public override void Flush()
		{
		}

		public byte[] GetBuffer()
		{
			return null;
		}

		public override int Read(byte[] buffer, int offset, int count)
		{
			return 0;
		}

		public override int ReadByte()
		{
			return 0;
		}

		public override long Seek(long offset, SeekOrigin loc)
		{
			return 0L;
		}

		private int CalculateNewCapacity(int minimum)
		{
			return 0;
		}

		private void Expand(int newSize)
		{
		}

		public override void SetLength(long value)
		{
		}

		public byte[] ToArray()
		{
			return null;
		}

		public byte[] ToArray(bool canBeLarger)
		{
			return null;
		}

		public override void Write(byte[] buffer, int offset, int count)
		{
		}

		public override void WriteByte(byte value)
		{
		}

		public void WriteTo(Stream stream)
		{
		}
	}
}
