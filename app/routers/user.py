from fastapi import APIRouter
from starlette.responses import RedirectResponse
from base64 import b64encode
from ..mail import *
from ..crypto import *
from ..templates.mailTemplate import *
from ..model import *

router = APIRouter(
    tags=["User"]
)

SITE = os.environ.get('SITE')


@router.post("/register")
async def create_new_user(
        user_auth: UserAuth
):
    """
        Create user in database
        @param user_auth: UserAuth
    """

    user_data = (user_auth.email,)
    current_user = select_request(select_user(), user_data)

    if current_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    if not user_auth.key_hash == user_auth.key_hash_conf:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    salt, h = generate_master_key_hash(get_byte_from_base64(user_auth.key_hash))

    user_data = (user_auth.email, b64encode(h).decode(), user_auth.symmetric_key_encrypted, b64encode(salt).decode())
    insert_update_delete_request(insert_user(), user_data)
    await send_email(user_auth.email, confirmationMail)

    return {"message": "User created successfully"}


@router.get("/verify")
async def email_verification(token: str):
    current_user = await get_current_user_from_token(token)
    if current_user and not current_user.verified:
        insert_update_delete_request(update_verification(), (current_user.email,))
        return RedirectResponse(url=f"https://{SITE}/#/account-verified")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified")


@router.get("/get_user", response_model=UserGet)
async def get_user(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)]
):
    """
        Authenticate user and return user's data in JSON format
        @param current_user: SecureEndpointParams
        @return user: User
    """

    user_get = UserGet(
        id=current_user.id,
        email=current_user.email,
        symmetric_key_encrypted=current_user.symmetric_key_encrypted,
        has_two_factor_auth=current_user.has_two_factor_auth,
        vault=current_user.vault.decode("utf-8") if current_user.vault else None
    )

    return user_get


@router.put("/update_vault")
def update_vault(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)],
    vault: Optional[Vault] = None
):
    vault_content = bytes(vault.vault, 'utf-8') if vault.vault else None

    insert_update_delete_request(vault_update(), (vault_content, current_user.email))
    return {"message": "Vault updated successfully"}


@router.put("/update_email")
async def update_email(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)],
    new_user_email: UserUniqueId
):
    insert_update_delete_request(update_user_email(), (new_user_email.email, current_user.email))
    return {"message": "Email updated successfully"}


@router.put("/update_password")
async def update_password(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)],
    user_auth: UserAuth,
    vault: Optional[Vault] = None
):
    if not user_auth.key_hash == user_auth.key_hash_conf:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    salt, h = generate_master_key_hash(get_byte_from_base64(user_auth.key_hash))
    vault_content = bytes(vault.vault, 'utf-8') if vault.vault else None
    insert_update_delete_request(password_update(), (b64encode(h).decode(), user_auth.symmetric_key_encrypted, b64encode(salt).decode(), vault_content, current_user.email))

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    token: Annotated[SecureEndpointParams, Depends(protected_endpoints_token)]
):
    insert_update_delete_request(add_revoked_token(), (token,))
    return {"message": "Logout successful"}


@router.delete("/delete_account")
async def delete_account(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)]
):
    insert_update_delete_request(delete_user(), (current_user.email,))
    return {"message": "Account deleted successfully"}
