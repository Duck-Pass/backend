from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from base64 import b64decode
from binascii import Error as BinasciiError

PBKDF_NUM_ITERATIONS = 600_000
SALT_LEN = 16


def gen_salt(length: int) -> bytes:
    """
    Generates a random salt of the given length
    :param int length: length of the salt
    :return: Salt of the given length in bytes
    """

    return get_random_bytes(length)


def pbkdf2_sha256(data: bytes, salt: bytes, iterations: int) -> bytes:
    """
    Generates a PBKDF2 hash of the given data
    :param bytes data: Data to hash
    :param bytes salt: Salt used in PBKDF2
    :param int iterations: Iterations of the algorithm
    :return: Hash of the given data
    """

    h = PBKDF2(data, salt, 32, count=iterations, hmac_hash_module=SHA256)
    return h


def generate_master_key_hash(master_password_hash: bytes) -> tuple[bytes, bytes]:
    """
    Generates a salt and a hash of the given master password hash (derivation)
    :param bytes master_password_hash: Hash of the master password
    :return: Tuple of salt and hash of the master password hash
    """

    salt = gen_salt(SALT_LEN)
    h = pbkdf2_sha256(master_password_hash, salt, PBKDF_NUM_ITERATIONS)
    return salt, h


def verify_master_key_hash(received_hash: bytes, salt: bytes, current_master_key_hash: bytes) -> bool:
    """
    Verifies the given hash processed with the given salt corresponds to the current master key hash
    :param bytes received_hash: Hash received from the client
    :param bytes salt: Salt used to generate the master key hash
    :param bytes current_master_key_hash: Master key hash to compare with
    :return: True if the hashes match, False otherwise
    """

    h = pbkdf2_sha256(received_hash, salt, PBKDF_NUM_ITERATIONS)
    return h == current_master_key_hash


def get_byte_from_base64(s: str) -> bytes:
    """
    Decodes a base64 string to bytes
    :param str s: Base64 string to decode
    :return: Decoded bytes
    """

    try:
        decoded_bytes = b64decode(s)
        return decoded_bytes
    except BinasciiError:
        print("error while decoding string")
        return b""
