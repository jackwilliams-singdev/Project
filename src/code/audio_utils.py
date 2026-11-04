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
def extract_audio(
    mov: Path,
    wav_dir: Path,
    mode: str,
    sample_rate: int = 48000,
    channel: str = "left",
    highpass_frequency: int = 100,
    loudness_target_i: int = -16,
    loudness_target_tp: float = -1.5,
    loudness_target_lra: int = 11,
) -> Path:
    
    # Extracts either raw or filtered audio
    wav_dir.mkdir(parents=True, exist_ok=True)
    
    apply_filters = (mode == "filtered")
    suffix = "_filtered" if apply_filters else "_raw"
    wav = wav_dir / f"{mov.stem}{suffix}.wav"
    
    channel_filters = {
        "left": "pan=mono|c0=c0",
        "right": "pan=mono|c0=c1",
        "mix": "pan=mono|c0=0.5*c0+0.5*c1",
    }
    if channel not in channel_filters:
        raise ValueError("channel must be 'left', 'right', or 'mix'")
    pan_filter = channel_filters[channel]

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-i", str(mov), "-vn", "-ar", str(sample_rate), "-c:a", "pcm_s16le"]
    
    # Audio filters
    if apply_filters:
        filter_chain = (
            f"{pan_filter},"
            f"highpass=f={highpass_frequency},"
            f"loudnorm=I={loudness_target_i}:TP={loudness_target_tp}:LRA={loudness_target_lra}"
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
def reduce_noise(
    input_wav: Path,
    output_wav: Path,
    prop_decrease: float = 0.8,
    stationary: bool = True,
    sample_rate: int = 48000,
) -> Path:
    """Applies noisereduce to an audio file."""
    print(f"Applying noisereduce to {input_wav.name}")
    
    # Load audio
    data, sr = librosa.load(str(input_wav), sr=sample_rate, mono=True)
    
    # Run the noise reduction
    reduced = nr.reduce_noise(
        y=data, 
        sr=sr,
        stationary=stationary,
        prop_decrease=prop_decrease
    )
    
    # Save the cleaned audio
    sf.write(str(output_wav), reduced, sr)
    print(f"Saved denoised audio: {output_wav.name}")
    return output_wav