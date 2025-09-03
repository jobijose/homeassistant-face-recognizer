import logging
import json
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.mqtt.models import ReceiveMessage
from .sensor import FaceRecognizerSensor
from .const import MQTT_TOPIC

_LOGGER = logging.getLogger(__name__)

async def async_setup_mqtt(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Subscribe to MQTT topic and update sensor."""
    topic = entry.data.get("topic", MQTT_TOPIC)
    sensor = FaceRecognizerSensor(topic)
    async_add_entities([sensor])

    async def message_received(msg: ReceiveMessage):
        try:
            payload = json.loads(msg.payload)
            status = payload.get("status")
            timestamp = payload.get("timestamp")

            if isinstance(status, bool):
                sensor._attr_native_value = "Recognised" if status else "Unrecognised"
            elif isinstance(status, str):
                sensor._attr_native_value = status.capitalize()
            else:
                sensor._attr_native_value = "Unknown"

            sensor._attr_extra_state_attributes = {"timestamp": timestamp}
            sensor.async_write_ha_state()

        except Exception as e:
            _LOGGER.error("Failed to parse MQTT message: %s", e)

    await hass.components.mqtt.async_subscribe(topic, message_received)
