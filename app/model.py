from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: int
    email: str
    key_hash: str
    symmetric_key_encrypted: str
    salt: str
    has_two_factor_auth: bool
    two_factor_auth: str
    verified: bool
    vault: Optional[bytes]


class UserGet(BaseModel):
    id: int
    email: str
    symmetric_key_encrypted: str
    has_two_factor_auth: bool
    vault: Optional[str]


class UserAuth(BaseModel):
    email: Optional[str]
    key_hash: str
    key_hash_conf: str
    symmetric_key_encrypted: str


class UserUniqueId(BaseModel):
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthKey(BaseModel):
    auth_key: str
    url: str


class TwoFactorAuthConnectionParams(BaseModel):
    username: str
    key_hash: str
    totp_code: str


class Vault(BaseModel):
    vault: str


class SecureEndpointParams(BaseModel):
    user: User
    token_revocation: bool
    token: Optional[str] = None
