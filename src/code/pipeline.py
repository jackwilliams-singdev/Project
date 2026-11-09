from pathlib import Path
from datetime import datetime

from code.audio_utils import extract_audio, reduce_noise
from code.transcribe import transcribe_audio
from code.analyzer import analyze_machine_state
from utils import load_prompt
from utils.helper_functions import get_conf_key

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def run_pipeline(input_video: Path, outputs_dir: Path, config: dict):\

    # Pipeline settings (audio)
    audio_mode = get_conf_key(config, "AUDIO_MODE")
    run_denoise = get_conf_key(config, "RUN_DENOISE")

    # Audio settings
    audio_sample_rate = get_conf_key(config, "AUDIO_SAMPLE_RATE")
    audio_channel = get_conf_key(config, "AUDIO_CHANNEL")
    highpass_frequency = get_conf_key(config, "HIGHPASS_FREQUENCY")
    loudness_target_i = get_conf_key(config, "LOUDNESS_TARGET_I")
    loudness_target_tp = get_conf_key(config, "LOUDNESS_TARGET_TP")
    loudness_target_lra = get_conf_key(config, "LOUDNESS_TARGET_LRA")
    denoise_stationary = get_conf_key(config, "DENOISE_STATIONARY")
    denoise_prop_decrease = get_conf_key(config, "DENOISE_PROP_DECREASE")
    
    # Transcription and analysis settings
    transcription_engine = get_conf_key(config, "TRANSCRIPTION_ENGINE")
    parakeet_model = get_conf_key(config, "PARAKEET_MODEL")
    gemini_model = get_conf_key(config, "GEMINI_MODEL")
    prompt_name = get_conf_key(config, "PROMPT_NAME") 
    machine_states = get_conf_key(config, "MACHINE_STATES")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = outputs_dir / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"STARTING RUN: {run_dir.name}\n")

    # 1. Run Audio Extraction (Mode dictates if FFmpeg filters are applied)
    extracted_wav = extract_audio(
        input_video,
        run_dir,
        mode=audio_mode,
        timestamp=timestamp,
        sample_rate=audio_sample_rate,
        channel=audio_channel,
        highpass_frequency=highpass_frequency,
        loudness_target_i=loudness_target_i,
        loudness_target_tp=loudness_target_tp,
        loudness_target_lra=loudness_target_lra,
    )

    # 2. Run Denoising (Independent toggle)
    final_wav = extracted_wav
    if run_denoise and extracted_wav and extracted_wav.exists():
        
        # Save to a temporary name first
        temp_denoised_wav = run_dir / f"{input_video.stem}_{audio_mode}_{timestamp}_temp_denoise.wav"
        
        reduce_noise(
            extracted_wav,
            temp_denoised_wav,
            prop_decrease=denoise_prop_decrease,
            stationary=denoise_stationary,
            sample_rate=audio_sample_rate,
        )
        
        # Delete the intermediate file and rename the temp file to the final name
        if extracted_wav.exists():
            extracted_wav.unlink()
            
        final_wav = run_dir / f"{input_video.stem}_{audio_mode}_{timestamp}.wav"
        temp_denoised_wav.rename(final_wav)
        
        print(f"Final audio file: {final_wav.name}\n")

    # 3. Run Transcription
    actual_transcript_file = run_dir / f"{input_video.stem}_transcript_{timestamp}.txt"
    
    transcribe_audio(
        audio_path=final_wav, 
        text_path=actual_transcript_file, 
        engine=transcription_engine, 
        model_name=parakeet_model,
    )

    # 4. Run State Analysis
    state_file = run_dir / f"{input_video.stem}_state_analysis_{timestamp}.txt"
    prompt_template = load_prompt(prompt_name) 
    
    analyze_machine_state(
        actual_transcript_file,
        state_file,
        prompt_template,
        model_name=gemini_model,
        machine_states=machine_states,
    )
    
    print(f"RUN COMPLETE: saved as {run_dir.name}")