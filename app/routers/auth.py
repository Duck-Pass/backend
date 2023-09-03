from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from ..mail import *
from ..model import *

router = APIRouter(
    tags=["Authentication"]
)


@router.post("/token", response_model=Token)
async def get_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
        Endpoint to get access token
        @param form_data: OAuth2PasswordRequestForm
        @return Token
    """
    current_user = authenticate_user(form_data.username, form_data.password)

    if not current_user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.has_two_factor_auth:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Two-factor authentication is enabled",
        headers={"WWW-Authenticate": "Bearer"},
    )
