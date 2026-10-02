using System;
using UnityEngine;

namespace BestHTTP
{
	[ExecuteInEditMode]
	public sealed class HTTPUpdateDelegator : MonoBehaviour
	{
		public static Func<bool> OnBeforeApplicationQuit;

		public static Action<bool> OnApplicationForegroundStateChanged;

		private static bool IsSetupCalled;

		public static HTTPUpdateDelegator Instance { get; private set; }

		public static bool IsCreated { get; private set; }

		public static bool IsThreaded { get; set; }

		public static bool IsThreadRunning { get; private set; }

		public static int ThreadFrequencyInMS { get; set; }

		static HTTPUpdateDelegator()
		{
		}

		public static void CheckInstance()
		{
		}

		private void Setup()
		{
		}

		private void ThreadFunc(object obj)
		{
		}

		private void Update()
		{
		}

		private void OnDisable()
		{
		}

		private void OnApplicationPause(bool isPaused)
		{
		}

		private void OnApplicationQuit()
		{
		}
	}
}
