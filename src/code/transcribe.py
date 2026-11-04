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


import onnx_asr

def transcribe_with_parakeet(audio_path: Path, text_path: Path, model_name: str):
    print(f"Transcribing {audio_path.name} using Parakeet ONNX ({model_name})...")

    model = onnx_asr.load_model(model_name).with_timestamps()
    result = model.recognize(str(audio_path))

    lines = []
    current_tokens = []
    segment_start = None
    last_end = None

    for i, token in enumerate(result.tokens):
        start = result.timestamps[i]
        end = result.timestamps[i + 1] if i + 1 < len(result.timestamps) else start

        # Detect long silence (> 1.5s) → force segment break
        silence_gap = start - last_end if last_end is not None else 0

        if segment_start is None:
            segment_start = start

        current_tokens.append(token)
        last_end = end

        # Break conditions: sentence-ending punctuation or long silence
        is_sentence_end = token.strip() in {".", "?", "!"}
        if is_sentence_end or silence_gap > 1.5:
            text = "".join(current_tokens).strip()
            if text:
                lines.append(f"[{segment_start:.2f}s -> {end:.2f}s] {text}")
            current_tokens = []
            segment_start = None
            last_end = None

    # Flush remaining tokens
    if current_tokens:
        text = "".join(current_tokens).strip()
        if text:
            lines.append(f"[{segment_start:.2f}s -> {last_end:.2f}s] {text}")

    text_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved Transcription (Parakeet ONNX): {text_path.name}")


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