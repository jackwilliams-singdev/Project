from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = SRC_ROOT / "prompts"
    
def load_prompt(prompt_name: str) -> str:

    prompt_path = PROMPTS_DIR / prompt_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")

def append_run_metadata(run_dir: Path, section: str, data: dict):
    
    metadata_file = run_dir / "run_metadata.txt"
    lines = [f"\n[{section}]"]
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    
    text_to_append = "\n".join(lines) + "\n"
    
    # Append to the file
    with open(metadata_file, "a", encoding="utf-8") as f:
        f.write(text_to_append)