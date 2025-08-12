from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import fitz  # PyMuPDF
import ahocorasick
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

# Import setup, models, and schemas from other files in the 'app' directory
from . import database, models, schemas, crud, security

# --- Tier-based File Size Limits ---
FREEMIUM_LIMIT_BYTES = 5 * 1024 * 1024  # 5 MB
EXCLUSIVE_LIMIT_BYTES = 50 * 1024 * 1024 # 50 MB
# -------------------------------------

# This command creates all the database tables based on your models
# if they don't exist already.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- API Endpoints ---

@app.post("/register-client", response_model=schemas.ClientInfo)
def register_client(client: schemas.ClientCreate, db: Session = Depends(database.get_db)):
    """
    Register a new client application to get its credentials.
    Defaults to the 'freemium' tier.
    """
    db_client = crud.get_client_by_name(db, client_name=client.client_name)
    if db_client:
        raise HTTPException(status_code=400, detail="Client name already registered")
    
    new_client, plain_secret = crud.create_client(db=db, client=client)
    
    return {
        "client_id": new_client.client_id, 
        "client_secret": plain_secret, 
        "client_name": new_client.client_name,
        "email": new_client.email,
        "redirect_uri": new_client.redirect_uri,
        "tier": new_client.tier
    }


@app.post("/oauth/token", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.TokenRequestForm, db: Session = Depends(database.get_db)):
    """
    The Client Credentials Grant flow.
    """
    if form_data.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type, must be 'client_credentials'",
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
    access_token = security.create_access_token(
        data={"sub": client.client_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- New Payment and Tier Endpoints ---

@app.post("/upgrade-to-exclusive", response_model=schemas.UpgradeResponse)
def upgrade_tier(
    current_client: models.Client = Depends(security.get_current_client),
    db: Session = Depends(database.get_db)
):
    """
    Mock payment endpoint. Upgrades the current client's tier to 'exclusive'.
    """
    if current_client.tier == "exclusive":
        return {"message": "Client is already on the exclusive tier.", "client": current_client}

    updated_client = crud.upgrade_client_tier(db, client_id=current_client.client_id)
    return {"message": "Upgrade successful!", "client": updated_client}


# --- Service Endpoints ---

@app.post("/extract-text/")
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    current_client: models.Client = Depends(security.get_current_client) # Any authenticated client can use this
):
    """
    Freemium endpoint to extract text from an uploaded PDF file.
    """
    # Check file size against the freemium limit
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > FREEMIUM_LIMIT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the 5MB limit for the freemium tier."
        )

    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    try:
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        extracted_text = "".join(page.get_text() for page in doc)
        doc.close()
        return {"filename": file.filename, "text": extracted_text, "authorized_client": current_client.client_id, "tier_access": "freemium"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {e}")

@app.post("/extract-text-ocr/")
async def extract_text_from_pdf_ocr(
    file: UploadFile = File(...),
    current_client: models.Client = Depends(security.require_tier("exclusive")) # ONLY exclusive clients can use this
):
    """
    Exclusive endpoint to extract text from a PDF using a real OCR library.
    """
    # Check file size against the exclusive limit
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > EXCLUSIVE_LIMIT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the 50MB limit for the exclusive tier."
        )

    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        pdf_bytes = await file.read()
        
        # Step 1: Convert PDF pages to images
        images = convert_from_bytes(pdf_bytes)
        
        # Step 2: Run OCR on each image and combine the text
        ocr_text = ""
        for image in images:
            ocr_text += pytesseract.image_to_string(image) + "\n"

        return {
            "filename": file.filename, 
            "ocr_text": ocr_text,
            "authorized_client": current_client.client_id,
            "tier_access": "exclusive"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during OCR processing: {e}")


@app.post("/search-text/")
async def search_text_with_aho_corasick(
    keywords: List[str] = Form(...),
    file: UploadFile = File(...),
    current_client: models.Client = Depends(security.get_current_client) # Any authenticated client can use this
):
    """
    Freemium endpoint to search for multiple keywords in a text file.
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
    return {"filename": file.filename, "found_keywords": found_keywords, "authorized_client": current_client.client_id, "tier_access": "freemium"}