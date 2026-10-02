namespace Prime31
{
	public class IAPProduct
	{
		public string productId { get; private set; }

		public string title { get; private set; }

		public string price { get; private set; }

		public string description { get; private set; }

		public string currencyCode { get; private set; }

		public IAPProduct(GoogleSkuInfo prod)
		{
		}

		public override string ToString()
		{
			return null;
		}
	}
}
