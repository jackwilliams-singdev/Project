import os
from pathlib import Path

# Import the new parser and helper functions
from utils.cmd_arg_parse import cmd_line_config
from utils.helper_functions import get_conf_key
from pipeline import run_pipeline

def main(conf):

    api_key = get_conf_key(conf, "GEMINI_API_KEY", required=False, default=None)
    
    if api_key:
        os.environ["GEMINI_API_KEY"] = str(api_key)
    else:
        print("Warning: Key not found in config or secrets.")

    input_video_str = get_conf_key(conf, "INPUT_VIDEO")
    outputs_dir_str = get_conf_key(conf, "OUTPUTS_DIR")

    INPUT_VIDEO = Path(input_video_str)
    OUTPUTS_DIR = Path(outputs_dir_str)

    if not INPUT_VIDEO.exists():
        print(f"File not found: {INPUT_VIDEO}")
        exit(1)

    print()
    print(f"Starting Pipeline for {INPUT_VIDEO.name}")

    run_pipeline(
        input_video=INPUT_VIDEO, 
        outputs_dir=OUTPUTS_DIR, 
        config=conf
    )

if __name__ == "__main__":
    # Parse both config and secrets into a single dictionary
    conf = cmd_line_config(description="Hydrocyclone Analysis Pipeline")
    main(conf)