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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,  # noqa: ANN001
) -> None:
    """Set up the Face Recognizer sensor for this config entry."""
    # Check if MQTT is available
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
            payload = json.loads(msg.payload)
            _LOGGER.debug(f"Received MQTT message: {payload}")

            # Validate event structure
            if not sensor.validate_event(payload):
                _LOGGER.error(f"Invalid event structure: {payload}")
                return

            # Extract event data
            event_type = payload.get("type")
            status = payload.get("status", "").lower()
            timestamp = payload.get("timestamp")
            event_id = payload.get("event_id")

            # Only process "update" events
            if event_type != EVENT_TYPE_UPDATE:
                if debug_enabled:
                    _LOGGER.debug(f"Ignoring non-update event type: {event_type}")
                return

            # Update sensor with event data
            sensor.process_event(status, timestamp, event_id)

            # Fire event for automations
            hass.bus.async_fire(
                EVENT_TYPE_RECOGNITION,
                {
                    ATTR_STATUS: sensor.last_status,
                    ATTR_TIMESTAMP: timestamp,
                    ATTR_EVENT_ID: event_id,
                    "raw": payload,
                },
            )

            if debug_enabled:
                _LOGGER.info(
                    f"Face recognition event processed: "
                    f"status={sensor.last_status}, timestamp={timestamp}, event_id={event_id}"
                )

        except json.JSONDecodeError:
            _LOGGER.error(f"Invalid JSON in MQTT message: {msg.payload}")
        except Exception as e:
            _LOGGER.error(f"Error processing MQTT message: {e}")

    # Subscribe and store unsubscribe callback so it can be removed on unload
    try:
        unsub = await mqtt.async_subscribe(hass, MQTT_TOPIC, message_received)
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = unsub
        _LOGGER.info("Successfully subscribed to MQTT topic: %s", MQTT_TOPIC)
    except Exception as e:
        _LOGGER.error("Failed to subscribe to MQTT topic %s: %s", MQTT_TOPIC, e)
        # Still add the sensor but it won't receive MQTT messages
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = None


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

        # Local variables for storing event data
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
        required_fields = ["type", "status", "timestamp", "event_id"]

        for field in required_fields:
            if field not in payload:
                _LOGGER.error(f"Missing required field in event: {field}")
                return False

        # Validate status values
        status = payload.get("status", "").lower()
        if status not in [STATUS_YES, STATUS_NO]:
            _LOGGER.error(f"Invalid status value: {status}. Expected 'yes' or 'no'")
            return False

        return True

    def process_event(self, status: str, timestamp: str, event_id: str) -> None:
        """Process recognition event and update sensor state."""
        # Convert status to boolean
        self.recognition_status = status == STATUS_YES

        # Store in local variables
        self.last_timestamp = timestamp
        self.last_event_id = event_id
        self.last_status = status

        # Update sensor state with yes/no values
        self._attr_native_value = STATUS_YES if self.recognition_status else STATUS_NO

        # Write state to Home Assistant
        self.async_write_ha_state()
