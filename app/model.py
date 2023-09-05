from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    """
    Represents a user in the database
    """

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
    """
    Represents a user with the information needed to be sent to the client
    """

    id: int
    email: str
    symmetric_key_encrypted: str
    has_two_factor_auth: bool
    vault: Optional[str]


class UserAuth(BaseModel):
    """
    Represents an authentication information of a user
    """

    email: Optional[str]
    key_hash: str
    key_hash_conf: str
    symmetric_key_encrypted: str


class Token(BaseModel):
    """
    Represents the token value and type for a JWT token
    """

    access_token: str
    token_type: str


class AuthKey(BaseModel):
    """
    Represents the two-factor authentication information needed to be sent to the client
    """

    auth_key: str
    url: str


class TwoFactorAuthConnectionParams(BaseModel):
    """
    Represents the params passed by the client when the user uses two-factor authentication at login
    """

    email: str
    key_hash: str
    totp_code: str


class Vault(BaseModel):
    """
    Represents the vault of a user
    """

    vault: str


class SecureEndpointParams(BaseModel):
    """
    Represents the params each protected function receives when a user authenticates with a JWT token
    """

    user: User
    token_revocation: bool
    token: Optional[str] = None
