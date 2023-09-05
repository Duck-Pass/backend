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
    email: UserId
):
    """
    Endpoint to get all breaches for a user
    :param UserId email: Used to get the breaches for a user
    :param User current_user: User's data and used for authentication
    :return: Content with the breaches of the user in a JSON format
    """

    if not is_valid_email(email.email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    json_data = await get_breaches_for_user(email.email)
    return Response(content=json.dumps(json_data), media_type="application/json")
