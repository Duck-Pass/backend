from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: int
    username: str
    email: str
    keyHash: str
    symmetricKeyEncrypted: str
    twoFactorAuth: str
    vaultPassword: bytes


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class TokenInfo(BaseModel):
    exp: int