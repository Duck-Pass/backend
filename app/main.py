from .database import *
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import RedirectResponse


"""
    Handle 404 error and redirect to custom 404 page
    @param request: Request
    @param exc: HTTPException
    @return RedirectResponse
"""
async def redirectionToNotFound(request: Request, exc: HTTPException):
    return RedirectResponse('https://duckpass.ch/404.html')


exception_handlers = {404: redirectionToNotFound}
app = FastAPI(exception_handlers=exception_handlers)    # Create FastAPI instance


"""
    Create user in database
    @param username: str
    @param email: str
    @param key_hash: str
    @param symmetric_key_encrypted: str
    @param two_factor_auth: str
    @param vault_password: str    
"""
@app.post("/create_user/")
def createNewUser(username: str, email: str, key_hash: str, symmetric_key_encrypted: str, two_factor_auth: str, vault_password: str):
    user_data = (username, email, key_hash, symmetric_key_encrypted, two_factor_auth, vault_password)
    insertUpdateDeleteRequest(insertUser(), user_data)
    return {"message": "User created successfully"}