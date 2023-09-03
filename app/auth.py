from datetime import timedelta, datetime
from fastapi import HTTPException, Depends, status
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .database import *
from .crypto import *
from .model import User
from .utils import bytea_to_text

SECRET_KEY = os.environ['SECRET_KEY']  # Key to generate token
ALGORITHM = os.environ['ALGORITHM']  # Algorithm to generate token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])  # Token expiration time
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Token url on API


def get_user_from_db(email: str):
    """
       Get user from database
       @param email: str
       @return current_user: tuple
    """

    user_data = (email,)
    current_user = select_request(select_user(), user_data)
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user[-1] is not None:
        current_user = current_user[:-1] + (bytea_to_text(current_user[-1]),)

    current_user = User(
        id=current_user[0],
        email=current_user[1],
        key_hash=current_user[2],
        symmetric_key_encrypted=current_user[3],
        salt=current_user[4],
        has_two_factor_auth=current_user[5],
        two_factor_auth=current_user[6],
        verified=current_user[7],
        vault=current_user[8]
    )

    return current_user


def authenticate_user(email: str, key_hash: str):
    """
        Authenticate user, compare entered password with password in database
        @param email: str
        @param key_hash: str
        @return current_user: tuple
    """

    current_user = get_user_from_db(email)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    if not verify_master_key_hash(get_byte_from_base64(key_hash), get_byte_from_base64(current_user.salt),
                                  get_byte_from_base64(current_user.key_hash)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    return current_user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
        Create access token
        @param data: dict
        @param expires_delta: timedelta
        @return encoded_jwt: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
    """
        Get current user from token
        @param token: str
        @return current_user: tuple
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    current_user = get_user_from_db(username)
    if current_user is None:
        raise credentials_exception
    return current_user


def is_token_revoked(token: str):
    if select_request(check_token_revoked(), (token,))[0]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")


async def protected_endpoints(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    is_token_revoked(token)
    current_user = await get_current_user_from_token(token)
    return current_user


async def protected_endpoints_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    is_token_revoked(token)
    return token
