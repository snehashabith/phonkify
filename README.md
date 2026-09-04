# Phonkify

## Basic Details
### Team Name: Sneha Shabith

### Team Members
- Sneha Shabith

### Project Description
Phonkify is a cursed algorithmic Phonk generator that uses Demucs for vocal isolation and Spotify's Pedalboard library for real-time digital signal processing. It strips stems from any audio input, pitch-shifts and bitcrushes the vocals, and layers them over heavy 808 sub-bass, drift cowbells, and distorted drum loops to turn normal audio into dynamic, ear-blasting Drift Phonk.

### The Problem (that doesn't exist)
Nobody gets up in the morning thinking, I wish everything sounded like an aggressive, 140 BPM, high-octane Drift Phonk edit recorded on a 1990s walkie-talkie.

### The Solution (that nobody asked for)
I built an algorithmic DSP pipeline that forcefully injects bass, bitcrush distortion, and pitch-shifted cowbells into whatever unsuspecting audio file you drag and drop into it.

---

## Technical Details

### Technologies/Components Used
For Software:
- **Languages:** Python 3.10+, JavaScript (JSX)
- **Frameworks:** FastAPI (Backend REST API), React / Vite (Frontend UI), Tailwind CSS
- **Libraries:** 
  - `demucs` (Stem separation & vocal isolation)
  - `pedalboard` (Spotify DSP audio effects chain)
  - `librosa` (Pitch shifting, beat tracking, and spectral analysis)
  - `pydub` (Multi-track audio layering & headroom normalization)
  - `soundfile` / `numpy` (Raw array operations)
- **Tools:** `ffmpeg` (System audio encoding), Uvicorn (ASGI Server), npm

For Hardware:
- *N/A (Pure Software/DSP Project)*

---

### Implementation

For Software:

# Installation
```bash
# Clone the repository
git clone [https://github.com/SnehaShabith/phonkify.git](https://github.com/SnehaShabith/phonkify.git)
cd phonkify

# Backend Setup
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
pip install "setuptools<70.0.0"

# Frontend Setup
cd ../frontend
npm install

```
## Hosted Link
https://phonkify-9tni4y1qe-snehashabiths-projects.vercel.app

### Project Documentation
# Screenshots
Input Section
<img width="1882" height="612" alt="Screenshot 2026-09-04 055531" src="https://github.com/user-attachments/assets/9750f6e9-f20b-45f7-b29c-f0b836562907" />

Output listening and download section
<img width="1901" height="645" alt="image" src="https://github.com/user-attachments/assets/701137f9-d487-4885-8cb3-78b9c7e8a09e" />

### Project Demo

# Video

https://drive.google.com/file/d/1ZcGOWRUtpRFQcz5Yr_aof5AVniVL5htQ/view?usp=sharing

The demo video shows how an input mp3 file is dropped into the input deck, generate phonk is pressed 
The input audio is stemmed and processed using demucs and pedalboard
The output file is then made available for listening and it is then downloaded.


## Team Contributions

-Me: Everything



---

Made with ❤️ at TinkerHub Useless Projects 



![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)

![Static Badge](https://img.shields.io/badge/UselessProjects--26-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)


