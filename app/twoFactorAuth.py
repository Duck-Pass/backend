import pyotp


def generate_secret():
    """
    Generates a random secret that the user will use as authenticator key
    :return: Random secret
    """

    return pyotp.random_base32()


def verify_code(secret, code):
    """
    Verifies the given code corresponds to the given secret
    :param str secret: Authenticator key of the user
    :param str code: Given 6-digits code
    :return: True if the code is valid, False otherwise
    """

    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_qrcode_url(secret, email):
    """
    Generates a QR code URL containing all the information needed to add the account to the authenticator app
    :param str secret: Authenticator key of the user
    :param str email: Email of the user
    :return: URL of the QR code
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="duckpass.ch", image="https://i.imgur.com/Xpk0PiT.png")
