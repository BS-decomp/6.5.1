using UnityEngine;
using UnityEngine.Events;

namespace CodeStage.AntiCheat.Detectors
{
	public abstract class ActDetectorBase : MonoBehaviour
	{
		protected const string IJJJJIIIIJJJIIJJIJIJJIIJJJIJJIIIJIIIIIIJJJJJJJJ = "Anti-Cheat Toolkit Detectors";

		protected const string JIJJIIJIIIJJJJJJIJJIJIIJIIJIIJIJJIIIIIJIIJIIJJJ = "Code Stage/Anti-Cheat Toolkit/";

		protected const string IJJIJIJIJJJJIIJIJIIJJIIJJIJIIIJIJIJIJJJJIIJJJIJ = "GameObject/Create Other/Code Stage/Anti-Cheat Toolkit/";

		protected static GameObject IIIJIIJJIIIJIIIIJJIJIJIJJJJJIJIIJIJIJIIIIIJIIJJ;

		public bool IJJIIJJIJJIJIJJJIIJJIIIIJJIIIIIJIIIJIJIJIJJIIJI;

		public bool JIIJIIJJJIJIJIJJIJIJIIIIJJIJIIIIJIJJJJIJJIJIJII;

		public bool IJJJJJIIIIJIJIIIJJJJIIIIJIJJJJIJJJIJJIJJIJIJJJI;

		[SerializeField]
		protected UnityEvent detectionEvent;

		protected UnityAction IJIIJJIIJJJJJIIIIIIJIJIIJIIJIIJJIJIIJIJIIIIJIJJ;

		[SerializeField]
		protected bool detectionEventHasListener;

		protected bool JIIIIIJIJJJIIIIIIJIJIIIIJIIIIIIJJIIIIJIJIJJIJIJ;

		protected bool IJJJIIJIIJJJIIJJIIIIIIIJJJJJJJJIIIIJIIJJIIIJJJJ;

		private void Start()
		{
		}

		private void OnEnable()
		{
		}

		private void OnDisable()
		{
		}

		private void OnApplicationQuit()
		{
		}

		protected virtual void OnDestroy()
		{
		}

		protected virtual bool IIIJJIJJJJIJIIJIIIIIIIIIJJIIJJIJJJIIIJIJJJJIJIJ(ActDetectorBase JIIIIJJJJIIJJJIIJIJIIJIIJJIIIIIIIIJJIJIJJJJJJJJ, string JJIJIIJJIJJJIJIIIJIJIIIJJJJIJJIJIJIJIJIIJIIJIJJ)
		{
			return false;
		}

		protected virtual void JIJIIIJIJIIIJIIJIIIJIIIIJJJIJJJJJIJIIJJJJIJJJIJ()
		{
		}

		protected virtual bool JIJIJJIJJIJJJIJIJIIJIIIIJIJJJJIIIIJIJJIJIIJIIJI()
		{
			return false;
		}

		internal virtual void JJIJIIIIIJIIIIIJIIJJIJIIIJIJJIJJJIJIJJIJJJIIIJI()
		{
		}

		protected abstract void JJJJIJJJJIJJJIJJIIIIJIIJIJJJJIJIIJIIJJJIIIIIJIJ();

		protected abstract void JJIJJIIJJJIJJJIJJJIIJIJIIJJJJJIJJJIIJIIJIIJJJJI();

		protected abstract void JJJJIJJJIJIIJIIJJJJIIJJIJIJIIJIIIJIJIJIJJJIIJII();

		protected abstract void IJJIIJJJIIJIIJIJJJJIJJJJIJIJJIJJJIIJJJJJJIIIJJJ();
	}
}
