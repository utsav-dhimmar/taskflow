from typing import List

from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    NameEmail,
)
from pydantic import BaseModel

from app.core.config import setting


class EmailSchema(BaseModel):
    email: List[NameEmail]


conf = ConnectionConfig(
    MAIL_USERNAME=setting.MAIL_USERNAME,
    MAIL_PASSWORD=setting.MAIL_PASSWORD,
    MAIL_FROM=setting.MAIL_FROM,
    MAIL_PORT=setting.MAIL_PORT,
    MAIL_SERVER=setting.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
    VALIDATE_CERTS=False,
)

mail = FastMail(config=conf)


async def send_email(recipient: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype=MessageType.html,
    )

    try:
        await mail.send_message(message)
        print("mail send successfully")
        return True
    except Exception as e:
        print("*" * 20)
        print("mail send failed ")

        print(e)
        print("*" * 20)
        return False
