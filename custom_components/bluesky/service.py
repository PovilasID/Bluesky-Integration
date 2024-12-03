import aiohttp
import string
import asyncio
from datetime import datetime, timezone
from .const import PDSHOST
import logging
charLimit = 293
_LOGGER = logging.getLogger(__name__)
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

async def post_to_bluesky(ACCESS_JWT, username, message):
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

async def smart_split(text): #Splits the post according to bluesky character limits.
  substrings = []
  while len(text) > 0:
    # If the remaining text is smaller than the chunk size, add it as is
    if len(text) <= charLimit:
      substrings.append(text)
      break

    # Find the last space within the chunk size
    split_index = text.rfind(" ", 0, charLimit)
    
    # If no space is found (a very long word), split at the chunk size
    if split_index == -1:
      split_index = charLimit

    # Check if the chunk ends with punctuation
    while split_index > 0 and text[split_index - 1] in string.punctuation:
      split_index -= 1  # Move the split point to include punctuation in the chunk

    # Add the chunk to the list and remove it from the original text
    substrings.append(text[:split_index].strip())
    text = text[split_index:].strip()

  return substrings

async def parse_and_post(username, password, message):
  ACCESS_JWT, _ = await create_session(username, password)
  #clean up line returns to make character limit parser easier for now.
  stringedMessage = message.replace("\n", " ")
  if len(stringedMessage) > charLimit:
    #Splits the message into shorter segments if longer than character limit.
    messageObj = await smart_split(stringedMessage)
    for idx, substring in enumerate(messageObj):
      parsedMessage = substring+" ("+str(idx+1)+"/"+str(len(messageObj))+")"
      await post_to_bluesky(ACCESS_JWT, username, parsedMessage)
      await asyncio.sleep(0.1) #make sure we dont accdentally post out of order.
  else:#if short enough post directly
    await post_to_bluesky(ACCESS_JWT, username, stringedMessage)
     
  
  