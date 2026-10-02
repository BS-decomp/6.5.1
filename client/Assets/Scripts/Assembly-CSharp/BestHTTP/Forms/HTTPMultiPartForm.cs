namespace BestHTTP.Forms
{
	public sealed class HTTPMultiPartForm : HTTPFormBase
	{
		private string Boundary;

		private byte[] CachedData;

		public override void PrepareRequest(HTTPRequest request)
		{
		}

		public override byte[] GetData()
		{
			return null;
		}
	}
}
