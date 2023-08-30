import os

SITE = os.environ.get('SITE')
API = os.environ.get('API')

def confirmationMail(token):

    return "DuckPass Account Verification", f"""
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
            <div style="display: flex; align-items: center; justify-content: center; flex-direction: column; background-color: #f8f8f8; padding: 2rem;">
                <img src="https://i.imgur.com/Xpk0PiT.png" alt="DuckPass Logo" style="width: 150px; height: auto; margin-bottom: 1rem;">
                <h3 style="color: #333;"> Quack your way into seamless security with DuckPass </h3>
                <br>
                <p style="color: #555;">Thanks for choosing DuckPass! Quack on the link below to verify your account:</p>

                <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #022837; color: white;" href="http://{API}/verify/?token={token}">
                    Verify your email
                <a>

                <p style="margin-top: 1rem; color: #555;">If you didn't sign up for DuckPass, please kindly ignore this email – nothing will happen. Thanks<p>
            </div>
        </body>
        </html>
    """

def resetPasswordMail(token):

    return "DuckPass Password Reset", f"""
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
            <div style="display: flex; align-items: center; justify-content: center; flex-direction: column; background-color: #f8f8f8; padding: 2rem;">
                <img src="https://i.imgur.com/Xpk0PiT.png" alt="DuckPass Logo" style="width: 150px; height: auto; margin-bottom: 1rem;">
                <h3 style="color: #333;"> Quack your way into seamless security with DuckPass </h3>
                <br>
                <p style="color: #555;">Forgot your password? No worries! Quack on the link below to reset it:</p>

                <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #022837; color: white;" href="https://{SITE}/#/reset/?token={token}">
                    Reset Password
                <a>

                <p style="margin-top: 1rem; color: #555;">If you didn't request a password reset, please kindly ignore this email – your password will remain unchanged. Thanks<p>
            </div>
        </body>
        </html>
    """
