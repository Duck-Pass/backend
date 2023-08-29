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
             username               VARCHAR(32),
             email                  VARCHAR(256) UNIQUE,
             keyHash     VARCHAR(2048) NOT NULL,
             symmetricKeyEncrypted  VARCHAR(2048) NOT NULL,
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
    return """SELECT * FROM duckpass."User" WHERE email = %s"""


"""
    Request to insert user
"""
def insertUser():
    return """INSERT INTO duckpass."User" (username, email, keyHash, symmetricKeyEncrypted, vaultPassword) VALUES (%s, %s,%s, %s, %s)"""


def deleteUser():
    return """DELETE FROM duckpass."User" WHERE email = %s"""


def updateTwoFactorAuth():
    return """UPDATE duckpass."User" SET twoFactorAuth = %s WHERE email = %s"""