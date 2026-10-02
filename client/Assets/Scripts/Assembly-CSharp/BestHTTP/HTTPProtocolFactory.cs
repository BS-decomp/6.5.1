using System;
using System.IO;

namespace BestHTTP
{
	public static class HTTPProtocolFactory
	{
		public static HTTPResponse Get(SupportedProtocols protocol, HTTPRequest request, Stream stream, bool isStreamed, bool isFromCache)
		{
			return null;
		}

		public static SupportedProtocols GetProtocolFromUri(Uri uri)
		{
			return SupportedProtocols.Unknown;
		}

		public static bool IsSecureProtocol(Uri uri)
		{
			return false;
		}
	}
}
