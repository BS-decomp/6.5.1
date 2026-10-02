using System.Collections.Generic;

namespace BestHTTP.Extensions
{
	public sealed class HeaderValue
	{
		public string Key { get; set; }

		public string Value { get; set; }

		public List<HeaderValue> Options { get; set; }

		public bool HasValue => false;

		public HeaderValue()
		{
		}

		public HeaderValue(string key)
		{
		}

		public void Parse(string headerStr, ref int pos)
		{
		}

		public bool TryGetOption(string key, out HeaderValue option)
		{
			option = null;
			return false;
		}

		private void ParseImplementation(string headerStr, ref int pos, bool isOptionIsAnOption)
		{
		}

		public override string ToString()
		{
			return null;
		}
	}
}
