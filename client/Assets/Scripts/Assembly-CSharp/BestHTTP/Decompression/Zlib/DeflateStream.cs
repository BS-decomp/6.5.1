using System.IO;

namespace BestHTTP.Decompression.Zlib
{
	public class DeflateStream : Stream
	{
		internal ZlibBaseStream _baseStream;

		internal Stream _innerStream;

		private bool _disposed;

		public virtual FlushType FlushMode
		{
			get
			{
				return FlushType.None;
			}
			set
			{
			}
		}

		public int BufferSize
		{
			get
			{
				return 0;
			}
			set
			{
			}
		}

		public CompressionStrategy Strategy
		{
			get
			{
				return CompressionStrategy.Default;
			}
			set
			{
			}
		}

		public virtual long TotalIn => 0L;

		public virtual long TotalOut => 0L;

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

		public DeflateStream(Stream stream, CompressionMode mode)
		{
		}

		public DeflateStream(Stream stream, CompressionMode mode, CompressionLevel level)
		{
		}

		public DeflateStream(Stream stream, CompressionMode mode, bool leaveOpen)
		{
		}

		public DeflateStream(Stream stream, CompressionMode mode, CompressionLevel level, bool leaveOpen)
		{
		}

		public DeflateStream(Stream stream, CompressionMode mode, CompressionLevel level, bool leaveOpen, int windowBits)
		{
		}

		protected override void Dispose(bool disposing)
		{
		}

		public override void Flush()
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

		public override void Write(byte[] buffer, int offset, int count)
		{
		}
	}
}
