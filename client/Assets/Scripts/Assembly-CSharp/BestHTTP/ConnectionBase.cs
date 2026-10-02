using System;

namespace BestHTTP
{
	internal abstract class ConnectionBase : IDisposable
	{
		protected DateTime LastProcessTime;

		protected HTTPConnectionRecycledDelegate OnConnectionRecycled;

		private bool IsThreaded;

		public string ServerAddress { get; protected set; }

		public HTTPConnectionStates State { get; protected set; }

		public bool IsFree => false;

		public bool IsActive => false;

		public HTTPRequest CurrentRequest { get; protected set; }

		public virtual bool IsRemovable => false;

		public DateTime StartTime { get; protected set; }

		public DateTime TimedOutStart { get; protected set; }

		public Uri LastProcessedUri { get; protected set; }

		protected bool IsDisposed { get; private set; }

		public ConnectionBase(string serverAddress)
		{
		}

		public ConnectionBase(string serverAddress, bool threaded)
		{
		}

		internal abstract void Abort(HTTPConnectionStates hTTPConnectionStates);

		internal void Process(HTTPRequest request)
		{
		}

		protected virtual void ThreadFunc(object param)
		{
		}

		internal void HandleProgressCallback()
		{
		}

		internal void HandleCallback()
		{
		}

		internal void Recycle(HTTPConnectionRecycledDelegate onConnectionRecycled)
		{
		}

		protected void RecycleNow()
		{
		}

		public void Dispose()
		{
		}

		protected virtual void Dispose(bool disposing)
		{
		}

		~ConnectionBase()
		{
		}
	}
}
