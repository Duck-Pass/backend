from datetime import timedelta, datetime
from fastapi import HTTPException, Depends, status
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .model import *
from .database import *
from .utils import byteaToText

SECRET_KEY = os.environ['SECRET_KEY']                                           # Key to generate token
ALGORITHM = os.environ['ALGORITHM']                                             # Algorithm to generate token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])    # Token expiration time
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")                          # Token url on API


"""
    Create access token
    @param data: dict
    @param expires_delta: timedelta
    @return encoded_jwt: str
"""
def createAccessToken(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt