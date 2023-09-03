import os
import psycopg2.pool
from urllib import parse
from contextlib import contextmanager

database_url = os.environ['DATABASE_URL']  # Database URL for connection

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


@contextmanager
def db_cursor():
    """
        Create and manage database access
    """

    conn = dbpool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        dbpool.putconn(conn)


def create_database():
    """
        Execute database creation
    """
    with db_cursor() as cur:
        cur.execute(database())


def select_request(req, values):
    """
        Execute select requests
        @param req: str
        @param values: tuple
        @return select result
    """
    with db_cursor() as cur:
        cur.execute(req, values)
        return cur.fetchone()


def insert_update_delete_request(req, values):
    """
        Execute insert and update requests
        @param req: str
        @param values: tuple
    """
    with db_cursor() as cur:
        cur.execute(req, values)


def database():
    """
        Database request
    """

    return """
     DROP SCHEMA IF EXISTS duckpass CASCADE;
     CREATE SCHEMA duckpass;
    
     SET SEARCH_PATH TO duckpass;
    
     DROP TABLE IF EXISTS "User" CASCADE;
     CREATE TABLE "User"
     (
        userId                 SERIAL,
        email                  VARCHAR(256) UNIQUE,
        keyHash     VARCHAR(2048) NOT NULL,
        symmetricKeyEncrypted  VARCHAR(2048) NOT NULL,
        salt VARCHAR(2048) NOT NULL,
        hasTwoFactorAuth BOOLEAN DEFAULT FALSE,
        twoFactorAuth VARCHAR(2048) DEFAULT '0',
        verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        vault bytea,
        PRIMARY KEY (userId)
     );
    
    DROP TABLE IF EXISTS "RevokedToken" CASCADE;
     CREATE TABLE "RevokedToken"
     (
        token VARCHAR(2048) UNIQUE,
        PRIMARY KEY (token)
     );
     """


def select_user():
    """
        Request to select user
    """

    return """SELECT userid, email, keyhash, symmetrickeyencrypted, salt, hastwofactorauth, twofactorauth, verified, vault  FROM duckpass."User" WHERE email = %s"""


def insert_user():
    """
        Request to insert user
    """

    return """INSERT INTO duckpass."User" (email, keyHash, symmetricKeyEncrypted, salt) VALUES (%s, %s, %s, %s)"""


def update_two_factor_auth():
    return """UPDATE duckpass."User" SET twoFactorAuth = %s, hasTwoFactorAuth = %s WHERE email = %s"""


def update_verification():
    return """UPDATE duckpass."User" SET verified = TRUE WHERE email = %s"""


def vault_update():
    return """UPDATE duckpass."User" SET vault = %s WHERE email = %s"""


def add_revoked_token():
    return """INSERT INTO duckpass."RevokedToken" (token) VALUES (%s)"""


def check_token_revoked():
    return """SELECT EXISTS(SELECT 1 FROM duckpass."RevokedToken" WHERE token = %s)"""


def delete_user():
    return """DELETE FROM duckpass."User" WHERE email = %s"""


def update_user_email():
    return """UPDATE duckpass."User" SET email = %s WHERE email = %s"""


def password_update():
    return """UPDATE duckpass."User" SET keyHash = %s, symmetricKeyEncrypted = %s, salt = %s, vault = %s WHERE email = %s"""
