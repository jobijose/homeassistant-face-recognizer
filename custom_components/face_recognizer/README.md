# Face Recognizer Integration for Home Assistant

This custom integration allows Home Assistant to receive face recognition status updates from a face-recognizer application via MQTT. It provides a sensor that reflects the recognition status and the latest timestamp of the recognition event.

## Installation

1. **Download the Integration**: Clone or download this repository to your Home Assistant's `custom_components` directory.

   ```
   custom_components/face_recognizer/
   ```

2. **Add to Home Assistant**:  
   [![Add to Home Assistant](https://my.home-assistant.io/badges/add.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=face_recognizer)

   Restart Home Assistant to recognize the new integration. You can also add it through the Home Assistant UI by navigating to `Configuration` > `Integrations` and searching for "Face Recognizer".

## Configuration

To configure the Face Recognizer integration, you need to set up the MQTT broker in your Home Assistant configuration. Ensure that the MQTT integration is enabled and configured correctly.

### Example Configuration

```yaml
mqtt:
  broker: <YOUR_MQTT_BROKER>
  port: <YOUR_MQTT_PORT>
  username: <YOUR_MQTT_USERNAME>
  password: <YOUR_MQTT_PASSWORD>
```

## Usage

Once the integration is installed and configured, it will automatically subscribe to the MQTT topic for face recognition updates. The integration will create a sensor that you can use in your Home Assistant dashboard.

### Sensor Attributes

- **status**: The current recognition status (e.g., "recognized", "not recognized").
- **timestamp**: The last time a recognition event was received.

## Example MQTT Message

The face recognizer app should publish messages to the configured MQTT topic in the following JSON format:

```json
{
  "status": true,
  "timestamp": "2023-10-01T12:00:00Z"
}
```

- **status**: Returns `true` if a face is recognized, `false` otherwise.
- **timestamp**: The last time a recognition event was

## Automations

You can now use this integration directly in automations via either the sensor state or the fired event.

### Event-based automation

An event named `face_recognition` is fired whenever a message arrives on the MQTT topic. You can trigger automations and access the parsed payload.

```yaml
alias: Notify on face recognized
trigger:
  - platform: event
    event_type: face_recognition
condition: []
action:
  - variables:
      status: "{{ trigger.event.data.status }}"
      ts: "{{ trigger.event.data.timestamp }}"
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ status == 'Recognised' }}"
        sequence:
          - service: notify.mobile_app_phone
            data:
              message: "Face recognized at {{ ts }}"
mode: single
```

Event data includes:

- `status`: Normalized string (Recognised/Unrecognised/Unknown)
- `timestamp`: ISO timestamp from the payload
- `raw`: The full JSON payload received

### State-based automation

You can also use the sensor's state in automations. The entity is named `sensor.face_recognizer_status`.

```yaml
alias: Light on when face recognized
trigger:
  - platform: state
    entity_id: sensor.face_recognizer_status
    to: "Recognised"
action:
  - service: light.turn_on
    target:
      entity_id: light.hall
mode: single
```