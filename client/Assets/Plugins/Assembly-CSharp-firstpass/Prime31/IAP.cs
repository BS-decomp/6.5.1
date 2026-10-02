using System;
using System.Collections.Generic;

namespace Prime31
{
	public static class IAP
	{
		public static List<GooglePurchase> androidPurchasedItems;

		private const string CONSUMABLE_PAYLOAD = "consume";

		private const string NON_CONSUMABLE_PAYLOAD = "nonconsume";

		private static Action<List<IAPProduct>> _productListReceivedAction;

		private static Action<bool, string> _purchaseCompletionAction;

		private static Action<string> _purchaseRestorationAction;

		static IAP()
		{
		}

		public static void init(string androidPublicKey)
		{
		}

		public static void requestProductData(string[] iosProductIdentifiers, string[] androidSkus, Action<List<IAPProduct>> completionHandler)
		{
		}

		public static void purchaseConsumableProduct(string productId, Action<bool, string> completionHandler)
		{
		}

		public static void purchaseNonconsumableProduct(string productId, Action<bool, string> completionHandler)
		{
		}

		public static void restoreCompletedTransactions(Action<string> completionHandler)
		{
		}
	}
}
