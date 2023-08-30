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
    vault: Optional[bytes]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class TokenInfo(BaseModel):
    exp: int


class AuthKey(BaseModel):
    authKey: str