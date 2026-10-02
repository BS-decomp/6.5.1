using System.IO;

namespace BestHTTP.PlatformSupport.FileSystem
{
	public sealed class DefaultIOService : IIOService
	{
		public Stream CreateFileStream(string path, FileStreamModes mode)
		{
			return null;
		}

		public void DirectoryCreate(string path)
		{
		}

		public bool DirectoryExists(string path)
		{
			return false;
		}

		public string[] GetFiles(string path)
		{
			return null;
		}

		public void FileDelete(string path)
		{
		}

		public bool FileExists(string path)
		{
			return false;
		}
	}
}
