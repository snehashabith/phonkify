import os
from pydub import AudioSegment
import numpy as np
import librosa

def select_drum_assets(vocal_path: str, base_dir: str):
    """
    Analyzes vocal RMS energy and tempo to choose between Trap and Dubstep drum loops.
    """
    y, sr = librosa.load(vocal_path, sr=None)
    
    # Measure Energy and BPM
    rms_energy = float(np.mean(librosa.feature.rms(y=y)))
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]

    assets_dir = os.path.join(base_dir, "assets")

    # High energy OR slow input speech -> Heavy Dubstep Loop
    if rms_energy > 0.18 or tempo < 110:
        selected_drums = os.path.join(assets_dir, "dubstep_drum_loop.wav")
    else:
        selected_drums = os.path.join(assets_dir, "trap_drum_loop.wav")

    gm_loop_path = os.path.join(assets_dir, "gm_loop.wav")
    cowbell_path = os.path.join(assets_dir, "cowbells.wav")

    return selected_drums, gm_loop_path, cowbell_path

def mix_track_with_drums(effected_vocal_path: str, base_dir: str, output_path: str) -> str:
    # 1. Dynamically select audio assets
    drum_path, gm_path, cowbell_path = select_drum_assets(effected_vocal_path, base_dir)

    vocal = AudioSegment.from_file(effected_vocal_path)
    track_length = len(vocal)

    # Helper function to loop an asset to match vocal duration
    def prepare_loop(path: str, gain_db: float = 0.0):
        if not os.path.exists(path):
            return None
        loop = AudioSegment.from_file(path) + gain_db
        if len(loop) < track_length:
            loops_needed = (track_length // len(loop)) + 1
            loop = loop * loops_needed
        return loop[:track_length]

    # 2. Load and loop selected assets with appropriate mixing gains
    drums = prepare_loop(drum_path, gain_db=0.0)      # Primary beat
    gm_loop = prepare_loop(gm_path, gain_db=-6.0)     # Background melody (-6dB lower)
    cowbell = prepare_loop(cowbell_path, gain_db=-2.0)  # Accent cowbell (-2dB)

    # 3. Layer everything together into the final mix
    final_mix = vocal + 1.5  # Vocal level

    if drums:
        final_mix = final_mix.overlay(drums)
    if gm_loop:
        final_mix = final_mix.overlay(gm_loop)
    if cowbell:
        final_mix = final_mix.overlay(cowbell)

    # 4. Normalize to -1.0 dBFS headroom to prevent clipping
    normalized_mix = final_mix.normalize(headroom=1.0)
    normalized_mix.export(output_path, format="mp3", bitrate="192k")

    return output_path