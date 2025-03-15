from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .config_flow import BlueskyConfigFlow
from .service import parse_and_post
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
  """Set up Bluesky from a config entry."""
  username = entry.data["username"]
  password = entry.data["password"]
  pds_host = entry.data["pds_host"]

  async def handle_post_service(call: ServiceCall):
    """Handle the service call to post a message."""
    message = call.data.get("message")
    image = call.data.get("image")
    
    if not message:
      hass.logger.error("Bluesky integration: No message provided in the service call.")
      return
    
    try:
      result = await parse_and_post(username, password, message, pds_host, image)
      hass.bus.async_fire("bluesky_event", result)
    except Exception as e:
      hass.logger.error(f"Failed to post to Bluesky: {e}")
  
  # Define the schema for the service
  service_schema = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Optional("image"): cv.string
  })

  # Register the service with the schema
  hass.services.async_register("bluesky", "post", handle_post_service, schema=service_schema)
  
  return True