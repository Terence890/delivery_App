from fastapi import APIRouter, HTTPException, Depends, status
from pymongo.errors import ConnectionFailure
import logging

from app.db.mongodb import get_database
from app.models.user import UserCreate, UserLogin, TokenResponse, UserResponse, User # Import User model
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    db = await get_database()
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user using the User model
        user = User(
            **user_data.dict(exclude={'password'}),
            password=hash_password(user_data.password)
        )
        await db.users.insert_one(user.dict())
        
        # Create token
        access_token = create_access_token(data={"sub": user.id, "role": user.role})
        
        # Create UserResponse from the created User object
        user_response = UserResponse(**user.dict())
        return TokenResponse(access_token=access_token, user=user_response)
    except ConnectionFailure:
        raise HTTPException(status_code=503, detail="Could not connect to the database.")
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    db = await get_database()
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user['id'], "role": user['role']})
    user_response = UserResponse(**user)
    return TokenResponse(access_token=access_token, user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
