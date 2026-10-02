using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using BestHTTP.Extensions;

namespace BestHTTP.ServerSentEvents
{
	public class EventSource : IHeartbeat
	{
		private States _state;

		[CompilerGenerated]
		private OnGeneralEventDelegate m_OnOpen;

		[CompilerGenerated]
		private OnMessageDelegate m_OnMessage;

		[CompilerGenerated]
		private OnErrorDelegate m_OnError;

		[CompilerGenerated]
		private OnRetryDelegate m_OnRetry;

		[CompilerGenerated]
		private OnGeneralEventDelegate m_OnClosed;

		[CompilerGenerated]
		private OnStateChangedDelegate m_OnStateChanged;

		private Dictionary<string, OnEventDelegate> EventTable;

		private byte RetryCount;

		private DateTime RetryCalled;

		public Uri Uri { get; private set; }

		public States State
		{
			get
			{
				return States.Initial;
			}
			private set
			{
			}
		}

		public TimeSpan ReconnectionTime { get; set; }

		public string LastEventId { get; private set; }

		public HTTPRequest InternalRequest { get; private set; }

		public event OnGeneralEventDelegate OnOpen
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public event OnMessageDelegate OnMessage
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public event OnErrorDelegate OnError
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public event OnRetryDelegate OnRetry
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public event OnGeneralEventDelegate OnClosed
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public event OnStateChangedDelegate OnStateChanged
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public EventSource(Uri uri)
		{
		}

		public void Open()
		{
		}

		public void Close()
		{
		}

		public void On(string eventName, OnEventDelegate action)
		{
		}

		public void Off(string eventName)
		{
		}

		private void CallOnError(string error, string msg)
		{
		}

		private bool CallOnRetry()
		{
			return false;
		}

		private void SetClosed(string msg)
		{
		}

		private void Retry()
		{
		}

		private void OnUpgraded(HTTPRequest originalRequest, HTTPResponse response)
		{
		}

		private void OnRequestFinished(HTTPRequest req, HTTPResponse resp)
		{
		}

		private void OnMessageReceived(EventSourceResponse resp, Message message)
		{
		}

		void IHeartbeat.OnHeartbeatUpdate(TimeSpan dif)
		{
		}
	}
}
