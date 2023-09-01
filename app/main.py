from fastapi import FastAPI, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, Response
from base64 import b64encode
import json
from .twoFactorAuth import *
from .mail import *
from .crypto import *
from .templates.mailTemplate import *
from .hibp import *

SITE = os.environ.get('SITE')

"""
    Handle 404 error and redirect to custom 404 page
    @param request: Request
    @param exc: HTTPException
    @return RedirectResponse
"""
async def redirectionToNotFound(request: Request, exc: HTTPException):
    return RedirectResponse(status_code=404, url=f"https://{SITE}/#/404.html")

exception_handlers = {404: redirectionToNotFound}
app = FastAPI(exception_handlers=exception_handlers)    # Create FastAPI instance


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
    Create user in database
    @param email: str
    @param key_hash: str
    @param key_hash_conf: str
    @param symmetric_key_encrypted: str
"""
@app.post("/register")
async def createNewUser(email: str, key_hash: str, key_hash_conf: str, symmetric_key_encrypted: str):

    user_data = (email,)
    user = selectRequest(selectUser(), user_data)
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    if not key_hash == key_hash_conf:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    salt, h = generate_master_key_hash(get_byte_from_base64(key_hash))

    user_data = (email, b64encode(h).decode(), symmetric_key_encrypted, b64encode(salt).decode())
    insertUpdateDeleteRequest(insertUser(), user_data)
    await send_email(email, confirmationMail)

    return {"message": "User created successfully"}


@app.get("/verify")
async def email_verification(token: str):
    user = await getCurrentUserFromToken(token)
    if user and not user.verified:
        insertUpdateDeleteRequest(updateVerification(), (user.email,))
        redirect_url = f"https://{SITE}/#/verification"
        return RedirectResponse(url=redirect_url)
    raise HTTPException(status_code=400, detail="User already verified")


"""
    Authenticate user and return user's data in JSON format
    @param email: str
    @return user: User
"""
@app.get("/get_user", response_model=UserGet)
async def getUser(
    connection_info: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):
    current_user = connection_info[0]
    token_revocation = connection_info[1]

    if token_revocation:
        raise HTTPException(status_code=401, detail="Token revoked")

    userGet = UserGet(
        id=current_user.id,
        email=current_user.email,
        symmetricKeyEncrypted=current_user.symmetricKeyEncrypted,
        hasTwoFactorAuth=current_user.hastwofactorauth,
        vault=current_user.vault.decode("utf-8") if current_user.vault else None
    )

    return userGet


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

    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.hastwofactorauth == False:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = createAccessToken(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Two-factor authentication is enabled",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/generate_auth_key", response_model=AuthKey)
async def generateAuthKey(
    connection_info: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):
    current_user = connection_info[0]
    token_revocation = connection_info[1]

    if token_revocation:
        raise HTTPException(status_code=401, detail="Token revoked")

    if current_user.twoFactorAuth != "0":
        raise HTTPException(status_code=400, detail="Two-factor authentication is already enabled")

    auth_key = generate_secret()
    return {"authKey": auth_key, "url": generate_qrcode_url(auth_key, current_user.email)}


@app.post("/enable_two_factor_auth")
async def enableTwoFactorAuth(
    connection_info: Annotated[SecureEndpointParams, Depends(protectedEndpoints)],
    auth_key: str,
    totp_code: str
):
    current_user = connection_info[0]
    token_revocation = connection_info[1]

    if token_revocation:
        raise HTTPException(status_code=401, detail="Token revoked")

    if current_user.twoFactorAuth != "0":
        raise HTTPException(status_code=400, detail="Two-factor authentication is already enabled")

    if not verify_code(auth_key, totp_code):
        raise HTTPException(status_code=400, detail="Invalid code")

    insertUpdateDeleteRequest(updateTwoFactorAuth(), (auth_key, True, current_user.email))
    return {"message": "Two-factor authentication enabled successfully"}


@app.post("/check_two_factor_auth")
async def checkTwoFactorAuth(
    twoFactorAuthParams: TwoFactorAuthConnectionParams
):
    current_user = AuthenticateUser(twoFactorAuthParams.username, twoFactorAuthParams.password)

    if not current_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not current_user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.twoFactorAuth == "0":
        raise HTTPException(status_code=400, detail="Two-factor authentication is not enabled")
    if not verify_code(current_user.twoFactorAuth, twoFactorAuthParams.totp_code):
        raise HTTPException(status_code=400, detail="Invalid code")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createAccessToken(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/disable_two_factor_auth")
async def disableTwoFactorAuth(
        connection_info: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):
    current_user = connection_info[0]
    token_revocation = connection_info[1]

    if token_revocation:
        raise HTTPException(status_code=401, detail="Token revoked")

    if current_user.twoFactorAuth == "0":
        raise HTTPException(status_code=400, detail="Two-factor authentication is not enabled")

    insertUpdateDeleteRequest(updateTwoFactorAuth(), ("0", False, current_user.email))
    return {"message": "Two-factor authentication disabled successfully"}


@app.post("/update_vault")
def updateVault(
    connection_info: Annotated[SecureEndpointParams, Depends(protectedEndpoints)],
    vault: Vault
):
    current_user = connection_info[0]
    token_revocation = connection_info[1]

    if token_revocation:
        raise HTTPException(status_code=401, detail="Token revoked")

    insertUpdateDeleteRequest(vaultUpdate(), (bytes(vault.vault, 'utf-8'), current_user.email))
    return {"message": "Vault updated successfully"}


@app.get("/hibp_breaches")
async def getHIBPBreaches(
    connection_info: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):
    current_user = connection_info[0]
    token_revocation = connection_info[1]

    if token_revocation:
        raise HTTPException(status_code=401, detail="Token revoked")

    json_data = await getBreachesForUser(current_user.email)
    return Response(content=json.dumps(json_data), media_type="application/json")


@app.post("/logout")
async def logout(
    connection_info: Annotated[SecureEndpointParams, Depends(protectedEndpointsToken)]
):
    token_revocation = connection_info[0]
    token = connection_info[1]

    if token_revocation:
        raise HTTPException(status_code=401, detail="Token already revoked")

    insertUpdateDeleteRequest(addRevokedToken(), (token,))
    return {"message": "Logout successful"}


