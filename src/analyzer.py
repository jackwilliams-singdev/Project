import os
from pathlib import Path
from google import genai

def analyze_machine_state(
    transcript_path: Path,
    output_path: Path,
    prompt_template: str,
):
    print(f"Sending transcript to Gemini for state analysis...")
    
    # 1. Read the transcript text
    transcript_text = transcript_path.read_text(encoding="utf-8")
    
    # 2. Initialize the Gemini client (it automatically picks up GEMINI_API_KEY)
    client = genai.Client()
    
    # 3. Insert the transcript into the prompt template.
    prompt = prompt_template.replace("{{TRANSCRIPT}}", transcript_text)
    
    # 4. Call the API
    # Use a fast, cost-effective model.
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )
    
    # 5. Save the result
    output_path.write_text(response.text, encoding="utf-8")
    print(f"✔ Saved State Analysis: {output_path.name}")