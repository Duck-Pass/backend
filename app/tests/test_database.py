import pytest
from app.database import *


@pytest.mark.run(order=1)
def test_db_connection():
    with db_cursor() as cur:
        assert cur is not None


@pytest.mark.run(order=2)
def test_query_execution():
    with db_cursor() as cur:
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result == (1,)


@pytest.mark.run(order=3)
def test_create_user():
    insert_update_delete_request(insert_user(), ("testMail@duckpass.ch", "testPassword", "testSymmetricKey", "Salt"))
    user = select_request(select_user(), ("testMail@duckpass.ch",))[1:]
    assert user == ("testMail@duckpass.ch", "testPassword", "testSymmetricKey", "Salt", False, "0", False, None)


@pytest.mark.run(order=4)
def test_delete_user():
    insert_update_delete_request(delete_user(), ("testMail@duckpass.ch",))
    user = select_request(select_user(), ("testMail@duckpass.ch",))
    assert user is None