using System;
using UnityEngine;

namespace BSCM.Game
{
	public class SceneSettings : MonoBehaviour
	{
		[Serializable]
		public class ModeSettings
		{
			public GameMode mode;

			public byte maxScore;

			public float time;

			public float respawnNoDamage;
		}

		public ModeSettings[] modes;

		public Transform redSpawn;

		public Transform blueSpawn;

		public Transform cameraStatic;

		public static SceneSettings instance;

		private void Awake()
		{
		}

		public void Create()
		{
		}

		public ModeSettings GetSettings(GameMode mode)
		{
			return null;
		}

		private bool CheckGO(Transform t)
		{
			return false;
		}

		private void CheckScene()
		{
		}
	}
}
