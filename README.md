# Face Recognizer Integration for Home Assistant

This custom integration connects your **Face Recognizer app** with **Home Assistant** via MQTT.  
It listens for JSON payloads with two fields:

```json
{
  "status": "Recognised" | "Unrecognised" | true | false,
  "timestamp": "2025-09-03T23:10:00"
}
