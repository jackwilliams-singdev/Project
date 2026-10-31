import yaml
import shutil
from pathlib import Path

# Import our custom modules
from audio_utils import extract_audio
from transcribe import transcribe_audio
from analyzer import analyze_machine_state

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    # 1. Load Settings
    config = load_config()
    
    RUN_EXTRACTION = config.get("RUN_AUDIO_EXTRACTION", True)
    RUN_TRANSCRIPTION = config.get("RUN_TRANSCRIPTION", True)
    AUDIO_MODE = config.get("AUDIO_MODE", "raw")
    
    INPUT_VIDEO = Path(config["INPUT_VIDEO"])
    OUTPUT_DIR = Path(config["OUTPUT_DIR"])
    WAV_DIR = Path(config["WAV_DIR"])

    if not INPUT_VIDEO.exists():
        print(f"File not found: {INPUT_VIDEO}")
        exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"--- Starting Pipeline for {INPUT_VIDEO.name} ---")
    
    final_wav = None

    # 2. Run Audio Extraction
    if RUN_EXTRACTION:
        intermediate_wav = extract_audio(INPUT_VIDEO, WAV_DIR, mode=AUDIO_MODE)
        final_wav = OUTPUT_DIR / intermediate_wav.name
        shutil.move(str(intermediate_wav), str(final_wav))
    else:
        # If skipping extraction, look for the existing file
        suffix = "_filtered" if AUDIO_MODE == "filtered" else "_raw"
        final_wav = OUTPUT_DIR / f"{INPUT_VIDEO.stem}{suffix}.wav"
        
    # 3. Run Transcription
    if RUN_TRANSCRIPTION:
        if final_wav and final_wav.exists():
            transcript_file = OUTPUT_DIR / f"{INPUT_VIDEO.stem}_transcript.txt"
            transcribe_audio(final_wav, transcript_file)
        else:
            print(f"⚠️ Cannot transcribe: Audio file not found at {final_wav}")

    if config.get("RUN_STATE_ANALYSIS", False):
        if final_wav and final_wav.exists():
            # We need the transcript to exist to analyze it
            transcript_file = OUTPUT_DIR / f"{INPUT_VIDEO.stem}_transcript.txt"
            if transcript_file.exists():
                state_file = OUTPUT_DIR / f"{INPUT_VIDEO.stem}_state_analysis.txt"
                analyze_machine_state(transcript_file, state_file)
            else:
                print("⚠️ Cannot analyze state: Transcript file not found.")
    
    print("--- Pipeline Complete! ---")