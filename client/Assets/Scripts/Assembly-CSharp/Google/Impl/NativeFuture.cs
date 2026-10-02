using System;

namespace Google.Impl
{
	internal class NativeFuture : BaseObject, FutureAPIImpl<GoogleSignInUser>
	{
		public bool Pending => false;

		public GoogleSignInUser Result => null;

		public GoogleSignInStatusCode Status => GoogleSignInStatusCode.Success;

		internal NativeFuture(IntPtr ptr)
			: base((IntPtr)0)
		{
		}

		public override void Dispose()
		{
		}
	}
}
