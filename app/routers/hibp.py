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
    current_user: Annotated[SecureEndpointParams, Depends(protected_endpoints)]
):
    """
    Endpoint to get all breaches for a user
    :param User current_user: User's data
    :return: Content with the breaches of the user in a JSON format
    """

    json_data = await get_breaches_for_user(current_user.email)
    return Response(content=json.dumps(json_data), media_type="application/json")
