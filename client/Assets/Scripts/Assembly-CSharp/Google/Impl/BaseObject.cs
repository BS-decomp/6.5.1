using System;
using System.Runtime.InteropServices;

namespace Google.Impl
{
	internal abstract class BaseObject : IDisposable
	{
		internal delegate UIntPtr OutStringMethod([In][Out] byte[] out_bytes, UIntPtr out_size);

		private HandleRef selfHandleRef;

		private static HandleRef nullSelf;

		public BaseObject(IntPtr intPtr)
		{
		}

		protected HandleRef SelfPtr()
		{
			return default;
		}

		public virtual void Dispose()
		{
		}

		internal static string OutParamsToString(OutStringMethod outStringMethod)
		{
			return null;
		}
	}
}
