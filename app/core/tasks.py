from celery import Celery
from app.core.celery import app
from app.utils.result_email import send_email
from app.core.audio_processor import AudioProcessor
from app.core.transcriber import WhisperTranscriber
import logging
import os

celery = app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task
def process_and_transcribe(conversation_path, sample_path, output_path, transcription_path, email):
    logger.info(f"Task started with paths: {type(conversation_path)}, {type(sample_path)}, {type(output_path)}, {type(transcription_path)}")
    try:
        try:
            audio_processor = AudioProcessor()
            output_file_path = audio_processor.extract_person(conversation_path, sample_path, output_path)
            if output_file_path is None:
                logger.error("Output file path is None.")
                return
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            raise e

        # Transcribe audio
        transcriber = WhisperTranscriber()
        transcriber.transcribe(output_file_path, transcription_path)
        print(f"Phase 2 done {transcription_path}")

        # Send email with transcription
        send_email(to_email=email, transcription_path=transcription_path)

        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise e