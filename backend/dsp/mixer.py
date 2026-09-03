"""Input-reactive arrangement instead of a fixed loop stack."""

import hashlib
import os
import random
from typing import Optional
import numpy as np
from pydub import AudioSegment, effects
from pedalboard import PitchShift


def _seed_for_file(path: str) -> int:
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return int.from_bytes(digest.digest()[:8], "big")


def select_drum_assets(vocal_path: str, base_dir: str):
    assets = os.path.join(base_dir, "assets")
    vocal = AudioSegment.from_file(vocal_path)
    drum = "dubstep_drum_loop.wav" if vocal.rms > 1500 else "trap_drum_loop.wav"
    return (os.path.join(assets, drum), os.path.join(assets, "gm_loop.wav"),
            os.path.join(assets, "cowbells.wav"))


def _retime_loop(loop: AudioSegment, target_bpm: float, source_bpm: float = 140.0) -> AudioSegment:
    """Tempo-match a loop while retaining its sample rate for the final mix."""
    if not target_bpm or target_bpm <= 0:
        return loop
    speed = max(0.40, min(1.20, target_bpm / source_bpm))
    altered_rate = int(loop.frame_rate * speed)
    return loop._spawn(loop.raw_data, overrides={"frame_rate": altered_rate}).set_frame_rate(loop.frame_rate)


def _transpose_segment(segment: AudioSegment, semitones: int) -> AudioSegment:
    """Pitch-shift a tonal loop without altering its duration."""
    if not semitones:
        return segment
    raw = np.array(segment.get_array_of_samples())
    if not len(raw):
        return segment
    channels = segment.channels
    frames = raw.reshape((-1, channels)).astype(np.float32)
    scale = float(max(abs(np.iinfo(raw.dtype).min), np.iinfo(raw.dtype).max))
    shifted = PitchShift(semitones=float(semitones))(frames.T / scale, segment.frame_rate).T
    restored = np.clip(shifted * scale, np.iinfo(raw.dtype).min, np.iinfo(raw.dtype).max).astype(raw.dtype)
    return segment._spawn(restored.reshape(-1).tobytes())


def _loop_slice(loop: AudioSegment, start_ms: int, duration_ms: int) -> AudioSegment:
    if not len(loop):
        return AudioSegment.silent(duration=duration_ms)
    start_ms %= len(loop)
    return (loop * ((start_ms + duration_ms) // len(loop) + 2))[start_ms:start_ms + duration_ms]


def _activity_db(vocal: AudioSegment, start: int, duration: int) -> float:
    chunk = vocal[start:start + duration]
    return chunk.dBFS if chunk.rms else -90.0


def mix_track_with_drums(effected_vocal_path: str, base_dir: str, output_path: str,
                         target_bpm: Optional[float] = None,
                         backing_semitones: int = 0,
                         max_duration_ms: Optional[int] = None) -> str:
    drum_path, gm_path, cowbell_path = select_drum_assets(effected_vocal_path, base_dir)
    vocal = AudioSegment.from_file(effected_vocal_path)
    if max_duration_ms is not None:
        vocal = vocal[:max_duration_ms]
    if not len(vocal):
        raise ValueError("No vocal audio was available for mixing")
    rng = random.Random(_seed_for_file(effected_vocal_path))
    length = len(vocal)
    drum = AudioSegment.from_file(drum_path) if os.path.exists(drum_path) else None
    melody = AudioSegment.from_file(gm_path) if os.path.exists(gm_path) else None
    cowbell = AudioSegment.from_file(cowbell_path) if os.path.exists(cowbell_path) else None
    if target_bpm:
        drum = _retime_loop(drum, target_bpm) if drum else None
        melody = _retime_loop(melody, target_bpm) if melody else None
        cowbell = _retime_loop(cowbell, target_bpm) if cowbell else None
    if drum:
        # Smooth sharp kick/snare peaks before they are mixed under a vocal.
        drum = effects.compress_dynamic_range(drum, threshold=-13, ratio=3.0, attack=3, release=100) - 2.0
    # Do not pitch-shift kick/snare loops: they are not tonal instruments. Only
    # melodic material is transposed to the detected vocal pitch class.
    melody = _transpose_segment(melody, backing_semitones) if melody else None
    cowbell = _transpose_segment(cowbell, backing_semitones) if cowbell else None

    # Let the instrumental lead while keeping a clear, lower-level vocal stem.
    mix = vocal - 3.0
    beat_ms = 60000.0 / target_bpm if target_bpm and target_bpm > 0 else 428.57
    section_ms = max(1, int(round(beat_ms * 4)))
    for index, start in enumerate(range(0, length, section_ms)):
        duration = min(section_ms, length - start)
        active = _activity_db(vocal, start, duration) > -33.0
        intro = index == 0 and length > section_ms * 1.4
        if drum and not intro:
            # The beat stays forward even during lines; the vocal is no longer
            # normalized above the arrangement.
            gain = rng.uniform(-6, -3) if active else rng.uniform(-3, 0)
            mix = mix.overlay(_loop_slice(drum, start, duration) + gain, position=start)
        if melody and not intro and (not active or rng.random() < 0.32):
            mix = mix.overlay(_loop_slice(melody, start, duration) + rng.uniform(-14, -9), position=start)
        if cowbell and not intro and index % rng.choice((2, 3)) == 0:
            mix = mix.overlay(_loop_slice(cowbell, start, duration) + rng.uniform(-12, -7), position=start)

    mix = effects.compress_dynamic_range(mix, threshold=-15, ratio=2.0, attack=8, release=90)
    effects.normalize(mix, headroom=0.8).export(output_path, format="mp3", bitrate="192k")
    return output_path
