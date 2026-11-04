import yaml
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = SRC_ROOT / "prompts"

def load_secrets(secrets_path="configs/secrets.yaml"):
    p = Path(secrets_path)
    if not p.exists():
        print(f"Warning: {secrets_path} not found; using existing environment variables.")
        return {}
    with open(p, "r") as f:
        return yaml.safe_load(f) or {}
    
def load_prompt(prompt_name: str) -> str:

    prompt_path = PROMPTS_DIR / prompt_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")

def setup_directories(outputs_dir: Path, mode: str, run_analysis: bool):
    mode_dir = outputs_dir / mode
    audio_dir = mode_dir / "audio"
    transcript_dir = mode_dir / "transcript"
    analysis_dir = mode_dir / "analysis"

    audio_dir.mkdir(parents=True, exist_ok=True)
    transcript_dir.mkdir(parents=True, exist_ok=True)
    if run_analysis:
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
    return audio_dir, transcript_dir, analysis_dir