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
    email: str,
    domain: str
):
    """
    Endpoint to get breach for a user for a given domain
    :param domain: Domain to check
    :param UserId email: Used to get the breaches for a user
    :param User current_user: User's data and used for authentication
    :return: Content with the breaches of the user in a JSON format
    """

    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    json_data = await get_breach_for_user(email, domain)
    if json_data:
        return {"message": "Breaches found"}
    else:
        return {"message": "No breaches found"}