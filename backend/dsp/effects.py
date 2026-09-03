import soundfile as sf
from pedalboard import Pedalboard, LowpassFilter, HighpassFilter, Bitcrush, Distortion, Reverb
import librosa
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Bitcrush, Distortion

def get_adaptive_pedalboard(vocal_path: str):
    y, sr = librosa.load(vocal_path, sr=None)
    
    # Measure spectral centroid (brightness) and energy (RMS)
    brightness = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    rms_energy = np.mean(librosa.feature.rms(y=y))
    
    # Darker/muffled vocals get higher high-pass cutoffs and drive
    if brightness < 1500:
        hp_cutoff = 500.0
        drive = 16.0
        bit_depth = 6.0  # Heavy crunch for dull inputs
    else:
        hp_cutoff = 350.0
        drive = 9.0
        bit_depth = 10.0 # Clean crunch for bright inputs
        
    return Pedalboard([
        HighpassFilter(cutoff_frequency_hz=hp_cutoff),
        LowpassFilter(cutoff_frequency_hz=3200.0),
        Bitcrush(bit_depth=bit_depth),
        Distortion(drive_db=drive)
    ])

def apply_phonk_fx(input_vocal_path: str, output_vocal_path: str) -> str:
    """
    Applies the classic Phonk lo-fi vocal treatment: Bandpass + Bitcrush + Saturation + Reverb.
    """
    audio, sample_rate = sf.read(input_vocal_path)

    # Transpose array to match Pedalboard format (channels, samples) if stereo
    if len(audio.shape) > 1:
        audio = audio.T

    # Pedalboard Phonk FX Chain
    board = get_adaptive_pedalboard(input_vocal_path)
    effected_audio = board(audio, sample_rate)

    # Transpose back if necessary
    if len(effected_audio.shape) > 1:
        effected_audio = effected_audio.T

    sf.write(output_vocal_path, effected_audio, sample_rate)
    return output_vocal_path