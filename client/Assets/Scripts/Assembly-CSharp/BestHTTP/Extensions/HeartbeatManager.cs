using System;
using System.Collections.Generic;

namespace BestHTTP.Extensions
{
	public sealed class HeartbeatManager
	{
		private List<IHeartbeat> Heartbeats;

		private IHeartbeat[] UpdateArray;

		private DateTime LastUpdate;

		public void Subscribe(IHeartbeat heartbeat)
		{
		}

		public void Unsubscribe(IHeartbeat heartbeat)
		{
		}

		public void Update()
		{
		}
	}
}
