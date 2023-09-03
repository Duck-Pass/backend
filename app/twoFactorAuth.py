import pyotp


def generate_secret():
    return pyotp.random_base32()


def verify_code(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_qrcode_url(secret, email):
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="duckpass.ch", image="https://i.imgur.com/Xpk0PiT.png")
