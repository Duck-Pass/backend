import pyotp


def generateSecret():
    return pyotp.random_base32()


def verifyCode(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
