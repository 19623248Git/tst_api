import requests
import json

# --- Configuration ---
BASE_URL = "http://[URL]:8000"

# --- Credentials have been added for you ---
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
# -------------------------------------------

print(f"--- Upgrading tier for Client ID: {CLIENT_ID} ---")

try:
    # 1. Get an access token first
    print("   Requesting access token...")
    token_request_body = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    token_response = requests.post(f"{BASE_URL}/oauth/token", json=token_request_body)
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]
    print("   ✅ Token received successfully.")

    # 2. Use the token to call the upgrade endpoint
    print("   Sending upgrade request...")
    headers = {"Authorization": f"Bearer {access_token}"}
    upgrade_response = requests.post(f"{BASE_URL}/upgrade-to-exclusive", headers=headers)
    upgrade_response.raise_for_status()
    
    # 3. Print the successful response
    upgraded_info = upgrade_response.json()
    print("\n✅ Upgrade successful!")
    print(f"   Message: {upgraded_info.get('message')}")
    
    client_details = upgraded_info.get('client', {})
    print(f"   Client Name: {client_details.get('client_name')}")
    print(f"   New Tier: {client_details.get('tier')}")

except requests.exceptions.HTTPError as e:
    print(f"❌ API Error: {e.response.status_code}")
    print(f"   Response: {e.response.text}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")