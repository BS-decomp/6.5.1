using System;
using System.Runtime.Serialization;
using System.Threading.Tasks;
using Google.Impl;

namespace Google
{
	public class GoogleSignIn
	{
		[Serializable]
		public class SignInException : Exception
		{
			public GoogleSignInStatusCode Status { get; internal set; }

			internal SignInException(GoogleSignInStatusCode status)
			{
			}

			public SignInException(GoogleSignInStatusCode status, string message)
			{
			}

			public SignInException(GoogleSignInStatusCode status, string message, Exception innerException)
			{
			}

			protected SignInException(GoogleSignInStatusCode status, SerializationInfo info, StreamingContext context)
			{
			}
		}

		private static GoogleSignIn theInstance;

		private static GoogleSignInConfiguration theConfiguration;

		private ISignInImpl impl;

		public static GoogleSignInConfiguration Configuration
		{
			get
			{
				return null;
			}
			set
			{
			}
		}

		public static GoogleSignIn DefaultInstance => null;

		internal GoogleSignIn(GoogleSignInImpl impl)
		{
		}

		public void EnableDebugLogging(bool flag)
		{
		}

		public Task<GoogleSignInUser> SignIn()
		{
			return null;
		}

		public Task<GoogleSignInUser> SignInSilently()
		{
			return null;
		}

		public void SignOut()
		{
		}

		public void Disconnect()
		{
		}
	}
}
