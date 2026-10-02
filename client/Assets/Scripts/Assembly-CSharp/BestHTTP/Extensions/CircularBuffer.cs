namespace BestHTTP.Extensions
{
	public sealed class CircularBuffer<T>
	{
		private T[] buffer;

		private int startIdx;

		private int endIdx;

		public int Capacity { get; private set; }

		public int Count { get; private set; }

		// C# has no syntax for parameterized property 'Item'.
		public T get_Item(int idx)
		{
			return default;
		}

		public void set_Item(int idx, T value)
		{
		}

		public CircularBuffer(int capacity)
		{
		}

		public void Add(T element)
		{
		}

		public void Clear()
		{
		}
	}
}
