import os
import yaml
from pathlib import Path

from audio_utils import extract_audio, reduce_noise
from transcribe import transcribe_audio
from analyzer import analyze_machine_state

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def load_config(config_path="configs/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
    
def load_secrets(secrets_path="configs/secrets.yaml"):
    p = Path(secrets_path)
    if not p.exists():
        print(f"Warning: {secrets_path} not found; using existing environment variables.")
        return {}
    with open(p, "r") as f:
        return yaml.safe_load(f) or {}
    
def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")

if __name__ == "__main__":
    # 1. Load Settings
    config = load_config()
    secrets = load_secrets()

    for key, value in secrets.items():
        os.environ.setdefault(key, str(value))
    
    RUN_EXTRACTION = config.get("RUN_AUDIO_EXTRACTION", True)
    RUN_TRANSCRIPTION = config.get("RUN_TRANSCRIPTION", True)
    RUN_STATE_ANALYSIS = config.get("RUN_STATE_ANALYSIS", False)
    RUN_DENOISE = config.get("RUN_DENOISE", True)

    AUDIO_MODE = config.get("AUDIO_MODE", "raw")

    TRANSCRIPTION_ENGINE = config.get("TRANSCRIPTION_ENGINE", "whisper")
    WHISPER_MODEL = config.get("WHISPER_MODEL", "distil-large-v3")
    PARAKEET_MODEL = config.get("PARAKEET_MODEL", "nvidia/parakeet-tdt-0.6b-v3")

    INPUT_VIDEO = Path(config["INPUT_VIDEO"])
    OUTPUTS_DIR = Path(config["OUTPUTS_DIR"])

    if not INPUT_VIDEO.exists():
        print(f"File not found: {INPUT_VIDEO}")
        exit(1)

    # Per-run output layout: Outputs/<mode>/{audio,transcript,analysis}
    MODE_DIR = OUTPUTS_DIR / AUDIO_MODE
    AUDIO_DIR = MODE_DIR / "audio"
    TRANSCRIPT_DIR = MODE_DIR / "transcript"
    ANALYSIS_DIR = MODE_DIR / "analysis"

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    if RUN_STATE_ANALYSIS:
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"--- Starting Pipeline for {INPUT_VIDEO.name} (mode: {AUDIO_MODE}) ---")

    final_wav = None

    # 2. Run Audio Extraction
    if RUN_EXTRACTION:
        final_wav = extract_audio(INPUT_VIDEO, AUDIO_DIR, mode=AUDIO_MODE)
    else:
        suffix = "_filtered" if AUDIO_MODE == "filtered" else "_raw"
        final_wav = AUDIO_DIR / f"{INPUT_VIDEO.stem}{suffix}.wav"

    # 2.5 Run Denoising
    if RUN_DENOISE and final_wav and final_wav.exists():
        denoised_wav = AUDIO_DIR / f"{INPUT_VIDEO.stem}_denoised.wav"
        final_wav = reduce_noise(final_wav, denoised_wav)

    # 3. Run Transcription
    if RUN_TRANSCRIPTION:
        if final_wav and final_wav.exists():
            transcript_file = TRANSCRIPT_DIR / f"{INPUT_VIDEO.stem}_transcript.txt"
            active_model = WHISPER_MODEL if TRANSCRIPTION_ENGINE == "whisper" else PARAKEET_MODEL
            
            transcribe_audio(
                audio_path=final_wav, 
                text_path=transcript_file, 
                engine=TRANSCRIPTION_ENGINE, 
                model_name=active_model
            )
        else:
            print(f"Cannot transcribe: Audio file not found at {final_wav}")

    if RUN_STATE_ANALYSIS:
        if final_wav and final_wav.exists():
            transcript_file = TRANSCRIPT_DIR / f"{INPUT_VIDEO.stem}_transcript.txt"
            if transcript_file.exists():
                state_file = ANALYSIS_DIR / f"{INPUT_VIDEO.stem}_state_analysis.txt"
                prompt_template = load_prompt(PROJECT_ROOT / config["PROMPT_FILE"])
                analyze_machine_state(
                    transcript_file,
                    state_file,
                    prompt_template,
                )
            else:
                print("Cannot analyze state: Transcript file not found.")

    print("--- Pipeline Complete! ---")