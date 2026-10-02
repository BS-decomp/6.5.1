using System;
using System.Collections.Generic;

namespace BestHTTP.Authentication
{
	public sealed class Digest
	{
		public Uri Uri { get; private set; }

		public AuthenticationTypes Type { get; private set; }

		public string Realm { get; private set; }

		public bool Stale { get; private set; }

		private string Nonce { get; set; }

		private string Opaque { get; set; }

		private string Algorithm { get; set; }

		public List<string> ProtectedUris { get; private set; }

		private string QualityOfProtections { get; set; }

		private int NonceCount { get; set; }

		private string HA1Sess { get; set; }

		internal Digest(Uri uri)
		{
		}

		public void ParseChallange(string header)
		{
		}

		public string GenerateResponseHeader(HTTPRequest request, Credentials credentials, bool isProxy = false)
		{
			return null;
		}

		public bool IsUriProtected(Uri uri)
		{
			return false;
		}
	}
}
