using System;
using System.IO;
using System.Net;
using System.Net.Sockets;

namespace BestHTTP.PlatformSupport.TcpClient.General
{
	public class TcpClient : IDisposable
	{
		private enum Properties : uint
		{
			LingerState = 1u,
			NoDelay = 2u,
			ReceiveBufferSize = 4u,
			ReceiveTimeout = 8u,
			SendBufferSize = 0x10u,
			SendTimeout = 0x20u
		}

		private NetworkStream stream;

		private bool active;

		private Socket client;

		private bool disposed;

		private Properties values;

		private int recv_timeout;

		private int send_timeout;

		private int recv_buffer_size;

		private int send_buffer_size;

		private LingerOption linger_state;

		private bool no_delay;

		protected bool Active
		{
			get
			{
				return false;
			}
			set
			{
			}
		}

		public Socket Client
		{
			get
			{
				return null;
			}
			set
			{
			}
		}

		public int Available => 0;

		public bool Connected => false;

		public bool ExclusiveAddressUse
		{
			get
			{
				return false;
			}
			set
			{
			}
		}

		public LingerOption LingerState
		{
			get
			{
				return null;
			}
			set
			{
			}
		}

		public bool NoDelay
		{
			get
			{
				return false;
			}
			set
			{
			}
		}

		public int ReceiveBufferSize
		{
			get
			{
				return 0;
			}
			set
			{
			}
		}

		public int ReceiveTimeout
		{
			get
			{
				return 0;
			}
			set
			{
			}
		}

		public int SendBufferSize
		{
			get
			{
				return 0;
			}
			set
			{
			}
		}

		public int SendTimeout
		{
			get
			{
				return 0;
			}
			set
			{
			}
		}

		public TimeSpan ConnectTimeout { get; set; }

		private void Init(AddressFamily family)
		{
		}

		public TcpClient()
		{
		}

		public TcpClient(AddressFamily family)
		{
		}

		public TcpClient(IPEndPoint localEP)
		{
		}

		public TcpClient(string hostname, int port)
		{
		}

		public bool IsConnected()
		{
			return false;
		}

		internal void SetTcpClient(Socket s)
		{
		}

		public void Close()
		{
		}

		public void Connect(IPEndPoint remoteEP)
		{
		}

		public void Connect(IPAddress address, int port)
		{
		}

		private void SetOptions()
		{
		}

		public void Connect(string hostname, int port)
		{
		}

		public void Connect(IPAddress[] ipAddresses, int port)
		{
		}

		public void EndConnect(IAsyncResult asyncResult)
		{
		}

		public IAsyncResult BeginConnect(IPAddress address, int port, AsyncCallback requestCallback, object state)
		{
			return null;
		}

		public IAsyncResult BeginConnect(IPAddress[] addresses, int port, AsyncCallback requestCallback, object state)
		{
			return null;
		}

		public IAsyncResult BeginConnect(string host, int port, AsyncCallback requestCallback, object state)
		{
			return null;
		}

		void IDisposable.Dispose()
		{
		}

		protected virtual void Dispose(bool disposing)
		{
		}

		~TcpClient()
		{
		}

		public Stream GetStream()
		{
			return null;
		}

		private void CheckDisposed()
		{
		}
	}
}
