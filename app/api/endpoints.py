from fastapi import APIRouter, File, UploadFile, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import os
import uuid
from dotenv import load_dotenv
from app.core.audio_processor import AudioProcessor
from app.core.transcriber import WhisperTranscriber
from app.utils.result_email import send_email
from app.core.tasks import process_and_transcribe

load_dotenv()

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

os.makedirs("temp", exist_ok=True)


@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def generate_unique_filename(original_filename: str) -> str:
    unique_id = str(uuid.uuid4())
    file_extension = os.path.splitext(original_filename)[1]
    return f"{unique_id}{file_extension}"


# @router.post("/upload/")
# async def upload_files(
#     conversation: UploadFile = File(...),
#     sample: UploadFile = File(...),
#     email: str = Form(...),
# ):
#     conversation_path = f"temp/{generate_unique_filename(conversation.filename)}"
#     sample_path = f"temp/{generate_unique_filename(sample.filename)}"
#     output_path = f"temp/{generate_unique_filename('output.wav')}"
#     transcription_path = f"temp/{generate_unique_filename('transcribe.txt')}"

#     with open(conversation_path, "wb") as f:
#         f.write(await conversation.read())

#     with open(sample_path, "wb") as f:
#         f.write(await sample.read())

#     try:
#         output_file_path = AudioProcessor().extract_person(
#             conversation_path, sample_path, output_path
#         )
#     except Exception as e:
#         return JSONResponse(
#             content={"message": f"Error occurred during audio processing: {str(e)}"},
#             status_code=500,
#         )

#     try:
#         transcriber = WhisperTranscriber()
#         transcriber.transcribe(output_file_path, transcription_path)
#     except Exception as e:
#         return JSONResponse(
#             content={"message": f"Error occurred during transcription: {str(e)}"},
#             status_code=500,
#         )

#     try:
#         send_email(to_email=email, transcription_path=transcription_path)
#     except Exception as e:
#         return JSONResponse(
#             content={"message": f"Error occurred during email sending: {str(e)}"},
#             status_code=500,
#         )

#     try:
#         if os.path.exists(conversation_path):
#             os.remove(conversation_path)
#         if os.path.exists(sample_path):
#             os.remove(sample_path)
#         if os.path.exists(output_file_path):
#             os.remove(output_file_path)
#         if os.path.exists(transcription_path):
#             os.remove(transcription_path)

#     except Exception as e:
#         return JSONResponse(
#             content={"message": f"Error occurred during cleanup: {str(e)}"},
#             status_code=500,
#         )

#     return JSONResponse(
#         content={
#             "message": "Processing, transcription, and email sending complete. You will receive an email with the transcription attached."
#         }
#     )


@router.post("/upload/")
async def upload_files(
    conversation: UploadFile = File(...),
    sample: UploadFile = File(...),
    email: str = Form(...),
):
    conversation_path = f"temp/{generate_unique_filename(conversation.filename)}"
    sample_path = f"temp/{generate_unique_filename(sample.filename)}"
    output_path = f"temp/{generate_unique_filename('output.wav')}"
    transcription_path = f"temp/{generate_unique_filename('transcribe.txt')}"

    with open(conversation_path, "wb") as f:
        f.write(await conversation.read())

    with open(sample_path, "wb") as f:
        f.write(await sample.read())

    process_and_transcribe.delay(
        conversation_path, 
        sample_path, 
        output_path, 
        transcription_path, 
        email
    )

    return JSONResponse(
        content={
            "message": "Processing started. You will receive an email with the transcription attached once the processing is complete."
        }
    )