import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read the database URL from the environment variable set in docker-compose.yml
# Provide a default SQLite URL for local testing if the variable isn't set.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

print(f"--- DATABASE_URL: {DATABASE_URL} ---")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()