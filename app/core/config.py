import os
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv("DATABASE_URL")

secret_key = os.getenv("JWT_SECRET_KEY")
algorithm = "HS256"
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))




# Email
smtp_host     = os.getenv("SMTP_HOST", "smtp.gmail.com")
smtp_port     = int(os.getenv("SMTP_PORT", 587))
smtp_user     = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMTP_PASSWORD")
