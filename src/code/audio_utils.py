import static_ffmpeg
static_ffmpeg.add_paths()
import subprocess
from pathlib import Path
import noisereduce as nr
import librosa
import soundfile as sf
from utils import append_run_metadata

def extract_audio(
    mov: Path,
    wav_dir: Path,
    mode: str,
    timestamp: str,
    sample_rate: int,
    channel: str,
    highpass_frequency: int,
    loudness_target_i: int,
    loudness_target_tp: float,
    loudness_target_lra: int,
) -> Path:
    
    wav_dir.mkdir(parents=True, exist_ok=True)
    apply_filters = (mode == "filtered")
    
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
        
        print(f"AUDIO FILTER SETTINGS:")
        print(f"  Channel:   {channel}")
        print(f"  Highpass:  {highpass_frequency} Hz")
        print(f"  Loudnorm:  I={loudness_target_i}, TP={loudness_target_tp}, LRA={loudness_target_lra}\n")
        
        append_run_metadata(wav_dir, "Audio Extraction", {
            "Mode": mode,
            "Channel": channel,
            "Highpass": f"{highpass_frequency} Hz",
            "Loudnorm_I": loudness_target_i,
            "Loudnorm_TP": loudness_target_tp,
            "Loudnorm_LRA": loudness_target_lra,
            "Source_File": mov.name
        })
    else:
        cmd.extend(["-af", pan_filter])
        append_run_metadata(wav_dir, "Audio Extraction", {
            "Mode": mode,
            "Channel": channel,
            "Source_File": mov.name
        })
        
    cmd.append(str(wav))
    subprocess.run(cmd, check=True)
    
    print(f"Audio Extracted")
    return wav

def reduce_noise(
    input_wav: Path,
    output_wav: Path,
    prop_decrease: float = 0.8,
    stationary: bool = True,
    sample_rate: int = 48000,
) -> Path:
    print(f"Applying noisereduce\n")
    
    print(f"DENOISE SETTINGS:")
    print(f"  Stationary:    {stationary}")
    print(f"  Prop Decrease: {prop_decrease}")
    
    append_run_metadata(output_wav.parent, "Denoising", {
        "Stationary": stationary,
        "Prop_Decrease": prop_decrease,
        "Input_File": input_wav.name
    })
    
    data, sr = librosa.load(str(input_wav), sr=sample_rate, mono=True)
    
    reduced = nr.reduce_noise(
        y=data, 
        sr=sr,
        stationary=stationary,
        prop_decrease=prop_decrease
    )
    
    sf.write(str(output_wav), reduced, sr)
    print()
    print(f"Audio Denoised")
    return output_wav