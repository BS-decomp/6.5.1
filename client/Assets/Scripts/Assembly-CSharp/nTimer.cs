using UnityEngine;

public class nTimer : MonoBehaviour
{
	private global::JJJJIJJIJIJIJIIJIIIJJJJIIIIJJJIJIIIIJIIJJIIIIJJ<TimerData> timers;

	private global::JJJJIJJIJIJIJIIJIIIJJJJIIIIJJJIJIIIIJIIJJIIIIJJ<TimerData> pool;

	private static int maxInvokeInUpdate;

	private bool enable;

	private void Start()
	{
	}

	private void OnEnable()
	{
	}

	private void OnDisable()
	{
	}

	private void OnDestroy()
	{
	}

	public TimerData Create(string tag, float delay, TimerDelegate callback)
	{
		return null;
	}

	public TimerData Create(string tag, float delay, bool loop, TimerDelegate callback)
	{
		return null;
	}

	public TimerData In(string tag)
	{
		return null;
	}

	public TimerData In(string tag, float delay)
	{
		return null;
	}

	public TimerData In(float delay, TimerDelegate callback)
	{
		return null;
	}

	public TimerData In(float delay, bool loop, TimerDelegate callback)
	{
		return null;
	}

	public TimerData In(string tag, float delay, bool loop, TimerDelegate callback)
	{
		return null;
	}

	public bool Contains(string tag)
	{
		return false;
	}

	public bool isActive(string tag)
	{
		return false;
	}

	public void Cancel(string tag)
	{
	}

	private void OnUpdate()
	{
	}
}
