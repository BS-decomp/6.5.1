using System;
using System.Collections.Generic;
using System.Security.Cryptography.X509Certificates;
using BestHTTP.Extensions;
using BestHTTP.Logger;
using BestHTTP.PlatformSupport.FileSystem;
using BestHTTP.Statistics;

namespace BestHTTP
{
	public static class HTTPManager
	{
		private static byte maxConnectionPerServer;

		private static HeartbeatManager heartbeats;

		private static ILogger logger;

		public static bool TryToMinimizeTCPLatency;

		public static int SendBufferSize;

		public static int ReceiveBufferSize;

		public static IIOService IOService;

		private static Dictionary<string, List<ConnectionBase>> Connections;

		private static List<ConnectionBase> ActiveConnections;

		private static List<ConnectionBase> FreeConnections;

		private static List<ConnectionBase> RecycledConnections;

		private static List<HTTPRequest> RequestQueue;

		private static bool IsCallingCallbacks;

		internal static object Locker;

		public static byte MaxConnectionPerServer
		{
			get
			{
				return 0;
			}
			set
			{
			}
		}

		public static bool KeepAliveDefaultValue { get; set; }

		public static TimeSpan MaxConnectionIdleTime { get; set; }

		public static uint CookieJarSize { get; set; }

		public static bool EnablePrivateBrowsing { get; set; }

		public static TimeSpan ConnectTimeout { get; set; }

		public static TimeSpan RequestTimeout { get; set; }

		public static HeartbeatManager Heartbeats => null;

		public static ILogger Logger
		{
			get
			{
				return null;
			}
			set
			{
			}
		}

		public static Func<HTTPRequest, X509Certificate, X509Chain, bool> DefaultCertificationValidator { get; set; }

		internal static int MaxPathLength { get; set; }

		internal static bool IsQuitting { get; private set; }

		static HTTPManager()
		{
		}

		public static void Setup()
		{
		}

		public static HTTPRequest SendRequest(string url, OnRequestFinishedDelegate callback)
		{
			return null;
		}

		public static HTTPRequest SendRequest(string url, HTTPMethods methodType, OnRequestFinishedDelegate callback)
		{
			return null;
		}

		public static HTTPRequest SendRequest(string url, HTTPMethods methodType, bool isKeepAlive, OnRequestFinishedDelegate callback)
		{
			return null;
		}

		public static HTTPRequest SendRequest(string url, HTTPMethods methodType, bool isKeepAlive, bool disableCache, OnRequestFinishedDelegate callback)
		{
			return null;
		}

		public static HTTPRequest SendRequest(HTTPRequest request)
		{
			return null;
		}

		public static GeneralStatistics GetGeneralStatistics(StatisticsQueryFlags queryFlags)
		{
			return default;
		}

		private static void SendRequestImpl(HTTPRequest request)
		{
		}

		private static string GetKeyForRequest(HTTPRequest request)
		{
			return null;
		}

		private static ConnectionBase CreateConnection(HTTPRequest request, string serverUrl)
		{
			return null;
		}

		private static ConnectionBase FindOrCreateFreeConnection(HTTPRequest request)
		{
			return null;
		}

		private static bool CanProcessFromQueue()
		{
			return false;
		}

		private static void RecycleConnection(ConnectionBase conn)
		{
		}

		private static void OnConnectionRecylced(ConnectionBase conn)
		{
		}

		internal static ConnectionBase GetConnectionWith(HTTPRequest request)
		{
			return null;
		}

		internal static bool RemoveFromQueue(HTTPRequest request)
		{
			return false;
		}

		public static void OnUpdate()
		{
		}

		public static void OnQuit()
		{
		}

		public static void AbortAll(bool allowCallbacks = false)
		{
		}
	}
}
