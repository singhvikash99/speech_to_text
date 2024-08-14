import numpy as np
import librosa
import scipy.io.wavfile as wav
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import os

class AudioProcessor:
    def __init__(self, n_mfcc=13, distance_threshold=9747):
        self.n_mfcc = n_mfcc
        self.distance_threshold = distance_threshold

    def calculate_distance(self, conv_segment_features, ref_segment_features):
        try:
            dist, _ = fastdtw(
                conv_segment_features.T, ref_segment_features.T, dist=euclidean
            )
            return dist
        except Exception as e:
            print(f"Error calculating distance: {e}")
            raise

    def extract_person(self, conversation_file, reference_file, output_file):
        try:
            if not os.path.exists(conversation_file):
                print(f"Conversation file does not exist: {conversation_file}")
                return None
            if not os.path.exists(reference_file):
                print(f"Reference file does not exist: {reference_file}")
                return None
            conversation, sr_conv = librosa.load(conversation_file, sr=None)
            reference, sr_ref = librosa.load(reference_file, sr=None)
        except Exception as e:
            print(f"Error loading audio files: {e}")
            return None

        if sr_conv != sr_ref:
            print("Sample rates of the conversation and reference files do not match.")
            return None

        segment_length_sec = 1
        segment_length_samples = int(segment_length_sec * sr_conv)
        hop_length_samples = int(segment_length_samples / 4)

        try:
            num_ref_segments = (
                len(reference) - segment_length_samples
            ) // hop_length_samples + 1
            reference_segments = [
                reference[
                    i * hop_length_samples : i * hop_length_samples + segment_length_samples
                ]
                for i in range(num_ref_segments)
            ]
        except Exception as e:
            print(f"Error creating reference segments: {e}")
            return None

        reference_segments_features = []
        for ref_seg in reference_segments:
            try:
                ref_mfcc = librosa.feature.mfcc(y=ref_seg, sr=sr_ref, n_mfcc=self.n_mfcc)
                ref_delta = librosa.feature.delta(ref_mfcc)
                ref_delta_delta = librosa.feature.delta(ref_delta)
                ref_features = np.vstack((ref_mfcc, ref_delta, ref_delta_delta))
                reference_segments_features.append(ref_features)
            except Exception as e:
                print(f"Error extracting features from reference segment: {e}")
                return None

        try:
            num_conv_segments = (
                len(conversation) - segment_length_samples
            ) // hop_length_samples + 1
            conversation_segments = [
                conversation[
                    i * hop_length_samples : i * hop_length_samples + segment_length_samples
                ]
                for i in range(num_conv_segments)
            ]
        except Exception as e:
            print(f"Error creating conversation segments: {e}")
            return None

        conversation_segments_features = []
        for conv_seg in conversation_segments:
            try:
                conv_mfcc = librosa.feature.mfcc(y=conv_seg, sr=sr_conv, n_mfcc=self.n_mfcc)
                conv_delta = librosa.feature.delta(conv_mfcc)
                conv_delta_delta = librosa.feature.delta(conv_delta)
                conv_features = np.vstack((conv_mfcc, conv_delta, conv_delta_delta))
                conversation_segments_features.append(conv_features)
            except Exception as e:
                print(f"Error extracting features from conversation segment: {e}")
                return None

        extracted_segments = []
        matched_indices = set()

        for i, conv_features in enumerate(conversation_segments_features):
            try:
                distances = [
                    self.calculate_distance(conv_features, ref_features)
                    for ref_features in reference_segments_features
                ]
                min_dist = min(distances)
                if min_dist < self.distance_threshold:
                    if i not in matched_indices:
                        extracted_segments.append(conversation_segments[i])
                        matched_indices.update(
                            range(i, i + (segment_length_samples // hop_length_samples))
                        )
                else:
                    print(
                        f"Conversation segment {i + 1} did not match the reference. Minimum distance was {min_dist}."
                    )
            except Exception as e:
                print(f"Error processing conversation segment {i + 1}: {e}")
                return None

        if extracted_segments:
            try:
                extracted_audio = np.hstack(extracted_segments)
                wav.write(output_file, sr_conv, (extracted_audio * 32767).astype(np.int16))
                return output_file
            except Exception as e:
                print(f"Error writing output file: {e}")
                return None
        else:
            print("No segments matched the reference.")
            return None
