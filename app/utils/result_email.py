import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, transcription_path):
    from_email = os.getenv("EMAIL_USER")
    from_password = os.getenv("EMAIL_PASSWORD") 
    subject = "Transcription Result"
    body = "Please find your transcription attached."

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if transcription_path:
        try:
            with open(transcription_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(transcription_path)}",
                )
                msg.attach(part)
        except Exception as e:
            print(f"Error attaching file: {str(e)}")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, from_password)
            server.send_message(msg)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")