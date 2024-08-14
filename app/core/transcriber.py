import whisperx


class WhisperTranscriber:
    def __init__(self, model_size="small", device="cpu"):
        # Ensure model is loaded with float32 computation
        self.model = whisperx.load_model(
            model_size, device=device, compute_type="float32"
        )

    def transcribe(self, audio_path, output_path="transcribe.txt"):
        audio = whisperx.load_audio(audio_path)
        result = self.model.transcribe(audio)

        with open(output_path, "w") as f:
            for segment in result["segments"]:
                f.write(segment["text"] + "\n")

        print(f"Transcription saved to {output_path}")
