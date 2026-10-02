using System.Collections;
using System.Collections.Generic;
using System.Text;

namespace BestHTTP.JSON
{
	public class Json
	{
		private const int TOKEN_NONE = 0;

		private const int TOKEN_CURLY_OPEN = 1;

		private const int TOKEN_CURLY_CLOSE = 2;

		private const int TOKEN_SQUARED_OPEN = 3;

		private const int TOKEN_SQUARED_CLOSE = 4;

		private const int TOKEN_COLON = 5;

		private const int TOKEN_COMMA = 6;

		private const int TOKEN_STRING = 7;

		private const int TOKEN_NUMBER = 8;

		private const int TOKEN_TRUE = 9;

		private const int TOKEN_FALSE = 10;

		private const int TOKEN_NULL = 11;

		private const int BUILDER_CAPACITY = 2000;

		public static object Decode(string json)
		{
			return null;
		}

		public static object Decode(string json, ref bool success)
		{
			return null;
		}

		public static string Encode(object json)
		{
			return null;
		}

		protected static Dictionary<string, object> ParseObject(char[] json, ref int index, ref bool success)
		{
			return null;
		}

		protected static List<object> ParseArray(char[] json, ref int index, ref bool success)
		{
			return null;
		}

		protected static object ParseValue(char[] json, ref int index, ref bool success)
		{
			return null;
		}

		protected static string ParseString(char[] json, ref int index, ref bool success)
		{
			return null;
		}

		protected static double ParseNumber(char[] json, ref int index, ref bool success)
		{
			return 0.0;
		}

		protected static int GetLastIndexOfNumber(char[] json, int index)
		{
			return 0;
		}

		protected static void EatWhitespace(char[] json, ref int index)
		{
		}

		protected static int LookAhead(char[] json, int index)
		{
			return 0;
		}

		protected static int NextToken(char[] json, ref int index)
		{
			return 0;
		}

		protected static bool SerializeValue(object value, StringBuilder builder)
		{
			return false;
		}

		protected static bool SerializeObject(IDictionary anObject, StringBuilder builder)
		{
			return false;
		}

		protected static bool SerializeArray(IList anArray, StringBuilder builder)
		{
			return false;
		}

		protected static bool SerializeString(string aString, StringBuilder builder)
		{
			return false;
		}

		protected static bool SerializeNumber(double number, StringBuilder builder)
		{
			return false;
		}
	}
}
