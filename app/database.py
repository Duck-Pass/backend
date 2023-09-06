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
    Context manager for database cursor
    :return: Database cursor
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
    Create database
    :return: None
    """
    with db_cursor() as cur:
        cur.execute(database())


def select_request(req, values):
    """
    Execute select request
    :param str req: Select request to execute
    :param tuples values: Values to insert in the request
    :return: Result of the request
    """
    with db_cursor() as cur:
        cur.execute(req, values)
        return cur.fetchone()


def insert_update_delete_request(req, values):
    """
    Execute insert, update or delete request
    :param str req: Request to execute
    :param tuples values: Values to insert in the request
    :return: None
    """
    with db_cursor() as cur:
        cur.execute(req, values)


def database():
    """
    Database architecture request
    :return: Database request
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
    :return: Request
    """

    return """SELECT userid, email, keyhash, symmetrickeyencrypted, salt, hastwofactorauth, twofactorauth, verified, vault  FROM duckpass."User" WHERE email = %s"""


def insert_user():
    """
    Request to insert user
    :return: Request
    """

    return """INSERT INTO duckpass."User" (email, keyHash, symmetricKeyEncrypted, salt) VALUES (%s, %s, %s, %s)"""


def update_two_factor_auth():
    """
    Request to update two-factor auth
    :return: Request
    """

    return """UPDATE duckpass."User" SET twoFactorAuth = %s, hasTwoFactorAuth = %s WHERE email = %s"""


def update_verification():
    """
    Request to update verification status of a user
    :return: Request
    """

    return """UPDATE duckpass."User" SET verified = TRUE WHERE email = %s"""


def vault_update():
    """
    Request to update vault
    :return: Request
    """

    return """UPDATE duckpass."User" SET vault = %s WHERE email = %s"""


def add_revoked_token():
    """
    Request to add revoked token
    :return: Request
    """

    return """INSERT INTO duckpass."RevokedToken" (token) VALUES (%s)"""


def check_token_revoked():
    """
    Request to check if token is revoked
    :return: Request
    """

    return """SELECT EXISTS(SELECT 1 FROM duckpass."RevokedToken" WHERE token = %s)"""


def delete_user():
    """
    Request to delete user
    :return: Request
    """

    return """DELETE FROM duckpass."User" WHERE email = %s"""


def update_user_email():
    """
    Request to update user email
    :return: Request
    """

    return """UPDATE duckpass."User" SET email = %s WHERE email = %s"""


def password_update():
    """
    Request to update password
    :return: Request
    """

    return """UPDATE duckpass."User" SET keyHash = %s, symmetricKeyEncrypted = %s, salt = %s, vault = %s WHERE email = %s"""
