using System.Collections;
using System.Threading.Tasks;

namespace Google
{
	public class Future<T>
	{
		private FutureAPIImpl<T> apiImpl;

		public bool Pending => false;

		private GoogleSignInStatusCode Status => GoogleSignInStatusCode.Success;

		private T Result => default;

		internal Future(FutureAPIImpl<T> impl)
		{
		}

		internal IEnumerator WaitForResult(TaskCompletionSource<T> tcs)
		{
			return null;
		}
	}
}
