from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import smtp_host, smtp_port, smtp_user, smtp_password

TEMPLATE_FOLDER_PATH = Path(__file__).parent.parent / 'templates'



conf = ConnectionConfig(
    MAIL_USERNAME=smtp_user,
    MAIL_PASSWORD=smtp_password,
    MAIL_FROM=smtp_user,
    MAIL_PORT=smtp_port,
    MAIL_SERVER=smtp_host,
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

   
    