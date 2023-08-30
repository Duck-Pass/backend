from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: int
    email: str
    keyHash: str
    symmetricKeyEncrypted: str
    salt: str
    twoFactorAuth: str
    verified: bool
    vaultPassword: Optional[bytes]

class UserGet(BaseModel):
    id: int
    email: str
    symmetricKeyEncrypted: str
    twoFactorAuth: str
    vaultPassword: Optional[bytes]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class TokenInfo(BaseModel):
    exp: int


class AuthKey(BaseModel):
    authKey: str