"""Constants for the Face Recognizer integration."""

DOMAIN = "face_recognizer"
MQTT_TOPIC = "face_recognizer/recognition_result"

CONF_MQTT_BROKER = "mqtt_broker"
CONF_MQTT_PORT = "mqtt_port"

# Event fired whenever a recognition message is received from MQTT
EVENT_RECOGNITION = "face_recognition"
