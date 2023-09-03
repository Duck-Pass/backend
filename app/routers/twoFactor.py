from fastapi import APIRouter
from ..twoFactorAuth import *
from ..mail import *
from ..model import *

router = APIRouter(
    tags=["Two Factor Authentication"]
)


@router.get("/generate_auth_key", response_model=AuthKey)
async def generate_auth_key(
        current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)]
):
    if current_user.has_two_factor_auth:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication is already enabled")

    auth_key = generate_secret()
    return {"auth_key": auth_key, "url": generate_qrcode_url(auth_key, current_user.email)}


@router.post("/enable_two_factor_auth")
async def enable_two_factor_auth(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)],
    auth_key: str,
    totp_code: str
):
    if current_user.has_two_factor_auth:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication is already enabled")

    if not verify_code(auth_key, totp_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

    insert_update_delete_request(update_two_factor_auth(), (auth_key, True, current_user.email))
    return {"message": "Two-factor authentication enabled successfully"}


@router.post("/check_two_factor_auth")
async def check_two_factor_auth(
    two_factor_auth_params: TwoFactorAuthConnectionParams
):
    current_user = authenticate_user(two_factor_auth_params.username, two_factor_auth_params.key_hash)

    if not current_user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.has_two_factor_auth:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication is not enabled")
    if not verify_code(current_user.two_factor_auth, two_factor_auth_params.totp_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/disable_two_factor_auth")
async def disable_two_factor_auth(
        current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)]
):
    if not current_user.has_two_factor_auth:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication is not enabled")

    insert_update_delete_request(update_two_factor_auth(), ("0", False, current_user.email))
    return {"message": "Two-factor authentication disabled successfully"}
