import os
import torch
import numpy as np
import soundfile as sf
from pydub import AudioSegment
import scipy.signal

# Demucs 4 still accesses the pre-SciPy-1.13 alias during import.
if not hasattr(scipy.signal, "hann"):
    scipy.signal.hann = scipy.signal.windows.hann
from demucs.apply import apply_model
from demucs.pretrained import get_model

# Load model once at module import to avoid latency on API requests
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL = get_model('htdemucs')
MODEL.to(DEVICE)
MODEL.eval()

def isolate_vocals(input_audio_path: str, output_vocal_path: str) -> str:
    """
    Separates vocals from an audio file using Demucs and saves the vocal stem as WAV.
    """
    # torchaudio 2.9 delegates decoding to TorchCodec, which is not bundled in
    # every install.  PyDub uses the project's FFmpeg decoder instead, keeping
    # MP3/WAV uploads functional without a TorchCodec runtime dependency.
    source = AudioSegment.from_file(input_audio_path).set_frame_rate(MODEL.samplerate)
    raw_samples = np.array(source.get_array_of_samples())
    if not len(raw_samples):
        raise ValueError("The uploaded audio contains no samples")
    scale = float(1 << (8 * source.sample_width - 1))
    wav = torch.from_numpy(
        raw_samples.reshape((-1, source.channels)).T.astype(np.float32) / scale
    )
    sr = MODEL.samplerate

    # Add batch dimension and move to device
    wav_tensor = wav.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        sources = apply_model(MODEL, wav_tensor)[0]

    # Index 3 corresponds to vocals in Demucs htdemucs output
    vocal_index = MODEL.sources.index("vocals")
    vocal_tensor = sources[vocal_index].cpu()

    os.makedirs(os.path.dirname(output_vocal_path), exist_ok=True)
    sf.write(output_vocal_path, vocal_tensor.T.numpy(), sr)
    
    return output_vocal_path
