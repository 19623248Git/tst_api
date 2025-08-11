from sqlalchemy.orm import Session
import bcrypt
import secrets
from . import models, schemas

def get_client_by_name(db: Session, client_name: str):
    """Looks up a client by its name."""
    return db.query(models.Client).filter(models.Client.client_name == client_name).first()

def get_client_by_id(db: Session, client_id: str):
    """Looks up a client by its ID."""
    return db.query(models.Client).filter(models.Client.client_id == client_id).first()

def create_client(db: Session, client: schemas.ClientCreate):
    """Creates a new client application, returning the DB object and the plain secret."""
    client_id = secrets.token_urlsafe(16)
    plain_secret = secrets.token_urlsafe(32)
    hashed_secret = bcrypt.hashpw(plain_secret.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    db_client = models.Client(
        client_id=client_id,
        client_secret_hash=hashed_secret,
        client_name=client.client_name,
        email=client.email,
        redirect_uri=client.redirect_uri
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client, plain_secret

def authenticate_client(db: Session, client_id: str, client_secret: str):
    """Authenticates a client by checking its ID and secret."""
    client = get_client_by_id(db, client_id=client_id)
    if not client:
        return None
    if not bcrypt.checkpw(client_secret.encode('utf-8'), client.client_secret_hash.encode('utf-8')):
        return None
    return client