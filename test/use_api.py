import requests
import json

BASE_URL = "http://localhost:8000"
PDF_FILE_PATH = "poem2.pdf"
TEXT_FILE_PATH = "poem2.txt"

# --- Paste the credentials you received from register_client.py here ---
CLIENT_ID = "rWm0FGPhEREXZr0w3waQ9g"
CLIENT_SECRET = "7Ema7WlHNMvyeApZxbUDClf0xx8_K6R_X3-Me4RIVR4"
# -----------------------------------------------------------------------


# 1. Get an access token using Client Credentials
print("Requesting access token...")
try:
    # The request body for the /oauth/token endpoint
    token_request_body = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    token_response = requests.post(f"{BASE_URL}/oauth/token", json=token_request_body)
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]
    print("Successfully received access token.")

    # 2. Use the token to call the protected API endpoints
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # --- Test PDF Extraction ---
    with open(PDF_FILE_PATH, "rb") as pdf_file:
        files = {"file": (PDF_FILE_PATH, pdf_file, "application/pdf")}
        
        print(f"\nUploading '{PDF_FILE_PATH}' to /extract-text/...")
        extract_response = requests.post(f"{BASE_URL}/extract-text/", headers=headers, files=files)
        extract_response.raise_for_status()

        print("\n--- PDF Extraction Response ---")
        print(json.dumps(extract_response.json(), indent=2))
        print("-----------------------------")

    # --- Test Text Search ---
    with open(TEXT_FILE_PATH, "rb") as text_file:
        data = {"keywords": ["fox", "dog", "lazy"]}
        files = {"file": (TEXT_FILE_PATH, text_file, "text/plain")}

        print(f"\nUploading '{TEXT_FILE_PATH}' to /search-text/...")
        search_response = requests.post(f"{BASE_URL}/search-text/", headers=headers, data=data, files=files)
        search_response.raise_for_status()

        print("\n--- Text Search Response ---")
        print(json.dumps(search_response.json(), indent=2))
        print("--------------------------")


except requests.exceptions.HTTPError as e:
    print(f"\nAPI Error: {e.response.text}")
except FileNotFoundError as e:
    print(f"\nError: Make sure '{e.filename}' exists in the same directory.")
except Exception as e:
    print(f"\nAn error occurred: {e}")