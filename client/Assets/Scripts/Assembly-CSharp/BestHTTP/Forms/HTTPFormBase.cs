using System.Collections.Generic;
using System.Text;

namespace BestHTTP.Forms
{
	public class HTTPFormBase
	{
		private const int LongLength = 256;

		public List<HTTPFieldData> Fields { get; set; }

		public bool IsEmpty => false;

		public bool IsChanged { get; protected set; }

		public bool HasBinary { get; protected set; }

		public bool HasLongValue { get; protected set; }

		public void AddBinaryData(string fieldName, byte[] content)
		{
		}

		public void AddBinaryData(string fieldName, byte[] content, string fileName)
		{
		}

		public void AddBinaryData(string fieldName, byte[] content, string fileName, string mimeType)
		{
		}

		public void AddField(string fieldName, string value)
		{
		}

		public void AddField(string fieldName, string value, Encoding e)
		{
		}

		public virtual void CopyFrom(HTTPFormBase fields)
		{
		}

		public virtual void PrepareRequest(HTTPRequest request)
		{
		}

		public virtual byte[] GetData()
		{
			return null;
		}
	}
}
