import static_ffmpeg
static_ffmpeg.add_paths()
import subprocess
from pathlib import Path
import noisereduce as nr
import librosa
import soundfile as sf

def extract_audio(
    mov: Path,
    wav_dir: Path,
    mode: str,
    timestamp: str,
    sample_rate: int = 48000,
    channel: str = "left",
    highpass_frequency: int = 100,
    loudness_target_i: int = -16,
    loudness_target_tp: float = -1.5,
    loudness_target_lra: int = 11,
) -> Path:
    
    wav_dir.mkdir(parents=True, exist_ok=True)
    
    apply_filters = (mode == "filtered")
    
    # New naming: IMG_5046_filtered_20261104_154512.wav
    wav = wav_dir / f"{mov.stem}_{mode}_{timestamp}.wav"
    
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
    
    if apply_filters:
        filter_chain = (
            f"{pan_filter},"
            f"highpass=f={highpass_frequency},"
            f"loudnorm=I={loudness_target_i}:TP={loudness_target_tp}:LRA={loudness_target_lra}"
        )
        cmd.extend(["-af", filter_chain])
        
        # Print filter settings (only for filtered mode)
        print(f"--- Audio Filter Settings ---")
        print(f"  Channel:   {channel}")
        print(f"  Highpass:  {highpass_frequency} Hz")
        print(f"  Loudnorm:  I={loudness_target_i}, TP={loudness_target_tp}, LRA={loudness_target_lra}")
        print(f"-----------------------------")
    else:
        cmd.extend(["-af", pan_filter])
        
    cmd.append(str(wav))
    subprocess.run(cmd, check=True)
    
    print(f"Extracted Audio ({mode}): {wav.name}")
    return wav

def reduce_noise(
    input_wav: Path,
    output_wav: Path,
    prop_decrease: float = 0.8,
    stationary: bool = True,
    sample_rate: int = 48000,
) -> Path:
    print(f"Applying noisereduce to {input_wav.name}")
    
    # Print denoise settings
    print(f"--- Denoise Settings ---")
    print(f"  Stationary:    {stationary}")
    print(f"  Prop Decrease: {prop_decrease}")
    print(f"------------------------")
    
    data, sr = librosa.load(str(input_wav), sr=sample_rate, mono=True)
    
    reduced = nr.reduce_noise(
        y=data, 
        sr=sr,
        stationary=stationary,
        prop_decrease=prop_decrease
    )
    
    sf.write(str(output_wav), reduced, sr)
    print(f"Saved denoised audio: {output_wav.name}")
    return output_wav