using System.Collections.Generic;

namespace Google
{
	public class GoogleSignInConfiguration
	{
		public bool UseGameSignIn;

		public string WebClientId;

		public bool RequestAuthCode;

		public bool ForceTokenRefresh;

		public bool RequestEmail;

		public bool RequestIdToken;

		public bool RequestProfile;

		public bool HidePopups;

		public string AccountName;

		public IEnumerable<string> AdditionalScopes;
	}
}
