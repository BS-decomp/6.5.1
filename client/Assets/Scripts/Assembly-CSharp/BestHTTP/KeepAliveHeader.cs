using System;
using System.Collections.Generic;

namespace BestHTTP
{
	internal sealed class KeepAliveHeader
	{
		public TimeSpan TimeOut { get; private set; }

		public int MaxRequests { get; private set; }

		public void Parse(List<string> headerValues)
		{
		}
	}
}
