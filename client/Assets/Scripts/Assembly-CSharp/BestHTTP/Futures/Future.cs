using System;
using System.Collections.Generic;

namespace BestHTTP.Futures
{
	public class Future<T> : IFuture<T>
	{
		private FutureState _state;

		private T _value;

		private Exception _error;

		private Func<T> _processFunc;

		private readonly List<FutureValueCallback<T>> _itemCallbacks;

		private readonly List<FutureValueCallback<T>> _successCallbacks;

		private readonly List<FutureErrorCallback> _errorCallbacks;

		private readonly List<FutureCallback<T>> _complationCallbacks;

		public FutureState state => FutureState.Pending;

		public T value => default;

		public Exception error => null;

		public IFuture<T> OnItem(FutureValueCallback<T> callback)
		{
			return null;
		}

		public IFuture<T> OnSuccess(FutureValueCallback<T> callback)
		{
			return null;
		}

		public IFuture<T> OnError(FutureErrorCallback callback)
		{
			return null;
		}

		public IFuture<T> OnComplete(FutureCallback<T> callback)
		{
			return null;
		}

		public IFuture<T> Process(Func<T> func)
		{
			return null;
		}

		private void ThreadFunc(object param)
		{
		}

		public void Assign(T value)
		{
		}

		public void BeginProcess(T initialItem = default(T))
		{
		}

		public void AssignItem(T value)
		{
		}

		public void Fail(Exception error)
		{
		}

		private void AssignImpl(T value)
		{
		}

		private void FailImpl(Exception error)
		{
		}

		private void FlushSuccessCallbacks()
		{
		}

		private void FlushErrorCallbacks()
		{
		}

		private void FlushComplationCallbacks()
		{
		}

		private void ClearCallbacks()
		{
		}
	}
}
