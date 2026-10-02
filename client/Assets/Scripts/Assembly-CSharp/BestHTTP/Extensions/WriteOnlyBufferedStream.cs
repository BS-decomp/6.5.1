using System.IO;

namespace BestHTTP.Extensions
{
	public sealed class WriteOnlyBufferedStream : Stream
	{
		private int _position;

		private byte[] buffer;

		private Stream stream;

		public override bool CanRead => false;

		public override bool CanSeek => false;

		public override bool CanWrite => false;

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

		public WriteOnlyBufferedStream(Stream stream, int bufferSize)
		{
		}

		public override void Flush()
		{
		}

		public override void Write(byte[] bufferFrom, int offset, int count)
		{
		}

		public override int Read(byte[] buffer, int offset, int count)
		{
			return 0;
		}

		public override long Seek(long offset, SeekOrigin origin)
		{
			return 0L;
		}

		public override void SetLength(long value)
		{
		}

		protected override void Dispose(bool disposing)
		{
		}
	}
}
