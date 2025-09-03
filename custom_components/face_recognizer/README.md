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