from fastapi import FastAPI, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from .auth import *

"""
    Handle 404 error and redirect to custom 404 page
    @param request: Request
    @param exc: HTTPException
    @return RedirectResponse
"""
async def redirectionToNotFound(request: Request, exc: HTTPException):
    return RedirectResponse('https://duckpass.ch/404.html')


exception_handlers = {404: redirectionToNotFound}
app = FastAPI(exception_handlers=exception_handlers)    # Create FastAPI instance


"""
    Create user in database
    @param username: str
    @param email: str
    @param key_hash: str
    @param symmetric_key_encrypted: str
    @param two_factor_auth: str
    @param vault_password: str    
"""
@app.post("/create_user/")
def createNewUser(username: str, email: str, key_hash: str, symmetric_key_encrypted: str, two_factor_auth: str, vault_password: str):
    user_data = (username, email, key_hash, symmetric_key_encrypted, two_factor_auth, vault_password)
    insertUpdateDeleteRequest(insertUser(), user_data)
    return {"message": "User created successfully"}


"""
    Authenticate user and return user's data in JSON format
    @param email: str
    @return user: User
"""
@app.get("/get_user/", response_model=User)
async def getUser(
    current_user: Annotated[User, Depends(getCurrentUserFromToken)]
):
    current_user = User(
        id=current_user[0],
        username=current_user[1],
        email=current_user[2],
        keyHash=current_user[3],
        symmetricKeyEncrypted=current_user[4],
        twoFactorAuth=current_user[5],
        vaultPassword=current_user[6]
    )
    return current_user


"""
    Endpoint to get access token
    @param form_data: OAuth2PasswordRequestForm
    @return Token
"""
@app.post("/token", response_model=Token)
async def getAccessToken(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = AuthenticateUser(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createAccessToken(
        data={"sub": user[2]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


"""
    Endpoint to get token info about expiration date
    @param token: str
    @return TokenInfo
"""
@app.get("/token_info/", response_model=TokenInfo)
def getTokenExpDate(token: str = Depends(oauth2_scheme)):
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expiration_timestamp = decoded_token['exp']
    return {"exp": expiration_timestamp}