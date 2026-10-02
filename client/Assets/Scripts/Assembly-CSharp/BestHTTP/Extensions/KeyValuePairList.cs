using System.Collections.Generic;

namespace BestHTTP.Extensions
{
	public class KeyValuePairList
	{
		public List<HeaderValue> Values { get; protected set; }

		public bool TryGet(string valueKeyName, out HeaderValue param)
		{
			param = null;
			return false;
		}
	}
}
