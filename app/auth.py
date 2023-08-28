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
    Get user from database
    @param email: str
    @return user: tuple
"""
def getUserFromDB(email: str):
   user_data = (email,)
   user = selectRequest(selectUser(), user_data)
   if user is None:
       raise HTTPException(status_code=404, detail="User not found")
   user = user[:-1] + (byteaToText(user[-1]),)
   return user


"""
    Authenticate user, compare entered password with password in database
    @param email: str
    @param password: str
    @return user: tuple
"""
def AuthenticateUser(email: str, password: str):
    user = getUserFromDB(email)
    if not user:
        return False
    if not password == user[3]:
        return False
    return user


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


"""
    Get current user from token
    @param token: str
    @return user: tuple
"""
async def getCurrentUserFromToken(token: Annotated[str, Depends(oauth2_scheme)]):
    credentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentialsException
        tokenData = TokenData(username=username)
    except JWTError:
        raise credentialsException
    user = getUserFromDB(tokenData.username)
    if user is None:
        raise credentialsException
    return user