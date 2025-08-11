from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import fitz  # PyMuPDF
import ahocorasick

# Import setup, models, and schemas from other files in the 'app' directory
from . import database, models, schemas, crud, security

# This command creates all the database tables based on your models
# if they don't exist already.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- API Endpoints ---

@app.post("/register-client", response_model=schemas.ClientInfo)
def register_client(client: schemas.ClientCreate, db: Session = Depends(database.get_db)):
    """
    Register a new client application to get its credentials.
    In a real-world scenario, you would protect this endpoint.
    This endpoint returns the client_secret in plain text ONCE upon creation.
    """
    db_client = crud.get_client_by_name(db, client_name=client.client_name)
    if db_client:
        raise HTTPException(status_code=400, detail="Client name already registered")
    
    # The create_client function returns the client object and the plain-text secret
    new_client, plain_secret = crud.create_client(db=db, client=client)
    
    return {
        "client_id": new_client.client_id, 
        "client_secret": plain_secret, 
        "client_name": new_client.client_name,
        "email": new_client.email,
        "redirect_uri": new_client.redirect_uri
    }


@app.post("/oauth/token", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.TokenRequestForm, db: Session = Depends(database.get_db)):
    """
    The Client Credentials Grant flow.
    A client application sends its client_id and client_secret to get a token.
    """
    if form_data.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type",
        )

    client = crud.authenticate_client(
        db, client_id=form_data.client_id, client_secret=form_data.client_secret
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    # The 'sub' (subject) of the token is the client_id
    access_token = security.create_access_token(
        data={"sub": client.client_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/extract-text/")
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    current_client: models.Client = Depends(security.get_current_client)
):
    """
    Protected endpoint to extract text from an uploaded PDF file.
    Requires a valid client access token.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        extracted_text = "".join(page.get_text() for page in doc)
        doc.close()
        
        return {"filename": file.filename, "text": extracted_text, "authorized_client": current_client.client_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {e}")


@app.post("/search-text/")
async def search_text_with_aho_corasick(
    keywords: List[str] = Form(...),
    file: UploadFile = File(...),
    current_client: models.Client = Depends(security.get_current_client)
):
    """
    Protected endpoint to search for multiple keywords in a text file.
    Requires a valid client access token.
    """
    A = ahocorasick.Automaton()
    for index, keyword in enumerate(keywords):
        A.add_word(keyword, (index, keyword))
    A.make_automaton()

    try:
        text_content = (await file.read()).decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not decode file content as UTF-8.")

    found_keywords = [
        {"keyword": original_keyword, "start_index": end_index - len(original_keyword) + 1, "end_index": end_index}
        for end_index, (insert_order, original_keyword) in A.iter(text_content)
    ]

    return {"filename": file.filename, "found_keywords": found_keywords, "authorized_client": current_client.client_id}
