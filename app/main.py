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
        Handle 404 error and redirect to custom 404-page
        @return RedirectResponse
    """
    return RedirectResponse(status_code=status.HTTP_404_NOT_FOUND, url=f"https://{SITE}/#/404.html")

app = FastAPI(exception_handlers={status.HTTP_404_NOT_FOUND: redirection_to_not_found})    # Create FastAPI instance

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(twoFactor.router)
app.include_router(hibp.router)
