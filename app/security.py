import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import crud, models, database

SECRET_KEY = os.getenv("SECRET_KEY", "a_default_secret_key_for_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Point the tokenUrl to the new endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_client(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Dependency to get the current client from a JWT token.
    This protects endpoints by ensuring a valid client token is provided.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id: str = payload.get("sub")
        if client_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    client = crud.get_client_by_id(db, client_id=client_id)
    if client is None:
        raise credentials_exception
    return client

def require_tier(required_tier: str):
    """
    A dependency factory that creates a dependency to check for a specific client tier.
    """
    def tier_checker(current_client: models.Client = Depends(get_current_client)):
        if current_client.tier != required_tier:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires the '{required_tier}' tier."
            )
        return current_client
    return tier_checker