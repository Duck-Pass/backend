from typing import Callable
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from .auth import *

conf = ConnectionConfig(
    MAIL_USERNAME = os.environ.get('EMAIL_USERNAME'),
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD'),
    MAIL_FROM = os.environ.get('EMAIL_FROM'),
    MAIL_PORT = int(os.environ.get('EMAIL_PORT')),
    MAIL_SERVER = os.environ.get('EMAIL_HOST'),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)

async def send_email(mail: str, mailTemplate: Callable[[str], tuple]):

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createAccessToken(
        data={"sub": mail}, expires_delta=access_token_expires
    )

    subject, template = mailTemplate(access_token)

    message = MessageSchema(
        subject=subject,
        recipients=[mail],  # List of recipients, as many as you can pass
        body=template,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)