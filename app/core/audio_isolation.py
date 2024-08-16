import torchaudio
from speechbrain.inference.speaker import EncoderClassifier, SpeakerRecognition
import os
import torch
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, model_source="speechbrain/spkrec-ecapa-voxceleb", segment_size=3):
        self.segment_size = segment_size
        self.embedding_model = EncoderClassifier.from_hparams(source=model_source)
        self.verification_model = SpeakerRecognition.from_hparams(source=model_source, savedir="pretrained_models/spkrec-ecapa-voxceleb")

    def extract_person(self, conversation_path, sample_path, output_path):
        try:
            signal, fs = torchaudio.load(conversation_path)
            num_segments = int(signal.shape[1] / (self.segment_size * fs)) + 1

            matched_segments = []

            for i in range(num_segments):
                start = i * self.segment_size * fs
                end = min((i + 1) * self.segment_size * fs, signal.shape[1])
                segment = signal[:, int(start):int(end)]
                
                segment_path = f"segment_{i}.wav"
                torchaudio.save(segment_path, segment, fs)
                
                try:
                    score, prediction = self.verification_model.verify_files(sample_path, segment_path)
                    
                    if prediction == 1:
                        logger.info(f"Segment {i} matches the speaker ({sample_path}) with score {score}")
                        matched_segments.append(segment)
                    else:
                        logger.info(f"Segment {i} does not match the speaker ({sample_path})")
                finally:
                    if os.path.exists(segment_path):
                        os.remove(segment_path)

            if matched_segments:
                combined_segments = torch.cat(matched_segments, dim=1)
                torchaudio.save(output_path, combined_segments, fs)
                logger.info(f"Matched speaker's audio saved to {output_path}")
            else:
                raise ValueError("No segments matched the provided speaker sample.")

            return output_path

        except Exception as e:
            logger.error(f"Error in extracting speaker: {str(e)}")
            raise e
