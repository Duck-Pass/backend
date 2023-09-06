import pytest
import requests


@pytest.mark.run(order=14)
def test_get_breaches_with_a_good_email_without_breaches():
    """
    Function to test the get breaches endpoint
    Note : We will only test this endpoint due to rate limiting by the HIBP API
    """

    url = f"{pytest.API}/hibp_breaches"

    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.run(order=15)
def test_get_breaches_without_email():
    """
    Function to test the get breaches endpoint without a valid email
    """

    url = f"{pytest.API}/hibp_pastes"

    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json",
    }

    response = requests.get(url, headers=headers)

    assert response.status_code == 404
