import pytest
import requests


@pytest.mark.run(order=16)
def test_auth_key_generation():
    """
    Function to test the auth_key_generation endpoint
    """

    url = f"{pytest.API}/generate_auth_key"

    headers = {
        "Authorization": "Bearer " + pytest.token,
        "accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 200
