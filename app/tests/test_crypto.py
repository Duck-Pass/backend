import pytest
from pytest_mock import mocker
from app.crypto import *

MOCK_MASTER_KEY = "k0KvWBh+i/abeV2emfvXf/xn+zKyHLyVbyJ6wBzS6lQ="
MOCK_SALT = "dCRMeUNqyS391itmSCclAw=="
MOCK_MASTER_KEY_RESULT = "ukjP00CxTYCFmXyQUmE/dWjQlntEXN/x/CLCl6631dg="


@pytest.mark.run(order=5)
def test_generate_master_key(mocker):
    salt_bytes = get_byte_from_base64(MOCK_SALT)
    master_key_bytes = get_byte_from_base64(MOCK_MASTER_KEY_RESULT)
    mocker.patch('app.crypto.gen_salt', return_value=salt_bytes)
    assert generate_master_key_hash(get_byte_from_base64(MOCK_MASTER_KEY)) == (salt_bytes, master_key_bytes)


@pytest.mark.run(order=6)
def test_verify_master_key_valid():
    assert verify_master_key_hash(get_byte_from_base64(MOCK_MASTER_KEY), get_byte_from_base64(MOCK_SALT), get_byte_from_base64(MOCK_MASTER_KEY_RESULT)) == True


@pytest.mark.run(order=7)
def test_verify_master_key_invalid():
    assert verify_master_key_hash(get_byte_from_base64(MOCK_MASTER_KEY), get_byte_from_base64(MOCK_SALT), b"") == False
