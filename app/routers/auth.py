from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from ..mail import *

router = APIRouter(
    tags=["Authentication"]
)


"""
    Endpoint to get access token
    @param form_data: OAuth2PasswordRequestForm
    @return Token
"""
@router.post("/token", response_model=Token)
async def getAccessToken(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = AuthenticateUser(form_data.username, form_data.password)

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