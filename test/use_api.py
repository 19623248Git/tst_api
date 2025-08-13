import requests
import json

URL = "localhost"

# --- Configuration ---
BASE_URL = f"http://{URL}:8000"
PDF_FILE_PATH = "sample_ocr.pdf" # Make sure this file exists

# --- Paste the credentials you received from register_client.py here ---
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
# -----------------------------------------------------------------------

print(f"--- Testing API access for Client ID: {CLIENT_ID} ---")

try:
    # 1. Get an access token
    token_request_body = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    token_response = requests.post(f"{BASE_URL}/oauth/token", json=token_request_body)
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]
    print("✅ Token received successfully.")
    
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Attempt to use the Exclusive OCR endpoint first
    print("\n--- Attempting to use the best available feature ---")
    print("   Trying the Exclusive '/extract-text-ocr/' endpoint...")
    
    with open(PDF_FILE_PATH, "rb") as pdf_file:
        files = {"file": (PDF_FILE_PATH, pdf_file, "application/pdf")}
        ocr_response = requests.post(f"{BASE_URL}/extract-text-ocr/", headers=headers, files=files)
        
        # Check if the client has access to the exclusive feature
        if ocr_response.status_code == 200:
            print("   ✅ SUCCESS: Client is on the 'exclusive' tier and has access to OCR.")
            print("\n      --- OCR Scan Result ---")
            print(json.dumps(ocr_response.json(), indent=2))
            print("      -----------------------")
        
        # If blocked, fall back to the freemium feature
        elif ocr_response.status_code == 403:
            print("   ⚠️ INFO: Client is on the 'freemium' tier. Falling back to standard extraction.")
            
            print("\n   Trying the Freemium '/extract-text/' endpoint...")
            with open(PDF_FILE_PATH, "rb") as pdf_file_fallback:
                files_fallback = {"file": (PDF_FILE_PATH, pdf_file_fallback, "application/pdf")}
                extract_response = requests.post(f"{BASE_URL}/extract-text/", headers=headers, files=files_fallback)
                extract_response.raise_for_status()
                print("   ✅ SUCCESS: Standard text extraction complete.")
                print("\n      --- Standard Extraction Result ---")
                print(json.dumps(extract_response.json(), indent=2))
                print("      --------------------------------")
        else:
            # Handle other potential errors
            ocr_response.raise_for_status()

except requests.exceptions.HTTPError as e:
    print(f"\nAPI Error: {e.response.status_code}")
    print(f"   Response: {e.response.text}")
except FileNotFoundError:
    print(f"\nError: The file '{PDF_FILE_PATH}' was not found.")
except Exception as e:
    print(f"\nAn error occurred: {e}")
