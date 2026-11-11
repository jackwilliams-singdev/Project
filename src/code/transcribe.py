from pathlib import Path
from utils import append_run_metadata

import onnx_asr

def save_transcript(text_path: Path, lines: list):
    text_path.write_text("\n".join(lines), encoding="utf-8")

def transcribe_with_parakeet(audio_path: Path, text_path: Path, model_name: str):
    print(f"Transcribing Audio using Parakeet ONNX ({model_name})")

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

    save_transcript(text_path, lines)
    
    # Save metadata to the shared file
    append_run_metadata(text_path.parent, "Transcription", {
        "Engine": "Parakeet ONNX",
        "Model": model_name,
        "Audio_File": audio_path.name,
        "Transcript_File": text_path.name
    })
    print(f"Saved Transcription (Parakeet ONNX): {text_path.name}\n")


# Function to route to desired model
def transcribe_audio(
    audio_path: Path,
    text_path: Path,
    engine: str,
    model_name: str,
):
    if engine.lower() == "parakeet":
        transcribe_with_parakeet(audio_path, text_path, model_name)
    else:
        raise ValueError(f"Unknown transcription engine: {engine}. Use 'whisper' or 'parakeet'.")