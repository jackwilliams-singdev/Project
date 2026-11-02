from pathlib import Path

from audio_utils import extract_audio, reduce_noise
from transcribe import transcribe_audio
from analyzer import analyze_machine_state
from utils import load_prompt, PROJECT_ROOT

def run_pipeline(input_video: Path, outputs_dir: Path, config: dict):
    
    # Extract settings from config with defaults
    audio_mode = config.get("AUDIO_MODE", "raw")
    run_extraction = config.get("RUN_AUDIO_EXTRACTION", True)
    run_transcription = config.get("RUN_TRANSCRIPTION", True)
    run_state_analysis = config.get("RUN_STATE_ANALYSIS", False)
    run_denoise = config.get("RUN_DENOISE", True)
    
    transcription_engine = config.get("TRANSCRIPTION_ENGINE", "whisper")
    whisper_model = config.get("WHISPER_MODEL", "distil-large-v3")
    parakeet_model = config.get("PARAKEET_MODEL", "nvidia/parakeet-tdt-0.6b-v3")

    # Setup directories internally
    mode_dir = outputs_dir / audio_mode
    audio_dir = mode_dir / "audio"
    transcript_dir = mode_dir / "transcript"
    analysis_dir = mode_dir / "analysis"

    audio_dir.mkdir(parents=True, exist_ok=True)
    transcript_dir.mkdir(parents=True, exist_ok=True)
    if run_state_analysis:
        analysis_dir.mkdir(parents=True, exist_ok=True)

    final_wav = None

    # Run Audio Extraction
    if run_extraction:
        final_wav = extract_audio(input_video, audio_dir, mode=audio_mode)
    else:
        suffix = "_filtered" if audio_mode == "filtered" else "_raw"
        final_wav = audio_dir / f"{input_video.stem}{suffix}.wav"

    # Run Denoising
    if run_denoise and final_wav and final_wav.exists():
        denoised_wav = audio_dir / f"{input_video.stem}_denoised.wav"
        final_wav = reduce_noise(final_wav, denoised_wav)

    # Run Transcription
    if run_transcription:
        if final_wav and final_wav.exists():
            transcript_file = transcript_dir / f"{input_video.stem}_transcript.txt"
            active_model = whisper_model if transcription_engine == "whisper" else parakeet_model
            
            transcribe_audio(
                audio_path=final_wav, 
                text_path=transcript_file, 
                engine=transcription_engine, 
                model_name=active_model
            )
        else:
            print(f"Cannot transcribe: Audio file not found at {final_wav}")

    # Run State Analysis
    if run_state_analysis:
        if final_wav and final_wav.exists():
            transcript_file = transcript_dir / f"{input_video.stem}_transcript.txt"
            if transcript_file.exists():
                state_file = analysis_dir / f"{input_video.stem}_state_analysis.txt"
                prompt_template = load_prompt(PROJECT_ROOT / config["PROMPT_FILE"])
                analyze_machine_state(
                    transcript_file,
                    state_file,
                    prompt_template,
                )
            else:
                print("Cannot analyze state: Transcript file not found.")