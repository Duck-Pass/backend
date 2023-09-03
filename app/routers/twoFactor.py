from fastapi import APIRouter
from ..twoFactorAuth import *
from ..mail import *
from ..model import *

router = APIRouter(
    tags=["Two Factor Authentication"]
)

@router.get("/generate_auth_key", response_model=AuthKey)
async def generateAuthKey(
    current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):
    if current_user.twoFactorAuth != "0":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication is already enabled")

    auth_key = generate_secret()
    return {"authKey": auth_key, "url": generate_qrcode_url(auth_key, current_user.email)}


@router.post("/enable_two_factor_auth")
async def enableTwoFactorAuth(
    current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)],
    auth_key: str,
    totp_code: str
):
    if current_user.twoFactorAuth != "0":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication is already enabled")

    if not verify_code(auth_key, totp_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

    insertUpdateDeleteRequest(updateTwoFactorAuth(), (auth_key, True, current_user.email))
    return {"message": "Two-factor authentication enabled successfully"}


@router.post("/check_two_factor_auth")
async def checkTwoFactorAuth(
    twoFactorAuthParams: TwoFactorAuthConnectionParams
):
    current_user = AuthenticateUser(twoFactorAuthParams.username, twoFactorAuthParams.password)

    if not current_user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.twoFactorAuth == "0":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication is not enabled")
    if not verify_code(current_user.twoFactorAuth, twoFactorAuthParams.totp_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createAccessToken(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/disable_two_factor_auth")
async def disableTwoFactorAuth(
        current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):
    if current_user.twoFactorAuth == "0":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication is not enabled")

    insertUpdateDeleteRequest(updateTwoFactorAuth(), ("0", False, current_user.email))
    return {"message": "Two-factor authentication disabled successfully"}
