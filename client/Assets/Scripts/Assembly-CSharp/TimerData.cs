public class TimerData
{
	public string tag;

	public TimerDelegate callback;

	public float endTime;

	public bool loop;

	public float delay;

	public bool cancelOnLoad;

	public bool stop;

	public bool Update(float time)
	{
		return false;
	}
}
