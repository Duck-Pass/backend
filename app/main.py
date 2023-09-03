from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from urllib.request import Request
from .mail import *
from .templates.mailTemplate import *
from .hibp import *
from .routers import auth, hibp, twoFactor, user

SITE = os.environ.get('SITE')


async def redirection_to_not_found(request: Request, exc: HTTPException):
    """
    Redirects to the 404 page
    :param Request request: Param needed for the function
    :param HTTPException exc: Param needed for the function
    :return: Redirect to the 404 page
    """
    return RedirectResponse(status_code=status.HTTP_404_NOT_FOUND, url=f"https://{SITE}/#/404.html")

app = FastAPI(title="DuckPass API",
              description="API for the DuckPass password manager",
              version="1.0.0",
              exception_handlers={status.HTTP_404_NOT_FOUND: redirection_to_not_found},
              license_info={
                  "name": "GPLv3",
                  "identifier": "GPL-3.0-only",
              })    # Create FastAPI instance

# Add CORS middleware for client requests to API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers of the API endpoints
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(twoFactor.router)
app.include_router(hibp.router)
