"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # TODO: Implement login logic
    pass


@router.post("/register")
async def register():
    """
    Register a new user
    """
    # TODO: Implement registration logic
    pass


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current user information
    """
    # TODO: Implement get current user logic
    pass
