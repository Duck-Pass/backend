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
    Create new user and send confirmation email
    :param UserAuth user_auth: User's authentication data (email, password, password confirmation)
    :return: Confirmation message and send email
    """

    user_data = (user_auth.email,)
    current_user = select_request(select_user(), user_data)

    if current_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    if not user_auth.key_hash == user_auth.key_hash_conf:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    # Hash the received password hash and generate a salt
    salt, h = generate_master_key_hash(get_byte_from_base64(user_auth.key_hash))

    user_data = (user_auth.email, b64encode(h).decode(), user_auth.symmetric_key_encrypted, b64encode(salt).decode())
    insert_update_delete_request(insert_user(), user_data)

    # Send confirmation email
    await send_email(user_auth.email, confirmation_mail)

    return {"message": "User created successfully"}


@router.get("/verify")
async def email_verification(token: str):
    """
    Verify user's email
    :param str token: Token received in the email
    :return: Redirect to the website
    """

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
    Get user's data
    :param User current_user: User's data
    :return: User's data for frontend
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
    """
    Update user's vault
    :param User current_user: User's data
    :param Vault vault: Vault value
    :return: Confirmation message
    """

    vault_content = bytes(vault.vault, 'utf-8') if vault.vault else None

    insert_update_delete_request(vault_update(), (vault_content, current_user.email))
    return {"message": "Vault updated successfully"}


@router.put("/update_email")
async def update_email(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)],
    user_auth: UserAuth,
    vault: Optional[Vault] = None
):
    """
    Update user's email
    :param User current_user: User's data
    :param UserAuth user_auth: User's authentication data
    :param UserUniqueId new_user_email: new user email
    :param Vault vault: User's vault
    :return: Confirmation message
    """
    if check_user_exists(user_auth.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    insert_update_delete_request(update_user_email(), (user_auth.email, current_user.email))

    # Recalculate the hash of the new password and generate a new salt
    salt, h = generate_master_key_hash(get_byte_from_base64(user_auth.key_hash))

    # Update the vault to be encrypted with the new password
    vault_content = bytes(vault.vault, 'utf-8') if vault.vault else None
    insert_update_delete_request(password_update(), (b64encode(h).decode(), user_auth.symmetric_key_encrypted, b64encode(salt).decode(), vault_content, user_auth.email))

    return {"message": "Email address changed successfully"}


@router.put("/update_password")
async def update_password(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)],
    user_auth: UserAuth,
    vault: Optional[Vault] = None
):
    """
    Update user's password
    :param User current_user: User's data
    :param UserAuth user_auth: User's authentication data (email, password, password confirmation, symmetric key)
    :param Vault vault: Vault value
    :return: Confirmation message
    """

    if not user_auth.key_hash == user_auth.key_hash_conf:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    # Recalculate the hash of the new password and generate a new salt
    salt, h = generate_master_key_hash(get_byte_from_base64(user_auth.key_hash))

    # Update the vault to be encrypted with the new password
    vault_content = bytes(vault.vault, 'utf-8') if vault.vault else None
    insert_update_delete_request(password_update(), (b64encode(h).decode(), user_auth.symmetric_key_encrypted, b64encode(salt).decode(), vault_content, current_user.email))

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    token: Annotated[SecureEndpointParams, Depends(protected_endpoints_token)]
):
    """
    Logout user
    :param str token: Token used for user's session
    :return: Confirmation message
    """

    insert_update_delete_request(add_revoked_token(), (token,))
    return {"message": "Logout successful"}


@router.delete("/delete_account")
async def delete_account(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)]
):
    """
    Delete user's account
    :param User current_user: User's data
    :return: Confirmation message
    """

    insert_update_delete_request(delete_user(), (current_user.email,))
    return {"message": "Account deleted successfully"}
