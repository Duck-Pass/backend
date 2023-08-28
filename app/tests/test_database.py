from app.database import *


def test_db_connection():
    with db_cursor() as cur:
        assert cur is not None


def test_query_execution():
    with db_cursor() as cur:
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result == (1,)
