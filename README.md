# Face Recognizer Integration for Home Assistant

A custom integration that connects your **Face Recognizer application** with **Home Assistant** via MQTT. This integration provides real-time face recognition status updates with dropdown state support for automations.

## 📋 Requirements

- Home Assistant 2025.2.0 or later
- MQTT integration enabled and configured
- Face recognition application that publishes to MQTT

## 🚀 Installation

### Option 1: HACS (Recommended)
1. Add this repository to HACS
2. Install "Face Recognizer" from the HACS store
3. Restart Home Assistant

### Option 2: Manual Installation
1. Download this repository
2. Copy the `custom_components/face_recognizer` folder to your Home Assistant's `custom_components` directory:
   ```
   custom_components/
     face_recognizer/
       __init__.py
       config_flow.py
       const.py
       manifest.json
       sensor.py
       strings.json
   ```
3. Restart Home Assistant

### Option 3: Direct Integration Setup
[![Open your Home Assistant instance and show the integration page.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=face_recognizer)

## ⚙️ Configuration

### 1. MQTT Setup (Required)
Configure MQTT in Home Assistant via **Settings** → **Devices & Services** → **Add Integration** → **MQTT**

Or via `configuration.yaml`:
```yaml
mqtt:
  broker: <YOUR_MQTT_BROKER>
  port: 1883
  username: <YOUR_USERNAME>  # optional
  password: <YOUR_PASSWORD>  # optional
```

### 2. Integration Setup
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Face Recognizer**
4. Click **Submit** (no additional configuration required)

The integration will automatically subscribe to MQTT messages on the topic: `face_recognizer/events`

## 📡 MQTT Message Format

The integration listens to the topic `face_recognizer/events` and expects JSON messages:

```json
{
  "type": "update",
  "status": "yes",
  "timestamp": "2026-01-23T12:00:00Z",
  "event_id": "event_123"
}
```

### Required Fields

- **type**: Event type (currently only `"update"` events are processed)
- **status**: Recognition status - `"yes"` (face recognized) or `"no"` (face not recognized)
- **timestamp**: ISO 8601 formatted timestamp of the event
- **event_id**: Unique identifier for the event (can be generated with `str(uuid.uuid4())` in Python)

### Status Values
- `"yes"` → Face recognized
- `"no"` → Face not recognized

## 🎯 Entities

### Sensor: Face Recognizer Status

- **Entity ID**: `sensor.face_recognizer_status`
- **Device Class**: `ENUM` (provides dropdown options in automations)
- **State**: `"yes"` or `"no"`
- **Icon**: `mdi:face-recognition`

**State Attributes:**
- `status`: Current status (`"yes"` or `"no"`)
- `timestamp`: ISO timestamp of the last recognition event
- `event_id`: Unique ID of the last event
- `last_update`: ISO timestamp of when the sensor last updated
- `status_text`: Same as status

### Device Information
- **Name**: Face Recognizer
- **Manufacturer**: jobijose
- **Model**: Face Recognizer
- **Suggested Area**: Security

## 📊 Events

The integration fires `face_recognition_event` whenever a valid MQTT message is received.

**Event Data:**
- `status`: Recognition status (`"yes"` or `"no"`)
- `timestamp`: ISO timestamp from the MQTT payload
- `event_id`: Event ID from the MQTT payload
- `raw`: The full JSON payload received

## 🤖 Automations

### Event-based Automation
```yaml
alias: "Notify on face recognition"
trigger:
  - platform: event
    event_type: face_recognition_event
condition:
  - condition: template
    value_template: "{{ trigger.event.data.status == 'yes' }}"
action:
  - service: notify.mobile_app_your_phone
    data:
      message: "Face recognized at {{ trigger.event.data.timestamp }}"
mode: single
```

## 📝 Changelog

### v1.0.0
- ✅ Initial release with face recognizer Home assistant custom component

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.