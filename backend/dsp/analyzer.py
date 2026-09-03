"""Feature extraction and conservative vocal processing decisions."""

from dataclasses import dataclass, replace
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
    backing_semitones: int


def calculate_adaptive_phonk_bpm(input_bpm: float) -> float:
    """Choose a half-time drift tempo that follows the source's pace."""
    # Slow sources must receive slow backing; fixed 140-BPM loops were the main
    # reason mellow uploads sounded rushed. Faster songs still get faster beats.
    if input_bpm < 85:
        return float(np.clip(input_bpm * 0.90, 65, 82))
    if input_bpm < 120:
        return float(np.clip(input_bpm * 0.84, 78, 102))
    return float(np.clip(input_bpm * 0.80, 100, 136))


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
    # The supplied melodic loops are authored around C.  Move their tonal
    # elements to the nearest pitch class in the voice rather than layering an
    # arbitrary cowbell melody over it.
    try:
        f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C6"))
        voiced = f0[np.isfinite(f0)]
        pitch_class = int(round(librosa.hz_to_midi(float(np.median(voiced))))) % 12 if len(voiced) else 0
    except Exception:
        pitch_class = 0
    backing_semitones = pitch_class if pitch_class <= 6 else pitch_class - 12
    return AudioProfile(tempo, calculate_adaptive_phonk_bpm(tempo), confidence, rms, brightness,
                        confidence < 0.35 or duration < 3.0, backing_semitones)


def pitch_and_stretch(vocal_path: str, output_path: str, target_bpm: Optional[float] = None,
                      semitone_shift: Optional[int] = None,
                      style: str = "dark_drift") -> AudioProfile:
    """Slow and lower the source for a dark, vocal-forward drift-phonk treatment."""
    profile = analyze_vocal(vocal_path)
    y, sr = librosa.load(vocal_path, sr=None, mono=False)
    target = target_bpm if target_bpm is not None else profile.target_bpm
    # librosa rates below 1 make the output longer/slower.  This is intentional:
    # the dark-drift preset applies a clearly audible half-time feel to every
    # input, including speech and acapellas.
    rate = float(np.clip(target / profile.bpm, 0.70, 0.90)) if style == "dark_drift" else (
        1.0 if profile.speech_like else float(np.clip(target / profile.bpm, 0.88, 1.14))
    )
    channels = [y] if y.ndim == 1 else y
    stretched = [librosa.effects.time_stretch(channel, rate=rate) for channel in channels]
    shift = semitone_shift if semitone_shift is not None else (
        -4 if style == "dark_drift" else (-1 if profile.brightness > 2100 else -2)
    )
    shifted = [librosa.effects.pitch_shift(channel, sr=sr, n_steps=shift) for channel in stretched]
    result = shifted[0] if y.ndim == 1 else np.vstack(shifted).T
    sf.write(output_path, result, sr)
    # This is the tempo of the rendered source, and is passed to the arranger so
    # its loops slow down with the vocal instead of fighting it.
    return replace(profile, target_bpm=profile.bpm * rate)
