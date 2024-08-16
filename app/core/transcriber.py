import whisperx
import os

class WhisperTranscriber:
    def __init__(self, model_size="medium", device="cpu", model_download_path="./model"):
        print(f"Initializing WhisperTranscriber with model size '{model_size}' on device '{device}'")
        
        if not os.path.exists(model_download_path):
            print(f"Creating directory for model at: {model_download_path}")
            os.makedirs(model_download_path)
        
        print(f"Downloading model to: {model_download_path}")
        self.model = whisperx.load_model(
            model_size, device=device, compute_type="float32", download_root=model_download_path
        )
        
        print("Model loaded successfully")

    def transcribe(self, audio_path, output_path="transcribe.txt"):
        print(f"Loading audio from {audio_path}")
        audio = whisperx.load_audio(audio_path)
        
        print("Transcribing audio...")
        result = self.model.transcribe(audio)
        
        print(f"Saving transcription to {output_path}")
        with open(output_path, "w") as f:
            for segment in result["segments"]:
                f.write(segment["text"] + "\n")

<<<<<<< HEAD
        print(f"Transcription saved to {output_path}")
=======
        print(f"Transcription saved successfully to {output_path}")
>>>>>>> origin/master
