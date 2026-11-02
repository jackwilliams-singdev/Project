import os
from pathlib import Path

from utils import load_config, load_secrets
from pipeline import run_pipeline

if __name__ == "__main__":

    config = load_config()
    secrets = load_secrets()

    for key, value in secrets.items():
        os.environ.setdefault(key, str(value))
    
    INPUT_VIDEO = Path(config["INPUT_VIDEO"])
    OUTPUTS_DIR = Path(config["OUTPUTS_DIR"])
    AUDIO_MODE = config.get("AUDIO_MODE", "raw")

    if not INPUT_VIDEO.exists():
        print(f"File not found: {INPUT_VIDEO}")
        exit(1)

    print(f"--- Starting Pipeline for {INPUT_VIDEO.name} (mode: {AUDIO_MODE}) ---")

    run_pipeline(
        input_video=INPUT_VIDEO, 
        outputs_dir=OUTPUTS_DIR, 
        config=config
    )
    print("--- Pipeline Complete! ---")