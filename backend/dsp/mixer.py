"""Input-reactive arrangement instead of a fixed loop stack."""

import hashlib
import os
import random
from pydub import AudioSegment, effects


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


def _loop_slice(loop: AudioSegment, start_ms: int, duration_ms: int) -> AudioSegment:
    if not len(loop):
        return AudioSegment.silent(duration=duration_ms)
    start_ms %= len(loop)
    return (loop * ((start_ms + duration_ms) // len(loop) + 2))[start_ms:start_ms + duration_ms]


def _activity_db(vocal: AudioSegment, start: int, duration: int) -> float:
    chunk = vocal[start:start + duration]
    return chunk.dBFS if chunk.rms else -90.0


def mix_track_with_drums(effected_vocal_path: str, base_dir: str, output_path: str) -> str:
    drum_path, gm_path, cowbell_path = select_drum_assets(effected_vocal_path, base_dir)
    vocal = AudioSegment.from_file(effected_vocal_path)
    if not len(vocal):
        raise ValueError("No vocal audio was available for mixing")
    rng = random.Random(_seed_for_file(effected_vocal_path))
    length = len(vocal)
    drum = AudioSegment.from_file(drum_path) if os.path.exists(drum_path) else None
    melody = AudioSegment.from_file(gm_path) if os.path.exists(gm_path) else None
    cowbell = AudioSegment.from_file(cowbell_path) if os.path.exists(cowbell_path) else None

    # Voice is the anchor. Backing changes by input hash, phrase energy and section.
    mix = vocal + 5.5
    section_ms = rng.choice((1800, 2000, 2400, 2800))
    for index, start in enumerate(range(0, length, section_ms)):
        duration = min(section_ms, length - start)
        active = _activity_db(vocal, start, duration) > -33.0
        intro = index == 0 and length > section_ms * 1.4
        if drum and not intro:
            gain = rng.uniform(-15, -10) if active else rng.uniform(-10, -6.5)
            mix = mix.overlay(_loop_slice(drum, rng.randrange(len(drum)), duration) + gain, position=start)
        if melody and not intro and (not active or rng.random() < 0.32):
            mix = mix.overlay(_loop_slice(melody, rng.randrange(len(melody)), duration) + rng.uniform(-22, -16), position=start)
        if cowbell and not intro and index % rng.choice((2, 3)) == 0:
            mix = mix.overlay(_loop_slice(cowbell, rng.randrange(len(cowbell)), duration) + rng.uniform(-20, -14), position=start)

    mix = effects.compress_dynamic_range(mix, threshold=-15, ratio=2.0, attack=8, release=90)
    effects.normalize(mix, headroom=0.8).export(output_path, format="mp3", bitrate="192k")
    return output_path
