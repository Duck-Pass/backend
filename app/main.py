from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, Response
from .mail import *
from .templates.mailTemplate import *
from .hibp import *
from .routers import auth, hibp, twoFactor, user

SITE = os.environ.get('SITE')

"""
    Handle 404 error and redirect to custom 404 page
    @param request: Request
    @param exc: HTTPException
    @return RedirectResponse
"""
async def redirectionToNotFound(request: Request, exc: HTTPException):
    return RedirectResponse(status_code=404, url=f"https://{SITE}/#/404.html")

app = FastAPI(exception_handlers={404: redirectionToNotFound})    # Create FastAPI instance

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

