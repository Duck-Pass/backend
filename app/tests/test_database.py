import pytest
from app.database import *
from app.utils import byteaToText


def test_db_connection():
    with db_cursor() as cur:
        assert cur is not None


def test_query_execution():
    with db_cursor() as cur:
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result == (1,)


def test_create_user():
    insertUpdateDeleteRequest(insertUser(), ("test", "testMail@duckpass.ch", "testPassword", "testSymmetricKey", "testTwoFactorAuth", "testVault"))
    user = selectRequest(selectUser(), ("testMail@duckpass.ch",))[1:]
    user = user[:-1] + (byteaToText(user[-1]),)
    assert user == ("test", "testMail@duckpass.ch", "testPassword", "testSymmetricKey", "testTwoFactorAuth", "testVault")


@pytest.mark.dependency(depends=["test_create_user"])
def test_delete_user():
    insertUpdateDeleteRequest(deleteUser(), ("testMail@duckpass.ch",))
    user = selectRequest(selectUser(), ("testMail@duckpass.ch",))
    assert user is None