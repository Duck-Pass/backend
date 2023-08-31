from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: int
    email: str
    keyHash: str
    symmetricKeyEncrypted: str
    salt: str
    hastwofactorauth: bool
    twoFactorAuth: str
    verified: bool
    vault: Optional[bytes]

class UserGet(BaseModel):
    id: int
    email: str
    symmetricKeyEncrypted: str
    hasTwoFactorAuth: bool
    vault: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthKey(BaseModel):
    authKey: str
    url: str


class TwoFactorAuthConnectionParams(BaseModel):
    username: str
    password: str
    totp_code: str


class Vault(BaseModel):
    vault: str




class SecureEndpointParams(BaseModel):
    user: User
    token_revocation: bool
    token: Optional[str] = None