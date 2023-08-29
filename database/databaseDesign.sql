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
    salt VARCHAR(2048) NOT NULL,
    twoFactorAuth VARCHAR(2048) DEFAULT '0',
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vaultPassword bytea,
    PRIMARY KEY (userId)
 );
