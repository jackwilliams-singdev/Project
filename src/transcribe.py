from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel
from faster_whisper.utils import download_model
from platformdirs import user_cache_path

MODEL_BASE_DIR = user_cache_path("Project", appauthor=False) / "whisper"

# Whipser Implementation
def get_whisper_model(model_name: str, model_base_dir: Optional[Path] = None):
    
    model_dir = (model_base_dir or MODEL_BASE_DIR) / model_name
    if not (model_dir / "model.bin").exists():
        print(f"Downloading Whisper model '{model_name}' (first run only)...")
        model_dir.mkdir(parents=True, exist_ok=True)
        download_model(model_name, output_dir=str(model_dir))
    
    return WhisperModel(str(model_dir), device="cpu", compute_type="int8")

def transcribe_with_whisper(
    audio_path: Path,
    text_path: Path,
    model_name: str,
    model_base_dir: Optional[Path] = None,
):
    print(f"Transcribing {audio_path.name} using Whisper ({model_name})...")
    
    model = get_whisper_model(model_name, model_base_dir)

    segments, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        language="en",
        vad_filter=False,
        vad_parameters=dict(min_silence_duration_ms=500),
        condition_on_previous_text=False,
        word_timestamps=True,
        hotwords="roping, flaring, transition",
    )

    lines = []
    for segment in segments:
        lines.append(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}")

    text_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved Transcription: {text_path.name}")


# Parakeet Implementation
def transcribe_with_parakeet(audio_path: Path, text_path: Path, model_name: str):
    print(f"Transcribing {audio_path.name} using Parakeet ({model_name})...")
    
    # NeMo takes a long time to load, so we only import it if we actually need it
    import nemo.collections.asr as nemo_asr

    # NeMo will automatically download the model to its cache directory on first run
    asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name)

    # NeMo expects a list of file paths
    hypotheses = asr_model.transcribe([str(audio_path)], timestamps=True)

    result = hypotheses[0]
    
    # Format timestamps
    lines = []
    if hasattr(result, 'timestamp') and 'segment' in result.timestamp:
        for seg in result.timestamp['segment']:
            lines.append(f"[{seg['start']:.2f}s -> {seg['end']:.2f}s] {seg['segment']}")
    else:
        lines.append(result.text)

    text_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved Transcription (Parakeet): {text_path.name}")


# Function to route to desired model
def transcribe_audio(
    audio_path: Path,
    text_path: Path,
    engine: str,
    model_name: str,
    model_base_dir: Optional[Path] = None,
):

    if engine.lower() == "whisper":
        transcribe_with_whisper(audio_path, text_path, model_name, model_base_dir)
    elif engine.lower() == "parakeet":
        transcribe_with_parakeet(audio_path, text_path, model_name)
    else:
        raise ValueError(f"Unknown transcription engine: {engine}. Use 'whisper' or 'parakeet'.")