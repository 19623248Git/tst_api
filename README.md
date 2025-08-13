Simple directions on how to use API after you register (i.e. the credentials obtained from ```/register-client```):
```py
    # Get access token
    token_request_body = {
        "grant_type": "client_credentials", # THIS IS FIXED, DO NOT CHANGE
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    token_response = requests.post(f"{BASE_URL}/oauth/token", json=token_request_body)
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    # Use the token to call an endpoint (e.g. upgrade endpoint)
    headers = {"Authorization": f"Bearer {access_token}"}
    upgrade_response = requests.post(f"{BASE_URL}/upgrade-to-exclusive", headers=headers)
    upgrade_response.raise_for_status()
```

For local development:

Run the docker-compose file:
docker-compose up --build

To check the database:
docker-compose exec db psql -U tstdb -d users

remove the web container:
docker-compose rm -f -s -v web

build the web container:
docker-compose up -d --build web

