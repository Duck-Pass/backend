from fastapi import APIRouter
from starlette.responses import RedirectResponse
from base64 import b64encode
from ..mail import *
from ..crypto import *
from ..templates.mailTemplate import *

SITE = os.environ.get('SITE')

router = APIRouter(
    tags=["User"]
)

"""
    Create user in database
    @param email: str
    @param key_hash: str
    @param key_hash_conf: str
    @param symmetric_key_encrypted: str
"""
@router.post("/register")
async def createNewUser(userAuth : UserAuth):

    user_data = (userAuth.email,)
    user = selectRequest(selectUser(), user_data)

    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    if not userAuth.keyHash == userAuth.keyHashConf:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    salt, h = generate_master_key_hash(get_byte_from_base64(userAuth.keyHash))

    user_data = (userAuth.email, b64encode(h).decode(), userAuth.symmetricKeyEncrypted, b64encode(salt).decode())
    insertUpdateDeleteRequest(insertUser(), user_data)
    await send_email(userAuth.email, confirmationMail)

    return {"message": "User created successfully"}


@router.get("/verify")
async def email_verification(token: str):
    user = await getCurrentUserFromToken(token)
    if user and not user.verified:
        insertUpdateDeleteRequest(updateVerification(), (user.email,))
        redirect_url = f"https://{SITE}/#/account-verified"
        return RedirectResponse(url=redirect_url)
    raise HTTPException(status_code=400, detail="User already verified")


"""
    Authenticate user and return user's data in JSON format
    @param email: str
    @return user: User
"""
@router.get("/get_user", response_model=UserGet)
async def getUser(
    current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):

    userGet = UserGet(
        id=current_user.id,
        email=current_user.email,
        symmetricKeyEncrypted=current_user.symmetricKeyEncrypted,
        hasTwoFactorAuth=current_user.hastwofactorauth,
        vault=current_user.vault.decode("utf-8") if current_user.vault else None
    )

    return userGet


@router.put("/update_vault")
def updateVault(
    current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)],
    vault: Optional[Vault] = None
):
    vaultValue = bytes(vault.vault, 'utf-8') if vault.vault else None

    insertUpdateDeleteRequest(vaultUpdate(), (vaultValue, current_user.email))
    return {"message": "Vault updated successfully"}


@router.put("/update_email")
async def updateEmail(
    current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)],
    newUserEmail: UserUniqueId
):
    insertUpdateDeleteRequest(updateUserEmail(), (newUserEmail.email, current_user.email))
    return {"message": "Email updated successfully"}


@router.put("/update_password")
async def updatePassword(
    current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)],
    userAuth: UserAuth,
    vault: Optional[Vault] = None
):
    if not userAuth.keyHash == userAuth.keyHashConf:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    salt, h = generate_master_key_hash(get_byte_from_base64(userAuth.keyHash))
    vaultValue = bytes(vault.vault, 'utf-8') if vault.vault else None
    insertUpdateDeleteRequest(passwordUpdate(), (b64encode(h).decode(), userAuth.symmetricKeyEncrypted, b64encode(salt).decode(), vaultValue, current_user.email))

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    token: Annotated[SecureEndpointParams, Depends(protectedEndpointsToken)]
):
    insertUpdateDeleteRequest(addRevokedToken(), (token,))
    return {"message": "Logout successful"}


@router.delete("/delete_account")
async def deleteAccount(
    current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):
    insertUpdateDeleteRequest(deleteUser(), (current_user.email,))
    return {"message": "Account deleted successfully"}