"""
Authentication Routes
Endpoints for user authentication and minimal hackathon flows.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext

try:
    from app.database import users_collection
except ImportError:
    users_collection = None

router = APIRouter(prefix="/auth", tags=["auth"])

# Configure passlib to use bcrypt exclusively
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class AuthRequest(BaseModel):
    email: str
    password: str

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: AuthRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database configured loosely.")
        
    existing_user = users_collection.find_one({"email": request.email.lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
        
    hashed_password = get_password_hash(request.password)
    
    user_dict = {
        "email": request.email.lower(),
        "hashed_password": hashed_password
    }
    
    users_collection.insert_one(user_dict)
    
    return {"message": "User created successfully"}

@router.post("/login")
async def login(request: AuthRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database configured loosely.")
        
    user = users_collection.find_one({"email": request.email.lower()})
    
    # Generic failure condition prevents account enumeration side-channels
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    return {
        "message": "Login successful",
        "userId": str(user["_id"])
    }
