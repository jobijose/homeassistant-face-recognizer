import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from . import mqtt_handler

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Face Recognizer from config entry."""
    hass.data.setdefault(DOMAIN, {})
    await mqtt_handler.async_setup_mqtt(hass, entry, hass.helpers.entity_platform.async_add_entities)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Face Recognizer entry."""
    return True
