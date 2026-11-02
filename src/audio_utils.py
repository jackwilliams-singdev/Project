import static_ffmpeg
static_ffmpeg.add_paths()
import subprocess
from pathlib import Path
import noisereduce as nr
import librosa
import soundfile as sf

"""
A function to extract and filter the audio.
"""
def extract_audio(mov: Path, wav_dir: Path, mode: str) -> Path:
    
    # Extracts either raw or filtered audio
    wav_dir.mkdir(parents=True, exist_ok=True)
    
    apply_filters = (mode == "filtered")
    suffix = "_filtered" if apply_filters else "_raw"
    wav = wav_dir / f"{mov.stem}{suffix}.wav"
    
    # Left (c0) or right (c1) channel
    pan_filter = "pan=mono|c0=c0"
    
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-i", str(mov), "-vn", "-ar", "48000", "-c:a", "pcm_s16le"]
    
    # Audio filters
    if apply_filters:
        filter_chain = (
            f"{pan_filter},"
            "highpass=f=100,"
            "loudnorm=I=-16:TP=-1.5:LRA=11"
        )
        cmd.extend(["-af", filter_chain])
    else:
        cmd.extend(["-af", pan_filter])
        
    cmd.append(str(wav))
    subprocess.run(cmd, check=True)
    
    print(f"Extracted Audio ({mode}): {wav.name}")
    return wav

"""
Applied noise reduction tool to hopefully mitigate slurry noise.
"""
def reduce_noise(input_wav: Path, output_wav: Path, prop_decrease: float = 0.8) -> Path:
    """Applies noisereduce to an audio file."""
    print(f"Applying noisereduce to {input_wav.name}")
    
    # Load audio
    data, sr = librosa.load(str(input_wav), sr=48000, mono=True)
    
    # Run the noise reduction
    reduced = nr.reduce_noise(
        y=data, 
        sr=sr,
        stationary=True, 
        prop_decrease=prop_decrease
    )
    
    # Save the cleaned audio
    sf.write(str(output_wav), reduced, sr)
    print(f"Saved denoised audio: {output_wav.name}")
    return output_wav