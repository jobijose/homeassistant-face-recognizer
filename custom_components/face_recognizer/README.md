# Face Recognizer Integration for Home Assistant

This custom integration allows Home Assistant to receive face recognition status updates from a face-recognizer application via MQTT. It provides a sensor that reflects the recognition status and the latest timestamp of the recognition event.

## Prerequisites

- Home Assistant with MQTT integration enabled and configured
- Face recognizer application that publishes events to the configured MQTT topic

## Installation

1. **Download the Integration**: Clone or download this repository to your Home Assistant's `custom_components` directory:

   ```
   custom_components/face_recognizer/
   ```

2. **Add to Home Assistant**:
   Restart Home Assistant to recognize the new integration. You can also add it through the Home Assistant UI by navigating to **Settings** → **Devices & Services** → **Create Integration** and searching for "Face Recognizer".

## Configuration

The Face Recognizer integration requires MQTT to be set up and operational in Home Assistant. Ensure the MQTT integration is enabled and configured correctly before installing Face Recognizer.

### MQTT Setup (Required)

Configure MQTT in your Home Assistant:

```yaml
mqtt:
  broker: <YOUR_MQTT_BROKER>
  port: <YOUR_MQTT_PORT>
  username: <YOUR_MQTT_USERNAME>
  password: <YOUR_MQTT_PASSWORD>
```

Once the integration is installed, it will automatically subscribe to MQTT messages on the topic: `face_recognizer/events`

## MQTT Message Format

The face recognizer application should publish messages to `face_recognizer/events` in the following JSON format:

```json
{
  "type": "update",
  "status": "yes",
  "timestamp": "2023-10-01T12:00:00Z",
  "event_id": "event_123"
}
```

### Required Fields

- **type**: Event type (currently only `"update"` events are processed)
- **status**: Recognition status - `"yes"` (face recognized) or `"no"` (face not recognized)
- **timestamp**: ISO 8601 formatted timestamp of the event
- **event_id**: Unique identifier for the event

## Entities

### Sensor: Face Recognizer Status

- **Entity ID**: `sensor.face_recognizer_status`
- **State**: `"true"` (recognized) or `"false"` (not recognized)
- **State Attributes**:
  - `status`: Current status (`yes` or `no`)
  - `timestamp`: ISO timestamp of the last recognition event
  - `event_id`: ID of the last event
  - `last_update`: ISO timestamp of when the sensor last updated
  - `status_text`: Text representation of the status

## Automations

### Event-based Automation

An event named `face_recognition_event` is fired whenever a message arrives on the MQTT topic. You can trigger automations and access the event data.

```yaml
alias: Notify on face recognized
trigger:
  - platform: event
    event_type: face_recognition_event
condition:
  - condition: template
    value_template: "{{ trigger.event.data.status == 'true' }}"
action:
  - service: notify.mobile_app_phone
    data:
      message: "Face recognized at {{ trigger.event.data.timestamp }}"
mode: single
```

Event data includes:

- `status`: Boolean representation of recognition (`"true"` or `"false"`)
- `timestamp`: ISO timestamp from the MQTT payload
- `event_id`: Event ID from the MQTT payload
- `raw`: The full JSON payload received

### State-based Automation

You can also use the sensor's state in automations:

```yaml
alias: Light on when face recognized
trigger:
  - platform: state
    entity_id: sensor.face_recognizer_status
    to: "true"
action:
  - service: light.turn_on
    entity_id: light.living_room
mode: single
```

## Troubleshooting

### Integration not showing in Settings

Ensure the custom_components folder is properly mounted in your Home Assistant configuration and the file structure is correct:

```
custom_components/
  face_recognizer/
    __init__.py
    config_flow.py
    const.py
    manifest.json
    sensor.py
    README.md
```

### MQTT messages not being received

1. Verify MQTT integration is properly configured and running
2. Check that messages are being published to `face_recognizer/events`
3. Enable debug logging in Home Assistant to see detailed messages:

   ```yaml
   logger:
     logs:
       custom_components.face_recognizer: debug
   ```

4. Verify the MQTT payload matches the required format exactly