from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from .auth import *

conf = ConnectionConfig(
    MAIL_USERNAME = os.environ.get('EMAIL_USERNAME'),
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD'),
    MAIL_FROM = os.environ.get('EMAIL_FROM'),
    MAIL_PORT = os.environ.get('EMAIL_PORT'),
    MAIL_SERVER = os.environ.get('EMAIL_HOST'),
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)

async def send_email(email : list, instance: User):

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createAccessToken(
        data={"sub": instance.email}, expires_delta=access_token_expires
    )

    template = f"""
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
            <div style=" display: flex; align-items: center; justify-content: center; flex-direction: column;">
                <h3> Account Verification </h3>
                <br>
                <p>Thanks for choosing EasyShopas, please 
                click on the link below to verify your account</p> 

                <a style="margin-top:1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #0275d8; color: white;"
                 href="http://localhost:8000/verification/?token={access_token}">
                    Verify your email
                <a>

                <p style="margin-top:1rem;">If you did not register for EasyShopas, 
                please kindly ignore this email and nothing will happen. Thanks<p>
            </div>
        </body>
        </html>
    """

    message = MessageSchema(
        subject="DuckPass Account Verification Mail",
        recipients=email,  # List of recipients, as many as you can pass
        body=template,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)