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

## 2. Environment Setup

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
## 3. Configuration

Before running the pipeline, you must provide it with your specific settings, paths, and your Gemini API key.

Create a file called config.yaml in the configs folder.
Here is the template you should use for the config yaml file.

```bash
# **Directory Paths**
INPUT_VIDEO: "/absolute/path/to/your/video.mov"
OUTPUTS_DIR: "/absolute/path/to/your/output/folder"
# Valid Inputs: Absolute paths to your video file and output directory.
# MUST be absolute paths (e.g., "/home/user/videos/input.mov").

# **Pipeline Settings:**
AUDIO_MODE: "filtered"                                 # Valid Inputs: "raw", "filtered"
RUN_DENOISE: true                                      # Valid Inputs: true or false

# **Audio Filtering Settings (Applied via FFmpeg)**
AUDIO_SAMPLE_RATE: 48000                               # Valid Inputs: Any positive integer (e.g., 16000, 44100, 48000).
AUDIO_CHANNEL: "right"                                 # Valid Inputs: "left", "right", or "mix"
HIGHPASS_FREQUENCY: 100                                # Valid Range: 1 to 20000 (Hz). 
LOUDNESS_TARGET_I: -16                                 # Valid Range: -70.0 to -5.0 (LUFS). 
LOUDNESS_TARGET_TP: -1.5                               # Valid Range: -9.0 to 0.0 (dBTP). 
LOUDNESS_TARGET_LRA: 11                                # Valid Range: 1.0 to 50.0 (LU).

# **Noise Reduction Settings (Applied via noisereduce)**
DENOISE_STATIONARY: true                               # Valid Inputs: true or false
DENOISE_PROP_DECREASE: 0.8                             # Valid Range: 0.0 to 1.0 (Float).

# **Transcription Settings.**
TRANSCRIPTION_ENGINE: "parakeet"                       # Valid Inputs: "parakeet" (More to come, only have parakeet implementation right now)
PARAKEET_MODEL: "nemo-parakeet-tdt-0.6b-v3"

# **Analysis settings**
GEMINI_MODEL: "gemini-3.5-flash-lite"                  # Valid Inputs: Any valid Gemini model string (e.g., "gemini-1.5-pro", "gemini-3.5-flash-lite")
PROMPT_NAME: "prompt1.txt"                             # Valid Inputs: The name of a .txt file located inside the `src/prompts/` directory.
MACHINE_STATES: "Roping, Flaring, Transition, Blocked" # Valid Inputs: A comma-separated string of the machine states you want the AI to look for.
```

Next create a secrets.yaml file to store your Gemini API Key.

```bash
nano src/configs/secrets.yaml
```

Then add your key and save.

```bash
GEMINI_API_KEY: "your-api-key-goes-here"
```

## 4. Running

Use this command to run.

```bash
python src/code/main.py -c src/configs/config.yaml src/configs/secrets.yaml
```

