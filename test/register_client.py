import requests
import json

BASE_URL = "http://localhost:8000"

# Information for the new client application you're registering
client_data = {
    "client_name": "ClientApp",
    "email": "ClientApp@App.com",
    "redirect_uri": "https://myclientapp.com/callback"
}

print(f"Registering new client: {client_data['client_name']}")

try:
    response = requests.post(f"{BASE_URL}/register-client", json=client_data)
    response.raise_for_status()

    credentials = response.json()
    print("\nRegistration Successful!")
    print("--- Client Credentials ---")
    print(json.dumps(credentials, indent=2))
    print("---------------------------------------------------------")

except requests.exceptions.HTTPError as e:
    print(f"\nError registering client: {e.response.text}")
except Exception as e:
    print(f"\nAn error occurred: {e}")