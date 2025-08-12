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
    # --- New Tier Column ---
    tier = Column(String(50), default="freemium", nullable=False)