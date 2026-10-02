using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;

namespace Prime31
{
	public class GoogleIABManager : AbstractManager
	{
		[CompilerGenerated]
		private static Action m_billingSupportedEvent;

		[CompilerGenerated]
		private static Action<string> m_billingNotSupportedEvent;

		[CompilerGenerated]
		private static Action<List<GooglePurchase>, List<GoogleSkuInfo>> m_queryInventorySucceededEvent;

		[CompilerGenerated]
		private static Action<string> m_queryInventoryFailedEvent;

		[CompilerGenerated]
		private static Action<string, string> m_purchaseCompleteAwaitingVerificationEvent;

		[CompilerGenerated]
		private static Action<GooglePurchase> m_purchaseSucceededEvent;

		[CompilerGenerated]
		private static Action<string, int> m_purchaseFailedEvent;

		[CompilerGenerated]
		private static Action<GooglePurchase> m_consumePurchaseSucceededEvent;

		[CompilerGenerated]
		private static Action<string> m_consumePurchaseFailedEvent;

		public static event Action billingSupportedEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public static event Action<string> billingNotSupportedEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public static event Action<List<GooglePurchase>, List<GoogleSkuInfo>> queryInventorySucceededEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public static event Action<string> queryInventoryFailedEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public static event Action<string, string> purchaseCompleteAwaitingVerificationEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public static event Action<GooglePurchase> purchaseSucceededEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public static event Action<string, int> purchaseFailedEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public static event Action<GooglePurchase> consumePurchaseSucceededEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		public static event Action<string> consumePurchaseFailedEvent
		{
			[CompilerGenerated]
			add
			{
			}
			[CompilerGenerated]
			remove
			{
			}
		}

		static GoogleIABManager()
		{
		}

		public void billingSupported(string empty)
		{
		}

		public void billingNotSupported(string error)
		{
		}

		public void queryInventorySucceeded(string json)
		{
		}

		public void queryInventoryFailed(string error)
		{
		}

		public void purchaseCompleteAwaitingVerification(string json)
		{
		}

		public void purchaseSucceeded(string json)
		{
		}

		public void purchaseFailed(string json)
		{
		}

		public void consumePurchaseSucceeded(string json)
		{
		}

		public void consumePurchaseFailed(string error)
		{
		}
	}
}
