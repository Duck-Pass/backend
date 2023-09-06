import pytest
import json
import requests
import random
import string
from app.auth import *
from app.model import UserAuth

# Token used by the test user
pytest.token = None

# User's data used below to test user's endpoints
MOCK_USER = UserAuth(
    email="test@duckpass.ch",
    key_hash="k0KvWBh+i/abeV2emfvXf/xn+zKyHLyVbyJ6wBzS6lQ=",
    key_hash_conf="k0KvWBh+i/abeV2emfvXf/xn+zKyHLyVbyJ6wBzS6lQ=",
    symmetric_key_encrypted="RMn8mQK4UonHn7fJtEO7PA==|5ELbhR1wNRO/B8buvyaTrGjRxwOFgplgSzGYnFPrJp/hkJF8tx8Ok72NiJLKmlnpMEakDWYUWXjukJ0H2dJw27bE/CvGRgXQoy+aIDWU3Ys=|Iv5wltHAR6OWqwgQPYfzicolBB7zZlZyw5g+pT2WuXM="
)
MOCK_USER2 = UserAuth(
    email="ducky@duckpass.ch",
    key_hash="oow+8a+orG/2kAjT0BtuAwfEC3fZ3ngyf+2/hmH8xAs=",
    key_hash_conf="oow+8a+orG/2kAjT0BtuAwfEC3fZ3ngyf+2/hmH8xAs=",
    symmetric_key_encrypted="aOZs9oeut12RsmlvbIrSRw==|ye3ZZ73DbOjvX00Al3OTPYRqqNvhLaP9Wq5dFtfI01Yyzhq0zI9KzEDfZ9lygnlPgkX5JkwMsMSulB7DCNSOgmUy3F9uNrcsVOJFKdqZ//Y=|gnixW1eVwBOJUH/hHYAOE/02YTjE3Qty2DylmDGeRKk="
)

pytest.API = "https://api-staging.duckpass.ch"


def login(username, password):
    """
    Function to log in a user
    :param username: Username used for the login
    :param password: Password used for the login
    :return: Status code of the response
    """
    url = f"{pytest.API}/token"

    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        pytest.token = response_data.get('access_token')
    return response.status_code


def get_user(token):
    """
    Function to get the user's data
    :param token: Token used to authenticate the user
    :return: Status code of the response
    """
    url = f"{pytest.API}/get_user"

    headers = {
        "Authorization": "Bearer " + token,
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    return response.status_code


@pytest.mark.run(order=8)
def test_api_register():
    """
    Function to test the register endpoint with a new user
    """

    url = f"{pytest.API}/register"

    data = {
        "email": MOCK_USER.email,
        "key_hash": MOCK_USER.key_hash,
        "key_hash_conf": MOCK_USER.key_hash_conf,
        "symmetric_key_encrypted": MOCK_USER.symmetric_key_encrypted
    }

    json_data = json.dumps(data)

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, data=json_data, headers=headers)
    insert_update_delete_request(update_verification(), (MOCK_USER.email,))
    assert response.status_code == 200


@pytest.mark.run(order=9)
def test_api_register_an_existing_user():
    """
    Function to test the register endpoint with an existing user
    """

    url = f"{pytest.API}/register"

    data = {
        "email": MOCK_USER.email,
        "key_hash": MOCK_USER.key_hash,
        "key_hash_conf": MOCK_USER.key_hash_conf,
        "symmetric_key_encrypted": MOCK_USER.symmetric_key_encrypted
    }

    json_data = json.dumps(data)

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, data=json_data, headers=headers)
    assert response.status_code == 400


@pytest.mark.run(order=10)
def test_api_login():
    """
    Function to test the login endpoint with an existing user
    """
    assert login(MOCK_USER.email, MOCK_USER.key_hash) == 200


@pytest.mark.run(order=11)
def test_api_login_with_bad_credentials():
    """
    Function to test the login endpoint with bad credentials
    """
    assert login(MOCK_USER2.email, MOCK_USER2.key_hash) == 404


@pytest.mark.run(order=12)
def test_get_user():
    """
    Function to test the get_user endpoint with a valid token
    """
    assert get_user(pytest.token) == 200


@pytest.mark.run(order=13)
def test_get_user_non_existing():
    """
    Function to test the get_user endpoint with a random token
    Note that this is the only function tested with bad token, because all the other functions that take a token as
    parameter are also filtered by the same function as they are entering the API.
    """
    assert get_user(''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(len(pytest.token)))) == 401


@pytest.mark.run(order=17)
def test_update_vault():
    """
    Function to test the update_vault endpoint
    """
    url = f"{pytest.API}/update_vault"


    data = {
        "vault": "aPpdFOam5Yo2NoEp7Z8Hsg==|OcEdoQTDcrE04alkeyZwZ3WoX39NRWIhREzHQlIFXb5voh5U782iKlLo4QuP6MwCzCnCsT/Pllo3LjTIIkqXJhsMyAe39hGqSaeVw+Bml/EUOZY38YdeRMTDU7H7pD8708by+xJTtXMQP6qywVgMGnF4qQ/bX6NMu6hBxa1spXyYvGW0LDA6yvTksVgER/ilKvZjsGfi4ciJVPPacFWh2A==|dc0mLRrLbOp9Bdy0HViQx35S+NUXz34PdzR54F03hyQ=",
    }

    json_data = json.dumps(data)

    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json"
    }

    response = requests.put(url, data=json_data, headers=headers)
    assert response.status_code == 200


@pytest.mark.run(order=18)
def test_update_email():
    """
    Function to test the update_email endpoint
    """

    url = f"{pytest.API}/update_email"

    data = {
        "user_auth": {
            "email": MOCK_USER2.email,
            "key_hash": MOCK_USER2.key_hash,
            "key_hash_conf": MOCK_USER2.key_hash_conf,
            "symmetric_key_encrypted": MOCK_USER2.symmetric_key_encrypted
        },
        "vault": {
            "vault": ""
        }
    }

    json_data = json.dumps(data)

    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json"
    }

    response = requests.put(url, data=json_data, headers=headers)
    assert response.status_code == 200
    assert login(MOCK_USER2.email, MOCK_USER2.key_hash) == 200


@pytest.mark.run(order=19)
def test_update_password():
    """
    Function to test the update_password endpoint
    """

    url = f"{pytest.API}/update_password"

    data = {
        "user_auth": {
            "email": MOCK_USER2.email,
            "key_hash": MOCK_USER.key_hash,
            "key_hash_conf": MOCK_USER.key_hash_conf,
            "symmetric_key_encrypted": MOCK_USER.symmetric_key_encrypted
        },
        "vault": {
            "vault": ""
        }
    }

    json_data = json.dumps(data)

    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json"
    }

    response = requests.put(url, data=json_data, headers=headers)
    assert response.status_code == 200


# test logout
@pytest.mark.run(order=20)
def test_logout():
    """
    Function to test the logout endpoint
    """

    url = f"{pytest.API}/logout"
    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json"
    }

    response = requests.post(url, headers=headers)
    assert response.status_code == 200
    assert get_user(pytest.token) == 401
    assert login(MOCK_USER2.email, MOCK_USER.key_hash) == 200


@pytest.mark.run(order=21)
def test_delete_user():
    """
    Function to test the delete_user endpoint
    """

    url = f"{pytest.API}/delete_account"
    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json"
    }

    response = requests.delete(url, headers=headers)
    assert response.status_code == 200

