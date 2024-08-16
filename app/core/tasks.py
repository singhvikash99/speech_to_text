from celery import Celery
from app.core.celery import app
from app.utils.result_email import send_email
# from app.core.audio_processor import AudioProcessor #librosa mfcc
from app.core.audio_isolation import AudioProcessor #speechbrain
from app.core.transcriber import WhisperTranscriber
import logging
import os

celery = app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task
def process_and_transcribe(conversation_path, sample_path, output_path, transcription_path, email):
    try:
        try:
            output_file_path = AudioProcessor().extract_person(
                conversation_path, sample_path, output_path
            )
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            os.remove(conversation_path)
            os.remove(sample_path)
            raise e
        
        try:
            transcriber = WhisperTranscriber()
            transcriber.transcribe(output_file_path, transcription_path)
        except Exception as e:
            logger.error(f"Error occurred intra: {str(e)}")
            os.remove(conversation_path)
            os.remove(sample_path)
            os.remove(output_file_path)
            raise e

        try:
            print(transcription_path)
            send_email(to_email=email, transcription_path=transcription_path)
        except Exception as e:
            logger.error(f"Error occurred intra: {str(e)}")
            os.remove(conversation_path)
            os.remove(sample_path)
            os.remove(output_file_path)
            os.remove(transcription_path)
            raise e
        
        os.remove(conversation_path)
        os.remove(sample_path)
        os.remove(output_file_path)
        os.remove(transcription_path)
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        os.remove(conversation_path)
        os.remove(sample_path)
        os.remove(output_file_path)
        os.remove(transcription_path)
        raise e