using System;
using System.Collections.Generic;
using System.Text;

namespace BestHTTP.Extensions
{
	public static class VariableSizedBufferPool
	{
		public static readonly byte[] NoData;

		public static bool _isEnabled;

		public static TimeSpan RemoveOlderThan;

		public static TimeSpan RunMaintenanceEvery;

		public static long MinBufferSize;

		public static long MaxBufferSize;

		public static long MaxPoolSize;

		public static bool RemoveEmptyLists;

		public static bool IsDoubleReleaseCheckEnabled;

		private static List<BufferStore> FreeBuffers;

		private static DateTime lastMaintenance;

		private static int PoolSize;

		private static uint GetBuffers;

		private static uint ReleaseBuffers;

		private static StringBuilder statiscticsBuilder;

		public static bool IsEnabled
		{
			get
			{
				return false;
			}
			set
			{
			}
		}

		static VariableSizedBufferPool()
		{
		}

		public static byte[] Get(long size, bool canBeLarger)
		{
			return null;
		}

		public static void Release(List<byte[]> buffers)
		{
		}

		public static void Release(byte[] buffer)
		{
		}

		public static byte[] Resize(ref byte[] buffer, int newSize, bool canBeLarger)
		{
			return null;
		}

		public static string GetStatistics(bool showEmptyBuffers = true)
		{
			return null;
		}

		public static void Clear()
		{
		}

		internal static void Maintain()
		{
		}

		private static bool IsPowerOfTwo(long x)
		{
			return false;
		}

		private static long NextPowerOf2(long x)
		{
			return 0L;
		}

		private static BufferDesc FindFreeBuffer(long size, bool canBeLarger)
		{
			return default;
		}

		private static void AddFreeBuffer(byte[] buffer)
		{
		}
	}
}
