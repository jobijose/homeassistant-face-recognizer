import logging
import json
from homeassistant.components.mqtt import DOMAIN as MQTT_DOMAIN
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, MQTT_TOPIC

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Face Recognizer sensor."""
    sensor = FaceRecognizerSensor()
    async_add_entities([sensor])

    async def message_received(msg: ReceiveMessage):
        try:
            payload = json.loads(msg.payload)
            status = payload.get("status")
            timestamp = payload.get("timestamp")

            if isinstance(status, bool):
                sensor._attr_native_value = "Recognised" if status else "Unrecognised"
            elif isinstance(status, str):
                sensor._attr_native_value = status
            else:
                sensor._attr_native_value = "Unknown"

            sensor._attr_extra_state_attributes = {"timestamp": timestamp}
            sensor.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to parse MQTT message: %s", e)

    await hass.components.mqtt.async_subscribe(MQTT_TOPIC, message_received)


class FaceRecognizerSensor(SensorEntity):
    """Representation of a Face Recognizer sensor."""

    _attr_name = "Face Recognizer Status"
    _attr_icon = "mdi:face-recognition"

    def __init__(self):
        self._attr_native_value = "Unknown"
        self._attr_extra_state_attributes = {}
