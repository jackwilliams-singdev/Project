from pathlib import Path
from google import genai

def analyze_machine_state(
    transcript_path: Path,
    output_path: Path,
    prompt_template: str,
    model_name: str = "gemini-3.5-flash-lite",
    machine_states: str = "Roping, Flaring, Transition, Blocked",
):
    print(f"Sending transcript to {model_name}")
    
    # Read transcript text
    transcript_text = transcript_path.read_text(encoding="utf-8")
    
    # Initialize Gemini client
    client = genai.Client()
    
    # Insert the transcript into the prompt template.
    prompt = prompt_template.replace("{{TRANSCRIPT}}", transcript_text)
    prompt = prompt.replace("{{STATES}}", machine_states)
    
    # Call the API
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    output_path.write_text(response.text, encoding="utf-8")
    print(f"Saved State Analysis: {output_path.name}")