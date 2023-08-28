import os
import psycopg2.pool
from urllib import parse
from contextlib import contextmanager

database_url = os.environ['DATABASE_URL']           # Database URL for connection

# Parsing database URL
parse_result = parse.urlparse(database_url)
dbname = parse_result.path[1:]
user = parse_result.username
password = parse_result.password
host = parse_result.hostname
port = parse_result.port

# Creating database pool
dbpool = psycopg2.pool.ThreadedConnectionPool(dbname=dbname,
                                              user=user,
                                              password=password,
                                              host=host,
                                              port=port,
                                              minconn=1,
                                              maxconn=20)


"""
    Create and manage database access
"""
@contextmanager
def db_cursor():
    conn = dbpool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
            conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        dbpool.putconn(conn)
