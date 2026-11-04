Here is a pipeline I made that takes a Iphone (.mov) file, filters the audio, transcribes it, and returns a structured analysis of what happens at each timestamps.

This was applied to hydrocylone videos and can return in the analysis what state the machine is in at during a certain time period (based on speech in the video).

Setting up config.yaml:

**These can be true or false, they are for you to choose what stage of the pipeline you want to run**
RUN_AUDIO_EXTRACTION:  
RUN_TRANSCRIPTION: 
RUN_STATE_ANALYSIS:
RUN_DENOISE:

**This is where you choose the transcription model you want to use and where it should be saved to.
The engine decided if it will use parakeet or whisper, and then based on that it chooses the relevant model for transcription.**
**NOTE: Whisper implementation is broken so still to parakeet for now.**
TRANSCRIPTION_ENGINE: "parakeet"
WHISPER_MODEL: "model-name"
WHISPER_MODEL_DIR: # "model-dir"
PARAKEET_MODEL: "nemo-parakeet-tdt-0.6b-v3"

**This is the tag of the gemini model used for analysis at the end of the pipeline.**
**Can change this to any gemini model you want to use.**
GEMINI_MODEL: "gemini-3.5-flash-lite"

**These are settings that are applied to the raw audio to filter out some noise initially, relevant ranges are listed below.**
AUDIO_MODE: "filtered"
AUDIO_SAMPLE_RATE: 48000
AUDIO_CHANNEL: "right"
HIGHPASS_FREQUENCY: 100
LOUDNESS_TARGET_I: -16
LOUDNESS_TARGET_TP: -1.5
LOUDNESS_TARGET_LRA: 11

**Setting applied to the noise reduction model. (applied after filter).**
DENOISE_STATIONARY: true 
DENOISE_PROP_DECREASE: 0.8

**These need to be changed to suit your device.**
INPUT_VIDEO: "/media/jackwilliams/external_01_cyclone_data/Videos/IMG_5079.mov"
OUTPUTS_DIR: "/media/jackwilliams/external_01_cyclone_data/sing-data"

**You can choose a prompt from the prompts folder that will be fed to gemini for analysis.**
**You can adjust the list of relevant hydrocyclone states that will be used in the prompt.**
PROMPT_NAME: "prompt1.txt"
MACHINE_STATES: "Roping, Flaring, Transition, Blocked"
