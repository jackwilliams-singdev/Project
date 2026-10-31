import os
from pathlib import Path
from google import genai
from google.genai import types

def analyze_machine_state(transcript_path: Path, output_path: Path):
    print(f"Sending transcript to Gemini for state analysis...")
    
    # 1. Read the transcript text
    transcript_text = transcript_path.read_text(encoding="utf-8")
    
    # 2. Initialize the Gemini client (it automatically picks up GEMINI_API_KEY)
    client = genai.Client()
    
    # 3. Construct the prompt
    # We tell Gemini exactly what to look for and how to format the output.
    prompt = f"""
    You are an expert engineer analyzing the operation of a hydrocyclone.
    Below is a timestamped transcript from a video where a person is describing the machine.
    
    Your task:
    1. Read the transcript and the timestamps.
    2. Identify the state of the hydrocyclone (e.g., Roping, Cutting, Fanning, Flaring, Transition, Blockage).
    3. Return a structured summary of what state the machine is in at different timestamps.
    
    Transcript:
    {transcript_text}
    """
    
    # 4. Call the API
    # Using a fast, cost-effective model like 3.8 Flash
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    
    # 5. Save the result
    output_path.write_text(response.text, encoding="utf-8")
    print(f"✔ Saved State Analysis: {output_path.name}")