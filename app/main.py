from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .hibp import *
from .routers import auth, hibp, twoFactor, user

SITE = os.environ.get('SITE')


app = FastAPI(title="DuckPass API",
              description="API for the DuckPass password manager",
              version="1.0.0",
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
