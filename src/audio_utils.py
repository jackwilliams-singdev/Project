import static_ffmpeg
static_ffmpeg.add_paths()
import subprocess
from pathlib import Path

def extract_audio(mov: Path, wav_dir: Path, mode: str) -> Path:
    """Extracts audio based on mode, raw or filtered"""
    wav_dir.mkdir(parents=True, exist_ok=True)
    
    apply_filters = (mode == "filtered")
    suffix = "_filtered" if apply_filters else "_raw"
    wav = wav_dir / f"{mov.stem}{suffix}.wav"
    
    pan_filter = "pan=mono|c0=c1"
    
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-i", str(mov), "-vn", "-ar", "48000", "-c:a", "pcm_s16le"]
    
    if apply_filters:
        filter_chain = f"{pan_filter},highpass=f=100,loudnorm=I=-16:TP=-1.5:LRA=11"
        cmd.extend(["-af", filter_chain])
    else:
        cmd.extend(["-af", pan_filter])
        
    cmd.append(str(wav))
    subprocess.run(cmd, check=True)
    
    print(f"Extracted Audio ({mode}): {wav.name}")
    return wav