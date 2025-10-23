# Face Recognizer Integration for Home Assistant

A robust custom integration that connects your **Face Recognizer application** with **Home Assistant** via MQTT. This integration provides real-time face recognition status updates.

## 📋 Requirements

- Home Assistant 2025.2.4 or later
- MQTT broker configured in Home Assistant
- Face recognition application that publishes to MQTT

## 🚀 Installation

### Option 1: HACS (Recommended)
1. Add this repository to HACS
2. Install "Face Recognizer" from the HACS store
3. Restart Home Assistant

### Option 2: Manual Installation
1. Download this repository
2. Copy the `face_recognizer` folder to your `custom_components` directory
3. Restart Home Assistant

### Option 3: Direct Integration Setup
[![Open your Home Assistant instance and show the integration page.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=face_recognizer)

## ⚙️ Configuration

### 1. MQTT Setup
Ensure MQTT is properly configured in your `configuration.yaml`:

```yaml
# Basic MQTT configuration
mqtt:
  # Your MQTT broker settings here
```

### 2. Integration Setup
1. Go to **Configuration** → **Integrations**
2. Click **Add Integration**
3. Search for **Face Recognizer**
4. Follow the setup wizard

## 📡 MQTT Message Format

The integration listens to the topic `face_recognizer/recognition_result` and expects JSON messages:

```json
{
  "status": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Status Values
The `status` field accepts multiple formats and converts them to boolean:

**Boolean Values:**
- `true` → `true` (face recognized)
- `false` → `false` (no face recognized)

**String Values (converted to boolean):**
- `"true"`, `"recognised"`, `"recognized"`, `"detected"`, `"1"`, `"yes"` → `true`
- Any other string → `false`

**Unknown Types:**
- Defaults to `false`

## 🎯 Usage

### Sensor Entity
The integration creates a sensor entity: `sensor.face_recognizer_status`

**Attributes:**
- `status`: Boolean value (`true`/`false`)
- `timestamp`: Last recognition timestamp

### Event Firing
Fires `face_recognition` events with data:
- `status`: Boolean recognition status
- `timestamp`: ISO timestamp
- `raw`: Complete JSON payload

## 🤖 Automations

### Boolean State Automation
```yaml
alias: "Turn on lights when face recognized"
trigger:
  - platform: state
    entity_id: sensor.face_recognizer_status
    to: "true"
action:
  - service: light.turn_on
    target:
      entity_id: light.hallway
```

### Event-based Automation
```yaml
alias: "Notify on face recognition"
trigger:
  - platform: event
    event_type: face_recognition
condition:
  - condition: template
    value_template: "{{ trigger.event.data.status }}"
action:
  - service: notify.mobile_app_your_phone
    data:
      message: "Face recognized at {{ trigger.event.data.timestamp }}"
```

### Advanced Automation with Conditions
```yaml
alias: "Smart lighting based on face recognition"
trigger:
  - platform: state
    entity_id: sensor.face_recognizer_status
action:
  - choose:
      - conditions:
          - condition: state
            entity_id: sensor.face_recognizer_status
            state: "true"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.hallway
          - service: notify.persistent_notification
            data:
              message: "Welcome home!"
      - conditions:
          - condition: state
            entity_id: sensor.face_recognizer_status
            state: "false"
        sequence:
          - service: light.turn_off
            target:
              entity_id: light.hallway
```

## 🧪 Testing

The integration includes comprehensive tests. Run them with:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

## 🐛 Troubleshooting

### Common Issues

**1. MQTT Connection Error**
```
Cannot subscribe to topic 'face_recognizer/recognition_result'
```
**Solution:** Ensure MQTT integration is properly configured and running.

**2. Automation Timeout**
```
Your new automation has saved, but waiting for it to setup has timed out
```
**Solution:** Check for conflicting MQTT sensor configurations in `configuration.yaml`.

**3. Sensor Shows "Unknown"**
**Solution:** Check MQTT message format and ensure the face recognition app is publishing correctly.

### Debug Logging
Enable debug logging in `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.face_recognizer: debug
    homeassistant.components.mqtt: debug
```

## 📝 Changelog

### v1.0.0
- ✅ Initial release with face recognizer Home assistant custom component

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
