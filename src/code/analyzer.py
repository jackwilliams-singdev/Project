from pathlib import Path
from datetime import datetime
from google import genai
from utils import append_run_metadata

def analyze_machine_state(
    transcript_path: Path,
    output_path: Path,
    prompt_template: str,
    model_name: str,
    machine_states: str,
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
    
    output_path.write_text(response.text, encoding="utf-8")
    append_run_metadata(output_path.parent, "State Analysis", {
        "Model": model_name,
        "Transcript_File": transcript_path.name,
        "Analysis_File": output_path.name
    })
    print(f"Saved State Analysis: {output_path.name}\n")