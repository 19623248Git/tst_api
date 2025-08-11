from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

# Import setup, models, and schemas from other files in the 'app' directory
from . import database, models, schemas, crud

# This command creates all the database tables based on your models
# if they don't exist already.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "API is running. Go to /users to get all users."}

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Retrieve all users from the database.
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users