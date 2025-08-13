import requests
import json
import time

URL = "localhost"

# --- Configuration ---
BASE_URL = f"http://{URL}:8000"

# --- Step 1: Register a New Client Application ---
print("--- Step 1: Registering a new client ---")

# Information for the new client application
# Using a timestamp to ensure the client_name is unique for re-running the script
client_data = {
    "client_name": f"MyWebApp_{int(time.time())}",
    "email": f"dev{int(time.time())}@mywebapp.com",
    "redirect_uri": "https://mywebapp.com/callback"
}

try:
    response = requests.post(f"{BASE_URL}/register-client", json=client_data)
    response.raise_for_status()
    credentials = response.json()

    print("✅ Registration Successful!")
    print("\n--- Client Credentials (SAVE THESE for the next scripts) ---")
    print(json.dumps(credentials, indent=2))
    print("---------------------------------------------------------")

except requests.exceptions.HTTPError as e:
    print(f"❌ Error registering client: {e.response.text}")
except Exception as e:
    print(f"❌ An error occurred: {e}")