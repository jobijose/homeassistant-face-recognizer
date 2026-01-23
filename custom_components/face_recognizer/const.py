"""Constants for the Face Recognizer integration."""

DOMAIN = "face_recognizer"
MQTT_TOPIC = "face_recognizer/events"

CONF_MQTT_BROKER = "mqtt_broker"
CONF_MQTT_PORT = "mqtt_port"

# Event types
EVENT_TYPE_RECOGNITION = "face_recognition_event"
EVENT_TYPE_UPDATE = "update"

# Status values (MQTT payload)
STATUS_YES = "yes"
STATUS_NO = "no"
STATUS_UNKNOWN = "unknown"

# Attributes
ATTR_TIMESTAMP = "timestamp"
ATTR_STATUS = "status"
ATTR_EVENT_ID = "event_id"
ATTR_LAST_EVENT_ID = "last_event_id"
ATTR_LAST_UPDATE = "last_update"
ATTR_STATUS_TEXT = "status_text"
