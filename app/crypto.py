from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from base64 import b64decode
from binascii import Error as BinasciiError


PBKDF_NUM_ITERATIONS = 600_000
SALT_LEN = 16


def gen_salt(length: int) -> bytes:
    return get_random_bytes(length)


def pbkdf2_sha256(data: bytes, salt: bytes, iterations: int) -> bytes:
    h = PBKDF2(data, salt, 32, count=iterations, hmac_hash_module=SHA256)
    return h


def generate_master_key_hash(master_password_hash: bytes) -> tuple[bytes, bytes]:
    salt = gen_salt(SALT_LEN)
    h = pbkdf2_sha256(master_password_hash, salt, PBKDF_NUM_ITERATIONS)
    return salt, h


def verify_master_key_hash(received_hash: bytes, salt: bytes, current_master_key_hash: bytes) -> bool:
    h = pbkdf2_sha256(received_hash, salt, PBKDF_NUM_ITERATIONS)
    return h == current_master_key_hash


def get_byte_from_base64(s: str) -> bytes:
    try:
        decoded_bytes = b64decode(s)
        return decoded_bytes
    except BinasciiError:
        print("error while decoding string")
        return b""
