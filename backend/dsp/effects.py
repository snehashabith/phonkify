import soundfile as sf
from pedalboard import Pedalboard, LowpassFilter, HighpassFilter, Bitcrush, Distortion, Reverb

def apply_phonk_fx(input_vocal_path: str, output_vocal_path: str) -> str:
    """
    Applies the classic Phonk lo-fi vocal treatment: Bandpass + Bitcrush + Saturation + Reverb.
    """
    audio, sample_rate = sf.read(input_vocal_path)

    # Transpose array to match Pedalboard format (channels, samples) if stereo
    if len(audio.shape) > 1:
        audio = audio.T

    # Pedalboard Phonk FX Chain
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=400.0),   # Cut muddy lows
        LowpassFilter(cutoff_frequency_hz=3200.0),   # Phone-mic telephone effect
        Bitcrush(bit_depth=8.0),                     # Vintage digital crunch
        Distortion(drive_db=14.0),                   # Aggressive drive
        Reverb(room_size=0.65, wet_level=0.35)       # Spacial depth
    ])

    effected_audio = board(audio, sample_rate)

    # Transpose back if necessary
    if len(effected_audio.shape) > 1:
        effected_audio = effected_audio.T

    sf.write(output_vocal_path, effected_audio, sample_rate)
    return output_vocal_path