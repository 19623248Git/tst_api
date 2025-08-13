import requests
import json

URL = "localhost"

# --- Configuration ---
BASE_URL = f"http://{URL}:8000"

# --- Your Client Credentials ---
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
# -----------------------------

# The text you want to check for explicit content
text_to_check = "bitch bitch bitch fuck fuck fuck"

print(f"--- Testing Explicit Content Detection for Client ID: {CLIENT_ID} ---")

try:
    # 1. Get an access token for your service
    print("   Requesting access token from your API...")
    token_request_body = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    token_response = requests.post(f"{BASE_URL}/oauth/token", json=token_request_body)
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]
    print("   ✅ Token received successfully.")

    # 2. Use the token to call the /detect-explicit endpoint
    print(f"\n   Sending text to /detect-explicit for analysis...")
    headers = {"Authorization": f"Bearer {access_token}"}
    detection_request_body = {
        "text": text_to_check
    }
    
    detect_response = requests.post(
        f"{BASE_URL}/detect-explicit", 
        headers=headers, 
        json=detection_request_body
    )
    detect_response.raise_for_status()

    # 3. Print the result from the third-party API
    result = detect_response.json()
    print("\n✅ Analysis complete!")
    print("   --- Detection Result ---")
    print(json.dumps(result, indent=2))
    print("   ------------------------")

except requests.exceptions.HTTPError as e:
    print(f"\n❌ API Error: {e.response.status_code}")
    print(f"   Response: {e.response.text}")
except Exception as e:
    print(f"\n❌ An unexpected error occurred: {e}")