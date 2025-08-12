from pydantic import BaseModel, Field
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
    tier: str

# Schema for reading a client from the DB (doesn't include secret)
class Client(ClientCreate):
    client_id: str
    tier: str

    class Config:
        from_attributes = True

# Schema for the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for the token request body
class TokenRequestForm(BaseModel):
    grant_type: str = Field(..., pattern="client_credentials")
    client_id: str
    client_secret: str

# New schema for the upgrade response
class UpgradeResponse(BaseModel):
    message: str
    client: Client