"""Feature extraction and conservative vocal processing decisions."""

from dataclasses import dataclass
from typing import Optional

import librosa
import numpy as np
import soundfile as sf


@dataclass(frozen=True)
class AudioProfile:
    bpm: float
    target_bpm: float
    beat_confidence: float
    rms: float
    brightness: float
    speech_like: bool


def calculate_adaptive_phonk_bpm(input_bpm: float) -> float:
    """Choose a genre tempo without forcing every source to 140 BPM."""
    if input_bpm < 90:
        return float(np.clip(input_bpm * 1.35, 118, 130))
    if input_bpm > 130:
        return float(np.clip(input_bpm * 1.04, 142, 158))
    return float(np.clip(input_bpm * 1.08, 132, 146))


def analyze_vocal(vocal_path: str) -> AudioProfile:
    y, sr = librosa.load(vocal_path, sr=None, mono=True)
    if not len(y):
        raise ValueError("The uploaded audio contains no samples")
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, onset_envelope=onset)
    tempo = float(np.asarray(tempo).reshape(-1)[0]) if np.size(tempo) else 0.0
    duration = len(y) / sr
    confidence = min(1.0, len(beat_frames) / max(1.0, duration * 0.45))
    if not np.isfinite(tempo) or tempo < 55 or tempo > 210:
        tempo, confidence = 120.0, 0.0
    rms = float(np.mean(librosa.feature.rms(y=y)))
    brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    return AudioProfile(tempo, calculate_adaptive_phonk_bpm(tempo), confidence, rms, brightness,
                        confidence < 0.35 or duration < 3.0)


def pitch_and_stretch(vocal_path: str, output_path: str, target_bpm: Optional[float] = None,
                      semitone_shift: Optional[int] = None) -> AudioProfile:
    """Gently adapt sung vocals; protect the cadence of spoken/acapella clips."""
    profile = analyze_vocal(vocal_path)
    y, sr = librosa.load(vocal_path, sr=None, mono=False)
    target = target_bpm if target_bpm is not None else profile.target_bpm
    rate = 1.0 if profile.speech_like else float(np.clip(target / profile.bpm, 0.88, 1.14))
    channels = [y] if y.ndim == 1 else y
    stretched = [librosa.effects.time_stretch(channel, rate=rate) for channel in channels]
    shift = semitone_shift if semitone_shift is not None else (-1 if profile.brightness > 2100 else -2)
    shifted = [librosa.effects.pitch_shift(channel, sr=sr, n_steps=shift) for channel in stretched]
    result = shifted[0] if y.ndim == 1 else np.vstack(shifted).T
    sf.write(output_path, result, sr)
    return profile
