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


def check_user_exists(email: str):
    """
    Checks if the given email is already in the database
    :param str email: Email to check
    :return: True if the user exists, False otherwise
    """
    user_data = (email,)
    current_user = select_request(select_user(), user_data)
    return current_user is not None


def get_user_from_db(email: str):
    """
    Get user from database based on email
    :param str email: User's email to get from database
    :return: User's data
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
    Authenticate user with email and key hash (password)
    :param str email: User's email
    :param str key_hash: User's key hash (password)
    :return: User's data if credentials are valid
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
    :param dict data: Data to encode in token (user's email)
    :param expires_delta: Token expiration time
    :return: JWT token for user authentication
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
    :param str token: JWT token for user authentication
    :return: User's data if token is valid
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decoding token and checking if the content (email) corresponds to a user in the database
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
    """
    Check if token is revoked in the database
    :param str token: JWT token for user authentication
    :return: None
    """
    if select_request(check_token_revoked(), (token,))[0]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")


async def protected_endpoints(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Get current user from token
    :param str token: JWT token for user authentication
    :return: User's data if token is valid
    """
    is_token_revoked(token)
    current_user = await get_current_user_from_token(token)
    return current_user


async def protected_endpoints_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Get current user from token
    :param str token: JWT token for user authentication
    :return: Received token
    """
    is_token_revoked(token)
    return token
