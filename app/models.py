from sqlalchemy import Column, Integer, String
from .database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255), unique=True, index=True, nullable=False)
    client_secret_hash = Column(String(255), nullable=False)
    client_name = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    redirect_uri = Column(String(255))


# --- app/schemas.py ---
# File for the Pydantic models (data shapes for API requests/responses).

from pydantic import BaseModel
from typing import Optional

# Schema for creating a new client
class ClientCreate(BaseModel):
    client_name: str
    email: str
    redirect_uri: str

# Schema for returning client info (includes plain secret ONCE)
class ClientInfo(ClientCreate):
    client_id: str
    client_secret: str

# Schema for the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str