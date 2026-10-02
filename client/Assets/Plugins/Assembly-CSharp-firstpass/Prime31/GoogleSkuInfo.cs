using System.Collections.Generic;

namespace Prime31
{
	public class GoogleSkuInfo
	{
		public string title { get; private set; }

		public string price { get; private set; }

		public string type { get; private set; }

		public string description { get; private set; }

		public string productId { get; private set; }

		public string priceCurrencyCode { get; private set; }

		public long priceAmountMicros { get; private set; }

		public static List<GoogleSkuInfo> fromList(List<object> items)
		{
			return null;
		}

		public GoogleSkuInfo(Dictionary<string, object> dict)
		{
		}

		public override string ToString()
		{
			return null;
		}
	}
}
