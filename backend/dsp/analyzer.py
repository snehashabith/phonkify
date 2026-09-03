import librosa
import soundfile as sf
import numpy as np

def calculate_adaptive_phonk_bpm(input_bpm: float) -> float:
    """
    Dynamically select Phonk tempo based on original input speed.
    """
    if input_bpm < 90:
        # Slow ballad/speech -> Slow-drift Phonk (120-128 BPM)
        return float(np.clip(input_bpm * 1.4, 120, 128))
    elif input_bpm > 130:
        # Fast input -> Fast Aggressive Phonk (150-160 BPM)
        return float(np.clip(input_bpm * 1.05, 145, 160))
    else:
        # Standard range -> Standard Drift Phonk (138-145 BPM)
        return 140.0

def pitch_and_stretch(vocal_path: str, output_path: str, target_bpm: calculate_adaptive_phonk_bpm(tempo), semitone_shift: int = -2) -> str:
    """
    Detects track BPM, time-stretches to target_bpm (Drift Phonk style), and pitch-shifts down.
    """
    y, sr = librosa.load(vocal_path, sr=None)

    # 1. Estimate BPM
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]
    
    # Fallback default if detection fails or yields extreme values
    if tempo <= 0 or np.isnan(tempo):
        tempo = 120.0

    # 2. Time Stretch to Target BPM
    rate = target_bpm / tempo
    # Restrict rate bounds to prevent extreme audio warping
    rate = np.clip(rate, 0.7, 1.5)
    y_stretched = librosa.effects.time_stretch(y, rate=rate)

    # 3. Pitch Shift (-2 semitones default for Phonk dark vibe)
    y_shifted = librosa.effects.pitch_shift(y_stretched, sr=sr, n_steps=semitone_shift)

    # Save modified vocals
    sf.write(output_path, y_shifted, sr)
    return output_path