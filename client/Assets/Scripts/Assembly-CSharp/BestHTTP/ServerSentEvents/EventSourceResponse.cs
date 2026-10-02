using System;
using System.Collections.Generic;
using System.IO;

namespace BestHTTP.ServerSentEvents
{
	public sealed class EventSourceResponse : HTTPResponse, IProtocol
	{
		public Action<EventSourceResponse, Message> OnMessage;

		public Action<EventSourceResponse> OnClosed;

		private object FrameLock;

		private byte[] LineBuffer;

		private int LineBufferPos;

		private Message CurrentMessage;

		private List<Message> CompletedMessages;

		public bool IsClosed { get; private set; }

		public EventSourceResponse(HTTPRequest request, Stream stream, bool isStreamed, bool isFromCache)
			: base(null, null, isStreamed: false, isFromCache: false)
		{
		}

		public override bool Receive(int forceReadRawContentLength = -1, bool readPayloadData = true)
		{
			return false;
		}

		internal void StartReceive()
		{
		}

		private void ReceiveThreadFunc(object param)
		{
		}

		private new void ReadChunked(Stream stream)
		{
		}

		private new void ReadRaw(Stream stream, long contentLength)
		{
		}

		public void FeedData(byte[] buffer, int count)
		{
		}

		private void ParseLine(byte[] buffer, int count)
		{
		}

		void IProtocol.HandleEvents()
		{
		}
	}
}
