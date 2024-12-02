from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .config_flow import BlueskyConfigFlow
from .service import post_to_bluesky
from .const import DOMAIN

# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Set up the Bluesky component without using config flow (for backwards compatibility)."""
#     # If you're transitioning to config flow, you may not need this anymore
#     return True

# async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
#     """Set up Bluesky from a config entry."""
    
#     # Retrieve the username and password from the config entry
#     username = entry.data["username"]
#     password = entry.data["password"]

#     async def handle_post_service(call: ServiceCall):
#         """Handle the service call to post a message."""
#         message = call.data.get("message")
        
#         if not message:
#             hass.logger.error("Bluesky integration: No message provided in the service call.")
#             return
        
#         # Call the post_to_bluesky function to post the message
#         try:
#             result = await post_to_bluesky(username, password, message)
#             hass.bus.async_fire("bluesky_event", result)
#         except Exception as e:
#             hass.logger.error(f"Failed to post to Bluesky: {e}")
    
#     # Register the service that will handle the message posting
#     hass.services.async_register("bluesky", "post", handle_post_service)
    
#     # Return True to indicate successful setup
#     return True


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Set up Bluesky from a config entry."""
    username = entry.data["username"]
    password = entry.data["password"]

    async def handle_post_service(call: ServiceCall):
        """Handle the service call to post a message."""
        message = call.data.get("message")
        
        if not message:
            hass.logger.error("Bluesky integration: No message provided in the service call.")
            return
        
        try:
            result = await post_to_bluesky(username, password, message)
            hass.bus.async_fire("bluesky_event", result)
        except Exception as e:
            hass.logger.error(f"Failed to post to Bluesky: {e}")
    
    # Define the schema for the service
    service_schema = vol.Schema({
        vol.Required("message"): cv.string,
    })

    # Register the service with the schema
    hass.services.async_register("bluesky", "post", handle_post_service, schema=service_schema)
    
    return True