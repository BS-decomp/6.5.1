using System.Collections.Generic;
using UnityEngine;

namespace BSCM
{
	public class Manager
	{
		public static bool enabled;

		public static GameMode[] modes;

		public static int hash;

		public static string bundleUrl;

		private static AssetBundle bundle;

		private static Dictionary<GameMode, List<string>> scenesGameMode;

		private static string directoryPath;

		public static void Start()
		{
		}

		private static bool CheckFileName(string path)
		{
			return false;
		}

		private static string GetAssetBundlePath(string fileInfoPath)
		{
			return null;
		}

		public static bool HasMaps()
		{
			return false;
		}

		public static string[] GetMapsList(GameMode mode)
		{
			return null;
		}

		public static GameMode[] GetMapModes(string map)
		{
			return null;
		}

		public static void LoadBundle(string path)
		{
		}

		public static void UnloadBundle()
		{
		}

		public static string GetBundleName(string path)
		{
			return null;
		}

		public static string GetBundlePath(string bundleName)
		{
			return null;
		}

		public static string SaveBundle(string name, int[] modes, int hash, string url, byte[] map)
		{
			return null;
		}

		public static bool DeleteBundle(string name)
		{
			return false;
		}

		private static void CreateDirectory()
		{
		}

		public static int GetBundleHash(string bundleName)
		{
			return 0;
		}

		private static string GetBundleUrl(string bundleName)
		{
			return null;
		}

		private static GameMode[] GetBundleModesPath(string bundlePath)
		{
			return null;
		}

		private static GameMode[] GetBundleModes(string bundleName)
		{
			return null;
		}
	}
}
