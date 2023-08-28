from app.auth import *


def test_token_generation():

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createAccessToken(
        data={"sub": "Test"}, expires_delta=access_token_expires
    )

    if not access_token:
        assert False

    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "Test"
