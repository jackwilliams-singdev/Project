Here is a pipeline I made that takes a Iphone (.mov) file, filters the audio, transcribes it, and returns a structured analysis of what happens at each timestamps.

This was applied to hydrocylone videos and can return in the analysis what state the machine is in at during a certain time period (based on speech in the video).

**Setting Things Up:**

## 1. Prerequisites
You must have the following installed on your machine:
- **Python 3.10+**
- **FFmpeg** (If not installed globally, the pipeline uses `static-ffmpeg` to grab it automatically).
- **uv** (Recommended package manager) or `pip`.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## 3. Environment Setup

Open your terminal and run the command for your OS:
* **Linux:** `nano ~/.bashrc`
* **macOS:** `nano ~/.zshrc`

**Important:** You MUST replace `/absolute/path/to/your/Project` with the actual, full path to where you cloned the repository on your machine.
Scroll to the very bottom of the file and paste the following lines. 

```bash
export PYTHONPATH="/absolute/path/to/your/Project/src"
export LOGGING_CONFIG="/absolute/path/to/your/Project/src/configs/logging.yaml"
export ROOT_LOGGER_NAME="hydrocyclone"
export HF_HUB_CACHE="/absolute/path/to/a/large/drive/hf_cache"
```

Save the file (Ctrl+0, Enter, Ctrl+X).
Then apply changes using 

```bash
source ~/.bashrc  # (or source ~/.zshrc on macOS)
```
## 4. Configuration

Before running the pipeline, you must provide it with your specific settings, paths, and your Gemini API key.

Create a file called config.yaml in the configs folder.
Here is the template you should use for the config yaml file.

```bash
# TRANSCRIPTION SETTINGS
# =====================================================================
# Valid Inputs: "parakeet" (Whisper has been removed)
TRANSCRIPTION_ENGINE: "parakeet"

# Valid Inputs: Any valid HuggingFace ONNX model repository.
# Default: "nemo-parakeet-tdt-0.6b-v3"
PARAKEET_MODEL: "nemo-parakeet-tdt-0.6b-v3"

# ANALYSIS SETTINGS
# =====================================================================
# Valid Inputs: Any valid Gemini model string (e.g., "gemini-1.5-pro", "gemini-3.5-flash-lite")
GEMINI_MODEL: "gemini-3.5-flash-lite"

# Valid Inputs: The name of a .txt file located inside the `src/prompts/` directory.
PROMPT_NAME: "prompt1.txt"

# Valid Inputs: A comma-separated string of the machine states you want the AI to look for.
MACHINE_STATES: "Roping, Flaring, Transition, Blocked"

# AUDIO FILTERING SETTINGS (Applied via FFmpeg)
# =====================================================================
# Valid Inputs: "raw" or "filtered"
# "filtered" = Applies Highpass and Loudnorm filters.
# "raw" = Skips FFmpeg filters entirely.
AUDIO_MODE: "filtered"

# Valid Inputs: true or false
# true = Applies noise reduction (noisereduce library).
# false = Skips noise reduction.
RUN_DENOISE: true

# Valid Inputs: Any positive integer (e.g., 16000, 44100, 48000).
# Practical: 48000 (video standard) or 16000 (speech standard).
AUDIO_SAMPLE_RATE: 48000

# Valid Inputs: "left", "right", or "mix" (case-sensitive string).
AUDIO_CHANNEL: "right"

# Valid Range: 1 to 20000 (Hz). 
# Practical Range: 80 to 200 Hz (removes low-frequency rumble).
HIGHPASS_FREQUENCY: 100

# Valid Range: -70.0 to -5.0 (LUFS). 
# Practical Range: -16 (podcast standard) to -14 (streaming standard).
LOUDNESS_TARGET_I: -16

# Valid Range: -9.0 to 0.0 (dBTP). 
# Practical Range: -1.0 to -2.0 (prevents audio clipping).
LOUDNESS_TARGET_TP: -1.5

# Valid Range: 1.0 to 50.0 (LU).
# Practical Range: 7 to 11 (keeps spoken word volume consistent).
LOUDNESS_TARGET_LRA: 11

# NOISE REDUCTION SETTINGS (Applied via noisereduce)
# =====================================================================
# Valid Inputs: true or false
# true = Assumes constant background noise (e.g., a fan).
# false = Adapts to changing background noise (e.g., traffic).
DENOISE_STATIONARY: true

# Valid Range: 0.0 to 1.0 (Float).
# 0.0 = no noise reduction. 1.0 = maximum reduction (may cause robotic artifacts).
DENOISE_PROP_DECREASE: 0.8

# DIRECTORY PATHS
# =====================================================================
# Valid Inputs: Absolute paths to your video file and output directory.
# MUST be absolute paths (e.g., "/home/user/videos/input.mov").
INPUT_VIDEO: "/absolute/path/to/your/video.mov"
OUTPUTS_DIR: "/absolute/path/to/your/output/folder"
```

Next create a secrets.yaml file to store your Gemini API Key.

```bash
nano src/configs/secrets.yaml
```

Then add your key and save.

```bash
GEMINI_API_KEY: "your-api-key-goes-here"
```

## 5. Running

Use this command to run.

```bash
python src/code/main.py -c src/configs/config.yaml src/configs/secrets.yaml
```

