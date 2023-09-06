from fastapi import APIRouter
import json
from starlette.responses import Response
from ..hibp import *
from ..mail import *
from ..model import *

router = APIRouter(
    tags=["HIBP Integration"]
)


@router.get("/hibp_breaches")
async def get_hibp_breaches(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)],
):
    """
    Endpoint to get breach for a user for a given domain
    :return: Content with the breaches of the user in a JSON format
    """

    json_data = await get_breach_for_user(current_user.email)
    return Response(content=json.dumps(json_data), media_type="application/json")


@router.get("/hibp_password")
async def get_hibp_breaches_password(
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)],
    hash_begin: str
):
    """
    Endpoint to get breach for a user for a given domain
    :param str hash_begin: Beginning of the hash of the password
    :return: Content with the breaches of the user in a JSON format
    """

    if not is_valid_email(current_user.email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    breached_hashes = await get_breach_for_password(current_user.email, hash_begin.upper())
    return breached_hashes
