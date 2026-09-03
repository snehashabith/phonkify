"""Vocal-forward, intentionally restrained phonk coloration."""

import librosa
import numpy as np
import soundfile as sf
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Distortion, Reverb


def get_adaptive_pedalboard(vocal_path: str) -> Pedalboard:
    y, sr = librosa.load(vocal_path, sr=None, mono=True)
    brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    # Darker than the standard vocal treatment, but still leaves enough 1-4 kHz
    # information for words to remain understandable after the pitch drop.
    highpass = 70.0 if brightness < 1600 else 95.0
    lowpass = 4400.0 if brightness > 2400 else 3900.0
    # Applied to the isolated vocal stem after its pitch drop, not to the drums.
    drive = 4.5 if brightness > 1800 else 6.0
    return Pedalboard([HighpassFilter(cutoff_frequency_hz=highpass), LowpassFilter(cutoff_frequency_hz=lowpass), Distortion(drive_db=drive), Reverb(room_size=0.28, wet_level=0.11, dry_level=0.96)])


def apply_phonk_fx(input_vocal_path: str, output_vocal_path: str) -> str:
    audio, sample_rate = sf.read(input_vocal_path, always_2d=True)
    effected = get_adaptive_pedalboard(input_vocal_path)(audio.T, sample_rate).T
    result = (effected * 0.84) + (audio * 0.16)
    # Lift the treated signal slightly so the dark filter/saturation is audible
    # above the newly stronger drum layer.
    result *= 1.12
    peak = float(np.max(np.abs(result)))
    if peak > 0.98:
        result *= 0.98 / peak
    sf.write(output_vocal_path, result, sample_rate)
    return output_vocal_path
