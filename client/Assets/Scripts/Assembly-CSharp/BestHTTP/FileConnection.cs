namespace BestHTTP
{
	internal sealed class FileConnection : ConnectionBase
	{
		public FileConnection(string serverAddress)
			: base(null)
		{
		}

		internal override void Abort(HTTPConnectionStates newState)
		{
		}

		protected override void ThreadFunc(object param)
		{
		}
	}
}
