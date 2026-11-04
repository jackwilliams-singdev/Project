from pathlib import Path
from datetime import datetime
from google import genai

def analyze_machine_state(
    transcript_path: Path,
    output_path: Path,
    prompt_template: str,
    model_name: str = "gemini-3.5-flash-lite",
    machine_states: str = "Roping, Flaring, Transition, Blocked",
):
    print(f"Sending transcript to {model_name}")
    
    transcript_text = transcript_path.read_text(encoding="utf-8")
    
    client = genai.Client()
    
    prompt = prompt_template.replace("{{TRANSCRIPT}}", transcript_text)
    prompt = prompt.replace("{{STATES}}", machine_states)
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    
    # NEW: Add metadata footer to the analysis output
    metadata = (
        "\n\n"
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Model used:   {model_name}\n"
        f"Transcript:   {transcript_path.name}\n"
    )
    
    full_text = response.text + metadata
    output_path.write_text(full_text, encoding="utf-8")
    print(f"Saved State Analysis: {output_path.name}")