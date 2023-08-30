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

"""
    Execute database creation
"""
def createDatabase():
    with db_cursor() as cur:
        cur.execute(database())


"""
    Execute select requests
    @param req: str 
    @param values: tuple
    @return select result
"""
def selectRequest(req, values):
    with db_cursor() as cur:
        cur.execute(req, values)
        return cur.fetchone()


"""
    Execute insert and update requests
    @param req: str
    @param values: tuple
"""
def insertUpdateDeleteRequest(req, values):
    with db_cursor() as cur:
        cur.execute(req, values)


"""
    Database request
"""
def database():
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
        twoFactorAuth VARCHAR(2048) DEFAULT '0',
        verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        vaultPassword bytea,
        PRIMARY KEY (userId)
     );
     """


"""
    Request to select user
"""
def selectUser():
    return """SELECT userid, email, keyhash, symmetrickeyencrypted, salt, twofactorauth, verified, vaultpassword  FROM duckpass."User" WHERE email = %s"""


"""
    Request to insert user
"""
def insertUser():
    return """INSERT INTO duckpass."User" (email, keyHash, symmetricKeyEncrypted, salt) VALUES (%s, %s, %s, %s)"""


def deleteUser():
    return """DELETE FROM duckpass."User" WHERE email = %s"""


def updateTwoFactorAuth():
    return """UPDATE duckpass."User" SET twoFactorAuth = %s WHERE email = %s"""


def updateVerification():
    return """UPDATE duckpass."User" SET verified = TRUE WHERE email = %s"""


def updateVault():
    return """UPDATE duckpass."User" SET vaultPassword = %s WHERE email = %s"""


def updatePassword():
    return """UPDATE duckpass."User" SET keyHash = %s, salt = %s WHERE email = %s"""
