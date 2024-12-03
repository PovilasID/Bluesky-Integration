import logging
import aiohttp
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import HomeAssistant
import voluptuous as vol
from .const import DOMAIN, PDSHOST


_LOGGER = logging.getLogger(__name__)

class BlueskyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
  """Handle a config flow for Bluesky."""
  VERSION = 1
  def __init__(self):
    """Initialize the config flow."""
    self.username = None
    self.password = None

  async def async_step_user(self, user_input=None):
    """Handle the initial step to collect username and password."""
    if user_input is None:
      return self.async_show_form(
        step_id="user",
        data_schema=self._get_schema(),
      )

    # Store the user input
    self.username = user_input["username"]
    self.password = user_input["password"]

    # Validate the credentials (optional, but recommended)
    try:
      # Here, you can call a function to validate the credentials if needed
      await self._validate_credentials(self.username, self.password)
    except Exception as e:
      return self.async_show_form(
        step_id="user",
        data_schema=self._get_schema(),
        errors={"base": "invalid_credentials"},
      )

    # Save the credentials in the config entry
    return self.async_create_entry(
      title=self.username,
      data={
        "username": self.username,
        "password": self.password,
      },
    )

  def _get_schema(self):
    """Return a schema for the username and password fields."""
    return vol.Schema(
      {
        vol.Required("username"): str,
        vol.Required("password"): str,
      }
    )

  async def _validate_credentials(self, username, password):
    """Validate the provided credentials by making a request to the API."""
    url = f"{PDSHOST}/xrpc/com.atproto.server.createSession"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "identifier": username,  # Use the username provided by the user
        "password": password     # Use the password provided by the user
    }

    try:
      async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
          if response.status == 200:
            data = await response.json()
            # Extract token and refresh_token
            token = data.get("accessJwt")
            refresh_token = data.get("refreshJwt")
            if token and refresh_token:
              return "pass"  # Return "pass" if tokens are successfully retrieved
          else:
            error_text = await response.text()
            _LOGGER.error(f"Failed to create session. Status: {response.status}, Error: {error_text}")
            raise HomeAssistantError(f"Invalid credentials: {error_text}")
    except Exception as e:
      _LOGGER.error(f"Error while validating credentials: {e}")
      raise HomeAssistantError("An error occurred while validating credentials.")

