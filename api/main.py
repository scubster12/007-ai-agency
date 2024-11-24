from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI(title="007 AI Agency API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", Fernet.generate_key().decode())
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Data Models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserPreferences(BaseModel):
    marketing_emails: bool = False
    product_updates: bool = True
    security_alerts: bool = True
    analytics_consent: bool = False
    personalization: bool = False
    cookie_preference: str = "essential"
    essential_cookies: bool = True
    analytics_cookies: bool = False
    marketing_cookies: bool = False
    functional_cookies: bool = False

class UserData(BaseModel):
    email: str
    preferences: UserPreferences
    last_access: datetime
    last_consent_update: datetime
    active_sessions: List[dict] = []

# Encryption setup
def get_encryption_key():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        key = Fernet.generate_key()
        with open(".env", "a") as f:
            f.write(f"\nENCRYPTION_KEY={key.decode()}")
    return key if isinstance(key, bytes) else key.encode()

fernet = Fernet(get_encryption_key())

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_data_path(email: str) -> Path:
    return Path(f"data/users/{email}.json")

def encrypt_data(data: dict) -> bytes:
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_data(encrypted_data: bytes) -> dict:
    return json.loads(fernet.decrypt(encrypted_data).decode())

# API Endpoints
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In production, implement proper user authentication
    user_data = {"sub": form_data.username}
    access_token = create_access_token(user_data)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/preferences")
async def get_preferences(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401)
        
        user_path = get_user_data_path(email)
        if not user_path.exists():
            return UserPreferences().dict()
        
        with open(user_path, "rb") as f:
            data = decrypt_data(f.read())
            return data["preferences"]
            
    except JWTError:
        raise HTTPException(status_code=401)

@app.put("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401)
        
        user_path = get_user_data_path(email)
        user_path.parent.mkdir(parents=True, exist_ok=True)
        
        user_data = {
            "email": email,
            "preferences": preferences.dict(),
            "last_access": datetime.utcnow().isoformat(),
            "last_consent_update": datetime.utcnow().isoformat(),
            "active_sessions": []  # In production, implement session tracking
        }
        
        with open(user_path, "wb") as f:
            f.write(encrypt_data(user_data))
            
        return {"status": "success"}
            
    except JWTError:
        raise HTTPException(status_code=401)

@app.post("/export-data")
async def export_user_data(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401)
        
        user_path = get_user_data_path(email)
        if not user_path.exists():
            raise HTTPException(status_code=404, detail="No data found")
        
        with open(user_path, "rb") as f:
            data = decrypt_data(f.read())
            return data
            
    except JWTError:
        raise HTTPException(status_code=401)

@app.delete("/user-data")
async def delete_user_data(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401)
        
        user_path = get_user_data_path(email)
        if user_path.exists():
            user_path.unlink()
        
        return {"status": "success"}
            
    except JWTError:
        raise HTTPException(status_code=401)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
