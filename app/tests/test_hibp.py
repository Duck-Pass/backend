import pytest
import requests


@pytest.mark.run(order=14)
def test_get_breaches():
    """
    Function to test the get breaches endpoint
    """

    url = f"{pytest.API}/hibp_breaches"

    query_params = {
        "email": "test@duckpass.ch",
        "domain": "duckpass.ch"
    }

    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json",
    }

    response = requests.get(url, params=query_params, headers=headers)
    assert response.status_code == 200


@pytest.mark.run(order=15)
def test_get_breaches_without_email():
    """
    Function to test the get breaches endpoint without a valid email
    """

    url = f"{pytest.API}/hibp_pastes"

    query_params = {
        "email": "DUCKY",
        "domain": "duckpass.ch"
    }

    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json",
    }

    response = requests.get(url, params=query_params, headers=headers)

    print(response.text)

    assert response.status_code == 404

