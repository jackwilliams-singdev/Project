from pathlib import Path
from faster_whisper import WhisperModel

def transcribe_audio(audio_path: Path, text_path: Path):
    print(f"Loading Whisper model and transcribing {audio_path.name}...")
    
    model = WhisperModel("small", device="cpu", compute_type="int8")
    
    segments, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        language="en",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        condition_on_previous_text=False,
        hotwords="roping, cutting, fanning, flaring",
    )

    lines = []
    for segment in segments:
        lines.append(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

    full_text = "\n".join(lines)
    text_path.write_text(full_text, encoding="utf-8")
    print(f"Saved Transcription: {text_path.name}")