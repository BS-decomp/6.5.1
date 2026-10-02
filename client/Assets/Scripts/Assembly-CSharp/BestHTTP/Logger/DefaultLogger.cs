using System;

namespace BestHTTP.Logger
{
	public class DefaultLogger : ILogger
	{
		public Loglevels Level { get; set; }

		public string FormatVerbose { get; set; }

		public string FormatInfo { get; set; }

		public string FormatWarn { get; set; }

		public string FormatErr { get; set; }

		public string FormatEx { get; set; }

		public void Verbose(string division, string verb)
		{
		}

		public void Information(string division, string info)
		{
		}

		public void Warning(string division, string warn)
		{
		}

		public void Error(string division, string err)
		{
		}

		public void Exception(string division, string msg, Exception ex)
		{
		}

		private string GetFormattedTime()
		{
			return null;
		}
	}
}
