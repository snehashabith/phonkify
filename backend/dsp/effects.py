"""Vocal-forward, intentionally restrained phonk coloration."""

import librosa
import numpy as np
import soundfile as sf
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Distortion, Reverb


def get_adaptive_pedalboard(vocal_path: str) -> Pedalboard:
    y, sr = librosa.load(vocal_path, sr=None, mono=True)
    brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    highpass = 95.0 if brightness < 1600 else 135.0
    lowpass = 6500.0 if brightness > 2400 else 5200.0
    drive = 2.5 if brightness > 1800 else 4.0
    return Pedalboard([HighpassFilter(cutoff_frequency_hz=highpass), LowpassFilter(cutoff_frequency_hz=lowpass), Distortion(drive_db=drive), Reverb(room_size=0.18, wet_level=0.07, dry_level=0.98)])


def apply_phonk_fx(input_vocal_path: str, output_vocal_path: str) -> str:
    audio, sample_rate = sf.read(input_vocal_path, always_2d=True)
    effected = get_adaptive_pedalboard(input_vocal_path)(audio.T, sample_rate).T
    result = (effected * 0.84) + (audio * 0.16)
    peak = float(np.max(np.abs(result)))
    if peak > 0.98:
        result *= 0.98 / peak
    sf.write(output_vocal_path, result, sample_rate)
    return output_vocal_path
