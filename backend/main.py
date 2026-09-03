import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydub import AudioSegment

from dsp.separator import isolate_vocals
from dsp.analyzer import pitch_and_stretch
from dsp.effects import apply_phonk_fx
from dsp.mixer import mix_track_with_drums

app = FastAPI(title="Phonk Generator Engine")

# Enable CORS for React frontend (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PRECOMPUTED_DIR = os.path.join(BASE_DIR, "precomputed")

os.makedirs(TEMP_DIR, exist_ok=True)

DRUM_LOOP_PATH = os.path.join(ASSETS_DIR, "phonk_drum_loop_140bpm.wav")

@app.get("/health")
def health_check():
    return {"status": "ok", "engine": "Algorithmic DSP Pipeline"}

@app.post("/generate-phonk")
async def generate_phonk(file: UploadFile = File(...)):
    """
    Full pipeline: Upload -> Vocal isolation -> Tempo/Pitch -> Phonk FX -> Adaptive backing -> MP3
    """
    job_id = str(uuid.uuid4())[:8]
    # Do not let a client supplied filename influence the output directory.
    safe_name = os.path.basename(file.filename or "upload.wav")
    input_file_path = os.path.join(TEMP_DIR, f"input_{job_id}_{safe_name}")
    vocal_raw_path = os.path.join(TEMP_DIR, f"vocals_raw_{job_id}.wav")
    vocal_pitched_path = os.path.join(TEMP_DIR, f"vocals_pitched_{job_id}.wav")
    vocal_fx_path = os.path.join(TEMP_DIR, f"vocals_fx_{job_id}.wav")
    final_output_path = os.path.join(TEMP_DIR, f"output_phonk_{job_id}.mp3")

    try:
        # Save uploaded file
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        original_duration_ms = len(AudioSegment.from_file(input_file_path))

        # Step 1: isolate the vocal stem so the generated rhythm has room to lead.
        isolate_vocals(input_file_path, vocal_raw_path)

        # Apply the dark drift preset, then use its rendered tempo for the loops.
        profile = pitch_and_stretch(vocal_raw_path, vocal_pitched_path, style="dark_drift")

        # Step 3: Apply Pedalboard Phonk FX Chain
        apply_phonk_fx(vocal_pitched_path, vocal_fx_path)

        # Step 4: Procedural Drum Layering & Mixdown
        mix_track_with_drums(
            vocal_fx_path, BASE_DIR, final_output_path,
            target_bpm=profile.target_bpm,
            backing_semitones=profile.backing_semitones,
            max_duration_ms=original_duration_ms,
        )

        return FileResponse(
            path=final_output_path, 
            media_type="audio/mpeg", 
            filename=f"phonk_{file.filename}.mp3"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DSP Processing Failed: {str(e)}")

    finally:
        # Cleanup temporary files (keep final output until served if needed)
        for p in [input_file_path, vocal_raw_path, vocal_pitched_path, vocal_fx_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

@app.get("/demo/{demo_id}")
def get_precomputed_demo(demo_id: str):
    """
    Fallback endpoint to serve precomputed golden demos instantaneously during the pitch.
    """
    demo_path = os.path.join(PRECOMPUTED_DIR, f"demo{demo_id}_phonk.mp3")
    if not os.path.exists(demo_path):
        raise HTTPException(status_code=404, detail="Demo track not found")
    return FileResponse(path=demo_path, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
