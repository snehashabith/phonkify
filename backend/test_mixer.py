import os
import numpy as np
import soundfile as sf
from pydub import AudioSegment

# Import your mixer functions
from dsp.mixer import mix_track_with_drums, select_drum_assets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)


def create_dummy_wav(path: str, duration_sec: float = 4.0, sr: int = 44100):
  """Generates a simple sine wave WAV file if a required asset is missing."""
  if not os.path.exists(path):
    t = np.linspace(0, duration_sec, int(sr * duration_sec), False)
    # Simple 440 Hz tone
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)
    sf.write(path, audio, sr)
    print(f"[TEST SETUP] Created temporary dummy audio at: {path}")


def run_standalone_test():
  print("=" * 60)
  print("RUNNING STANDALONE MIXER TEST")
  print("=" * 60)
  CUSTOM_AUDIO="test_audio_jov.mp3"
  # 1. Define Paths
  test_vocal_path = os.path.join(TEMP_DIR, CUSTOM_AUDIO)
  test_output_path = os.path.join(TEMP_DIR, "test_mixed_output_jov.mp3")

  # Required asset paths inside backend/assets/
  trap_path = os.path.join(ASSETS_DIR, "trap_drum_loop.wav")
  dubstep_path = os.path.join(ASSETS_DIR, "dubstep_drum_loop.wav")
  gm_path = os.path.join(ASSETS_DIR, "gm_loop.wav")
  cowbell_path = os.path.join(ASSETS_DIR, "cowbells.wav")

  # 2. Ensure mock or real files exist
  create_dummy_wav(test_vocal_path, duration_sec=6.0)
  create_dummy_wav(trap_path, duration_sec=3.42)
  create_dummy_wav(dubstep_path, duration_sec=3.42)
  create_dummy_wav(gm_path, duration_sec=6.85)
  create_dummy_wav(cowbell_path, duration_sec=1.71)

  # 3. Test Asset Selection Logic
  print("\n1. Testing Asset Selection Logic...")
  selected_drums, gm_selected, cowbell_selected = select_drum_assets(
      test_vocal_path, BASE_DIR
  )
  print(f" -> Selected Drum Asset: {os.path.basename(selected_drums)}")
  print(f" -> Selected Melody Asset: {os.path.basename(gm_selected)}")
  print(f" -> Selected Cowbell Asset: {os.path.basename(cowbell_selected)}")

  # 4. Test Mixdown Execution
  print("\n2. Executing mix_track_with_drums()...")
  try:
    output_file = mix_track_with_drums(
        effected_vocal_path=test_vocal_path,
        base_dir=BASE_DIR,
        output_path=test_output_path,
    )

    if os.path.exists(output_file):
      file_size_kb = os.path.getsize(output_file) / 1024
      print(f"\n[SUCCESS] Test output created: {output_file}")
      print(f" -> Output File Size: {file_size_kb:.2f} KB")

      # Verify audio duration with PyDub
      mixed_audio = AudioSegment.from_file(output_file)
      print(f" -> Output Track Duration: {len(mixed_audio) / 1000.0:.2f} seconds")
    else:
      print("\n[FAILURE] Output file was not created.")

  except Exception as e:
    print(f"\n[ERROR] Mixdown failed with exception:\n{str(e)}")


if __name__ == "__main__":
  run_standalone_test()