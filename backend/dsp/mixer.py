import os
from pydub import AudioSegment

def mix_track_with_drums(
    effected_vocal_path: str, 
    drum_loop_path: str, 
    output_path: str, 
    vocal_gain_db: float = 3.0
) -> str:
    """
    Loops the pre-baked 140 BPM Phonk drums and overlays the processed vocals.
    """
    vocal_track = AudioSegment.from_file(effected_vocal_path)
    
    if os.path.exists(drum_loop_path):
        drum_track = AudioSegment.from_file(drum_loop_path)

        # Loop drums to cover the entire vocal duration
        if len(drum_track) < len(vocal_track):
            loops_needed = (len(vocal_track) // len(drum_track)) + 1
            drum_track = drum_track * loops_needed

        # Trim extra drum tail to match vocal length
        drum_track = drum_track[:len(vocal_track)]

        # Mix vocals over drum loop
        final_mix = drum_track.overlay(vocal_track + vocal_gain_db)
    else:
        # Fallback: export vocal only if drum asset is missing
        final_mix = vocal_track + vocal_gain_db

    final_mix.export(output_path, format="mp3", bitrate="192k")
    return output_path