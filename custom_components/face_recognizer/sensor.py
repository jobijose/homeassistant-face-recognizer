"""Face Recognizer sensor platform."""

import json
import logging
from datetime import datetime

from homeassistant.components import mqtt
from homeassistant.components.mqtt import DATA_MQTT
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_EVENT_ID,
    ATTR_LAST_UPDATE,
    ATTR_STATUS,
    ATTR_STATUS_TEXT,
    ATTR_TIMESTAMP,
    DOMAIN,
    EVENT_TYPE_RECOGNITION,
    EVENT_TYPE_UPDATE,
    MQTT_TOPIC,
    STATUS_NO,
    STATUS_YES,
)

_LOGGER = logging.getLogger(__name__)

# Upper bounds for untrusted MQTT input; anyone able to publish to the topic
# controls these values, so keep them from bloating state, events and logs.
MAX_PAYLOAD_BYTES = 1024
MAX_FIELD_LENGTH = 64


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Face Recognizer sensor for this config entry."""
    if DATA_MQTT not in hass.data:
        _LOGGER.error(
            "MQTT integration is not available. Please ensure MQTT is configured."
        )
        return

    sensor = FaceRecognizerSensor(entry.entry_id)
    async_add_entities([sensor])

    async def message_received(msg: ReceiveMessage) -> None:
        """Handle incoming MQTT event."""
        try:
            if len(msg.payload) > MAX_PAYLOAD_BYTES:
                _LOGGER.warning(
                    "Ignoring MQTT message larger than %d bytes", MAX_PAYLOAD_BYTES
                )
                return

            payload = json.loads(msg.payload)
            _LOGGER.debug("Received MQTT message: %r", payload)

            if not sensor.validate_event(payload):
                _LOGGER.warning("Ignoring MQTT message with invalid event structure")
                return

            event_type = payload.get("type")
            status = payload["status"].lower()
            timestamp = payload.get("timestamp")
            event_id = payload.get("event_id")

            if event_type != EVENT_TYPE_UPDATE:
                _LOGGER.debug("Ignoring non-update event type: %s", event_type)
                return

            sensor.process_event(status, timestamp, event_id)

            hass.bus.async_fire(
                EVENT_TYPE_RECOGNITION,
                {
                    ATTR_STATUS: sensor.last_status,
                    ATTR_TIMESTAMP: timestamp,
                    ATTR_EVENT_ID: event_id,
                },
            )

            _LOGGER.info(
                "Face recognition event processed: status=%s, timestamp=%s, event_id=%s",
                sensor.last_status,
                timestamp,
                event_id,
            )

        except (json.JSONDecodeError, UnicodeDecodeError):
            _LOGGER.warning("Ignoring MQTT message with invalid JSON")
        except Exception:
            _LOGGER.exception("Error processing MQTT message")

    try:
        unsub = await mqtt.async_subscribe(hass, MQTT_TOPIC, message_received)
        # Release the subscription when the entry unloads so reloads do not
        # stack duplicate handlers.
        entry.async_on_unload(unsub)
        _LOGGER.info("Successfully subscribed to MQTT topic: %s", MQTT_TOPIC)
    except Exception:
        _LOGGER.exception("Failed to subscribe to MQTT topic %s", MQTT_TOPIC)


class FaceRecognizerSensor(SensorEntity):
    """Sensor for face recognition status."""

    _attr_name = "Face Recognizer Status"
    _attr_icon = "mdi:face-recognition"
    _attr_native_unit_of_measurement = None
    _attr_unique_id = f"{DOMAIN}_status"
    _attr_has_entity_name = False
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [STATUS_YES, STATUS_NO]

    def __init__(self, entry_id: str) -> None:
        """Initialize the FaceRecognizerSensor entity."""
        self._entry_id = entry_id
        self._attr_native_value = STATUS_NO

        self.last_timestamp: str | None = None
        self.last_event_id: str | None = None
        self.last_status: str = STATUS_NO
        self.recognition_status: bool = False

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Face Recognizer",
            manufacturer="jobijose",
            model="Face Recognizer",
            suggested_area="Security",
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            ATTR_TIMESTAMP: self.last_timestamp,
            ATTR_EVENT_ID: self.last_event_id,
            ATTR_STATUS: self.last_status,
            ATTR_LAST_UPDATE: datetime.now().isoformat(),
            ATTR_STATUS_TEXT: self.last_status,
        }

    def validate_event(self, payload: dict) -> bool:
        """Validate MQTT event structure."""
        if not isinstance(payload, dict):
            _LOGGER.error("Event payload must be a JSON object")
            return False

        required_fields = ["type", "status", "timestamp", "event_id"]

        for field in required_fields:
            if field not in payload:
                _LOGGER.error("Missing required field in event: %s", field)
                return False
            value = payload[field]
            if not isinstance(value, str) or len(value) > MAX_FIELD_LENGTH:
                _LOGGER.error(
                    "Field %s must be a string of at most %d characters",
                    field,
                    MAX_FIELD_LENGTH,
                )
                return False

        status = payload["status"].lower()
        if status not in [STATUS_YES, STATUS_NO]:
            _LOGGER.error("Invalid status value. Expected 'yes' or 'no'")
            return False

        return True

    def process_event(self, status: str, timestamp: str, event_id: str) -> None:
        """Process recognition event and update sensor state."""
        self.recognition_status = status == STATUS_YES

        self.last_timestamp = timestamp
        self.last_event_id = event_id
        self.last_status = status

        self._attr_native_value = STATUS_YES if self.recognition_status else STATUS_NO

        self.async_write_ha_state()
