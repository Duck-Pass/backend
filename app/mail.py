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

async def send_email(mail: str):

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createAccessToken(
        data={"sub": mail}, expires_delta=access_token_expires
    )

    template = f"""
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
            <div style="display: flex; align-items: center; justify-content: center; flex-direction: column; background-color: #f8f8f8; padding: 2rem;">
                <img src="https://i.imgur.com/Xpk0PiT.png" alt="DuckPass Logo" style="width: 150px; height: auto; margin-bottom: 1rem;">
                <h3 style="color: #333;"> Quack your way into seamless security with DuckPass </h3>
                <br>
                <p style="color: #555;">Thanks for choosing DuckPass! Click on the link below to verify your account:</p>

                <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #022837; color: white;" href="http://staging.duckpass.ch/verify/?token={access_token}">
                    Verify your email
                <a>

                <p style="margin-top: 1rem; color: #555;">If you didn't sign up for DuckPass, please kindly ignore this email – nothing will happen. Thanks<p>
            </div>
        </body>
        </html>
    """

    message = MessageSchema(
        subject="DuckPass Account Verification Mail",
        recipients=[mail],  # List of recipients, as many as you can pass
        body=template,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)