using UnityEngine;

namespace BSCM
{
	public class CustomMaterials : MonoBehaviour
	{
		public Material[] materials;

		public Material error;

		private static CustomMaterials Instance;

		public static CustomMaterials instance => null;
	}
}
