from fastapi import APIRouter
import json
from starlette.responses import Response
from ..hibp import *
from ..mail import *

router = APIRouter(
    tags=["HIBP Integration"]
)


@router.get("/hibp_breaches")
async def getHIBPBreaches(
    current_user: Annotated[SecureEndpointParams, Depends(protectedEndpoints)]
):
    json_data = await getBreachesForUser(current_user.email)
    return Response(content=json.dumps(json_data), media_type="application/json")