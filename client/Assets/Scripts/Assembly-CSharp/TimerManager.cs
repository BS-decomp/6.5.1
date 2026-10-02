using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class TimerManager : MonoBehaviour
{
	public delegate void Callback();

	private class Event
	{
		public int ID;

		public string tag;

		public Callback Function;

		public int Iterations;

		public float Interval;

		public float StartTime;

		public float DueTime;

		public bool CancelOnLoad;

		public void Execute()
		{
		}

		public void Recycle()
		{
		}
	}

	public static float time;

	private List<Event> list;

	private List<Event> pool;

	public static TimerDelegate OnUpdate;

	public static bool stopOnUpdate;

	public int eventCount;

	private static TimerManager instance;

	private void Awake()
	{
	}

	private static void Init()
	{
	}

	private void Update()
	{
	}

	public static int Start()
	{
		return 0;
	}

	public static int Start(bool cancelOnLoad)
	{
		return 0;
	}

	public static float GetDuration(int id)
	{
		return 0f;
	}

	public static int In(float delay, Callback callback)
	{
		return 0;
	}

	public static int In(string tag, float delay, Callback callback)
	{
		return 0;
	}

	public static int In(float delay, bool cancelOnLoad, Callback callback)
	{
		return 0;
	}

	public static int In(string tag, float delay, bool cancelOnLoad, Callback callback)
	{
		return 0;
	}

	public static int In(float delay, int iterations, float interval, Callback callback)
	{
		return 0;
	}

	public static int In(string tag, float delay, int iterations, float interval, Callback callback)
	{
		return 0;
	}

	public static int In(float delay, bool cancelOnLoad, int iterations, float interval, Callback callback)
	{
		return 0;
	}

	public static int In(string tag, float delay, bool cancelOnLoad, int iterations, float interval, Callback callback)
	{
		return 0;
	}

	public static void Cancel(int id)
	{
	}

	public static void Cancel(params int[] ids)
	{
	}

	public static void Cancel(string tag)
	{
	}

	public static void CancelAll()
	{
	}

	private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
	{
	}

	public static bool IsActive(int id)
	{
		return false;
	}

	public static bool IsActive(string tag)
	{
		return false;
	}
}
