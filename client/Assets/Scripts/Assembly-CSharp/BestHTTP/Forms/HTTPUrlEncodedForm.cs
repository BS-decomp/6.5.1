namespace BestHTTP.Forms
{
	public sealed class HTTPUrlEncodedForm : HTTPFormBase
	{
		private const int EscapeTreshold = 256;

		private byte[] CachedData;

		public override void PrepareRequest(HTTPRequest request)
		{
		}

		public override byte[] GetData()
		{
			return null;
		}

		public static string EscapeString(string originalString)
		{
			return null;
		}
	}
}
