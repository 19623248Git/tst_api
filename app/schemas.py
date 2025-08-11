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

# Schema for the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str

# New schema for the token request body to clean up Swagger UI
class TokenRequestForm(BaseModel):
    grant_type: str = Field(..., pattern="client_credentials")
    client_id: str
    client_secret: str