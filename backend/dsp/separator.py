import os
import torch
import torchaudio
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
    wav, sr = torchaudio.load(input_audio_path)
    
    # Resample to model sample rate (44.1kHz) if needed
    if sr != MODEL.samplerate:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=MODEL.samplerate)
        wav = resampler(wav)
        sr = MODEL.samplerate

    # Add batch dimension and move to device
    wav_tensor = wav.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        sources = apply_model(MODEL, wav_tensor)[0]

    # Index 3 corresponds to vocals in Demucs htdemucs output
    vocal_tensor = sources[3].cpu()

    os.makedirs(os.path.dirname(output_vocal_path), exist_ok=True)
    torchaudio.save(output_vocal_path, vocal_tensor, sr)
    
    return output_vocal_path
