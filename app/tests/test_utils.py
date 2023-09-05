import pytest

from ..utils import *


@pytest.mark.run(order=22)
def test_email_regex_valid():
    """
    Function to test the email_regex_valid function
    """

    assert is_valid_email("test@duckpass.ch")


@pytest.mark.run(order=23)
def test_email_regex_not_valid():
    """
    Function to test the email_regex_valid function when we don't give a valid email
    """

    assert not is_valid_email("ducky")


def test_bytea_to_text():
    """
    Test with a bytea value
    """
    bytea_value = b'Hello, World!'
    result = bytea_to_text(bytea_value)
    assert result == 'Hello, World!'


def test_empty_bytea_to_text():
    """
    Test with an empty bytea value
    """
    bytea_value = b''
    result = bytea_to_text(bytea_value)
    assert result == ''
