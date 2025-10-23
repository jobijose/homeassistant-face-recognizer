import json
import logging

from homeassistant.components.mqtt import DATA_MQTT
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, EVENT_RECOGNITION, MQTT_TOPIC

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,  # noqa: ANN001
) -> None:
    """Set up the Face Recognizer sensor for this config entry."""
    # Check if MQTT is available
    if DATA_MQTT not in hass.data:
        _LOGGER.error("MQTT integration is not available. Please ensure MQTT is configured.")
        return

    sensor = FaceRecognizerSensor(entry.entry_id)
    async_add_entities([sensor])

    async def message_received(msg: ReceiveMessage) -> None:
        try:
            payload = json.loads(msg.payload)
            status = payload.get("status")
            timestamp = payload.get("timestamp")

            # Convert status to boolean, default to False
            if isinstance(status, bool):
                sensor.native_value = status
            elif isinstance(status, str):
                # Convert string status to boolean
                sensor.native_value = status.lower() in ("true", "recognised", "recognized", "detected", "1", "yes")
            else:
                # Default to False for unknown types
                sensor.native_value = False

            # Store timestamp in attributes so automations can use it
            sensor.extra_state_attributes = {"timestamp": timestamp}
            sensor.async_write_ha_state()

            # Fire an event for automations that includes timestamp and raw payload
            hass.bus.async_fire(
                EVENT_RECOGNITION,
                {
                    "status": sensor.native_value,
                    "timestamp": timestamp,
                    "raw": payload,
                },
            )
        except json.JSONDecodeError as e:
            _LOGGER.exception("Failed to decode MQTT message as JSON: %s", e)
        except (KeyError, TypeError) as e:
            _LOGGER.exception("Missing or invalid fields in MQTT message: %s", e)

    # Subscribe and store unsubscribe callback so it can be removed on unload
    try:
        unsub = await hass.components.mqtt.async_subscribe(MQTT_TOPIC, message_received)
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = unsub
        _LOGGER.info("Successfully subscribed to MQTT topic: %s", MQTT_TOPIC)
    except Exception as e:
        _LOGGER.error("Failed to subscribe to MQTT topic %s: %s", MQTT_TOPIC, e)
        # Still add the sensor but it won't receive MQTT messages
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = None


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the sensor platform for this config entry: unsubscribe MQTT."""
    unsub = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if unsub:
        try:
            await unsub()
            _LOGGER.info("Successfully unsubscribed from MQTT topic for %s", entry.entry_id)
        except Exception:  # pragma: no cover - best-effort cleanup
            _LOGGER.exception("Error while unsubscribing MQTT for %s", entry.entry_id)
    return True


class FaceRecognizerSensor(SensorEntity):
    """Representation of a Face Recognizer sensor."""

    _attr_name = "Face Recognizer Status"
    _attr_icon = "mdi:face-recognition"
    _attr_native_unit_of_measurement = None

    def __init__(self, entry_id: str) -> None:
        """Initialize the FaceRecognizerSensor entity."""
        self._entry_id = entry_id
        self._attr_native_value = False  # Default to False
        self._attr_extra_state_attributes = {}
        self._attr_unique_id = f"{DOMAIN}_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Face Recognizer",
            manufacturer="Custom",
            model="Face Recognizer",
        )
