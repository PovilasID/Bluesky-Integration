import aiohttp
from datetime import datetime, timezone
from .const import PDSHOST

async def create_session(BLUESKY_HANDLE, BLUESKY_PASSWORD):
    url = f"{PDSHOST}/xrpc/com.atproto.server.createSession"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "identifier": BLUESKY_HANDLE,
        "password": BLUESKY_PASSWORD
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                # Extract token and refresh_token
                token = data.get("accessJwt")
                refresh_token = data.get("refreshJwt")
                return token, refresh_token
            else:
                error_text = await response.text()
                raise Exception(f"Failed to create session. Status: {response.status}, Error: {error_text}")

async def post_to_bluesky(username, password, message):
    ACCESS_JWT, _ = await create_session(username, password)
    url = f"{PDSHOST}/xrpc/com.atproto.repo.createRecord"
    headers = {
        "Authorization": f"Bearer {ACCESS_JWT}",
        "Content-Type": "application/json"
    }
    payload = {
        "repo": username,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": message,
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print("Record created successfully:", data)
            else:
                error_text = await response.text()
                raise Exception(f"Failed to create record. Status: {response.status}, Error: {error_text}")
