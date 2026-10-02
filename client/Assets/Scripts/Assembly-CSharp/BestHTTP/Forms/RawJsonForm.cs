namespace BestHTTP.Forms
{
	public sealed class RawJsonForm : HTTPFormBase
	{
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
