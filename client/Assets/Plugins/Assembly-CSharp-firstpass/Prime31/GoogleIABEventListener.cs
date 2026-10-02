using System.Collections.Generic;
using UnityEngine;

namespace Prime31
{
	public class GoogleIABEventListener : MonoBehaviour
	{
		private void OnEnable()
		{
		}

		private void OnDisable()
		{
		}

		private void billingSupportedEvent()
		{
		}

		private void billingNotSupportedEvent(string error)
		{
		}

		private void queryInventorySucceededEvent(List<GooglePurchase> purchases, List<GoogleSkuInfo> skus)
		{
		}

		private void queryInventoryFailedEvent(string error)
		{
		}

		private void purchaseCompleteAwaitingVerificationEvent(string purchaseData, string signature)
		{
		}

		private void purchaseSucceededEvent(GooglePurchase purchase)
		{
		}

		private void purchaseFailedEvent(string error, int response)
		{
		}

		private void consumePurchaseSucceededEvent(GooglePurchase purchase)
		{
		}

		private void consumePurchaseFailedEvent(string error)
		{
		}
	}
}
