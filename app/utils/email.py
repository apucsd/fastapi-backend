from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

TEMPLATE_FOLDER_PATH = Path(__file__).parent.parent / 'templates'



conf = ConnectionConfig(
    MAIL_USERNAME=SMTP_USER,
    MAIL_PASSWORD=SMTP_PASSWORD,
    MAIL_FROM=SMTP_USER,
    MAIL_PORT=SMTP_PORT,
    MAIL_SERVER=SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER_PATH

    
)

fm = FastMail(conf)

async def send_email(to:str, subject:str, template_name:str, **context):
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        template_body=context,
        subtype=MessageType.html
    )

    await fm.send_message(message, template_name=template_name)

   
    