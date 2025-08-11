from pydantic import BaseModel

# Base schema for a User
class UserBase(BaseModel):
    username: str
    email: str

# Schema for reading a user from the database (will be used in API responses)
# It doesn't include the password for security.
class User(UserBase):
    id: int

    class Config:
        from_attributes = True # Pydantic v2+ (was orm_mode)