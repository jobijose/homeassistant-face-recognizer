"""Tests for Face Recognizer sensor."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNKNOWN

from custom_components.face_recognizer.const import (
    DOMAIN,
    EVENT_TYPE_UPDATE,
    STATUS_YES,
    STATUS_NO,
    STATUS_RECOGNIZED,
    STATUS_UNRECOGNIZED,
    ATTR_TIMESTAMP,
    ATTR_EVENT_ID,
    ATTR_STATUS,
)
from custom_components.face_recognizer.sensor import FaceRecognizerSensor


@pytest.fixture
def sensor(hass: HomeAssistant):
    """Create a sensor instance."""
    return FaceRecognizerSensor("test_entry")


def test_sensor_initialization(sensor):
    """Test sensor initialization."""
    assert sensor._attr_native_value == STATE_UNKNOWN
    assert sensor.last_timestamp is None
    assert sensor.last_event_id is None


def test_validate_event_success(sensor):
    """Test valid event validation."""
    event = {
        "type": "update",
        "status": "yes",
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }
    assert sensor.validate_event(event) is True


def test_validate_event_missing_field(sensor):
    """Test event validation with missing field."""
    event = {
        "type": "update",
        "status": "yes",
        "timestamp": datetime.now().isoformat(),
    }
    assert sensor.validate_event(event) is False


def test_validate_event_invalid_status(sensor):
    """Test event validation with invalid status."""
    event = {
        "type": "update",
        "status": "maybe",
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }
    assert sensor.validate_event(event) is False


def test_validate_event_yes_status(sensor):
    """Test event validation with 'yes' status."""
    event = {
        "type": "update",
        "status": "YES",
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }
    assert sensor.validate_event(event) is True


def test_validate_event_no_status(sensor):
    """Test event validation with 'no' status."""
    event = {
        "type": "update",
        "status": "NO",
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }
    assert sensor.validate_event(event) is True


def test_process_event_recognized(sensor):
    """Test processing recognized event."""
    timestamp = datetime.now().isoformat()
    event_id = str(uuid.uuid4())
    
    # Mock async_write_ha_state
    sensor.async_write_ha_state = MagicMock()
    
    sensor.process_event(STATUS_YES, timestamp, event_id)
    
    assert sensor.recognition_status is True
    assert sensor.last_timestamp == timestamp
    assert sensor.last_event_id == event_id
    assert sensor.last_status == STATUS_RECOGNIZED
    assert sensor._attr_native_value == "true"
    sensor.async_write_ha_state.assert_called_once()


def test_process_event_unrecognized(sensor):
    """Test processing unrecognized event."""
    timestamp = datetime.now().isoformat()
    event_id = str(uuid.uuid4())
    
    # Mock async_write_ha_state
    sensor.async_write_ha_state = MagicMock()
    
    sensor.process_event(STATUS_NO, timestamp, event_id)
    
    assert sensor.recognition_status is False
    assert sensor.last_timestamp == timestamp
    assert sensor.last_event_id == event_id
    assert sensor.last_status == STATUS_UNRECOGNIZED
    assert sensor._attr_native_value == "false"
    sensor.async_write_ha_state.assert_called_once()


def test_extra_state_attributes(sensor):
    """Test extra state attributes."""
    timestamp = datetime.now().isoformat()
    event_id = str(uuid.uuid4())
    
    sensor.last_timestamp = timestamp
    sensor.last_event_id = event_id
    sensor.last_status = STATUS_RECOGNIZED

    attrs = sensor.extra_state_attributes
    
    assert attrs[ATTR_TIMESTAMP] == timestamp
    assert attrs[ATTR_EVENT_ID] == event_id
    assert attrs[ATTR_STATUS] == STATUS_RECOGNIZED


def test_http_update_recognized(sensor):
    """Test HTTP-based sensor update for recognized."""
    timestamp = datetime.now().isoformat()
    event_id = str(uuid.uuid4())
    
    # Mock async_write_ha_state
    sensor.async_write_ha_state = MagicMock()
    
    sensor.async_update_from_http(True, timestamp, event_id)
    
    assert sensor.recognition_status is True
    assert sensor.last_timestamp == timestamp
    assert sensor.last_event_id == event_id
    assert sensor._attr_native_value == "true"
    sensor.async_write_ha_state.assert_called_once()


def test_http_update_unrecognized(sensor):
    """Test HTTP-based sensor update for unrecognized."""
    timestamp = datetime.now().isoformat()
    
    # Mock async_write_ha_state
    sensor.async_write_ha_state = MagicMock()
    
    sensor.async_update_from_http(False, timestamp)
    
    assert sensor.recognition_status is False
    assert sensor.last_timestamp == timestamp
    assert sensor._attr_native_value == "false"
    assert sensor.last_event_id.startswith("http-")
    sensor.async_write_ha_state.assert_called_once()
    mock_unsub = AsyncMock()
    mock_hass.components.mqtt.async_subscribe.return_value = mock_unsub
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Get the message_received callback
    message_received = mock_hass.components.mqtt.async_subscribe.call_args[0][1]
    sensor = mock_async_add_entities.call_args[0][0][0]
    
    # Set hass attribute on sensor for async_write_ha_state to work
    sensor.hass = mock_hass
    sensor.async_write_ha_state = AsyncMock()
    
    # Create mock message with string status that should convert to True
    test_payload = {
        "status": "detected",  # This should convert to True
        "timestamp": "2024-01-01T12:00:00Z"
    }
    mock_msg = MagicMock(spec=ReceiveMessage)
    mock_msg.payload = json.dumps(test_payload)
    
    # Process message
    await message_received(mock_msg)
    
    # Verify sensor state updated (string "detected" should convert to True)
    assert sensor.native_value is True


@pytest.mark.asyncio
async def test_message_received_false_boolean(mock_hass, mock_entry, mock_async_add_entities):
    """Test message processing with false boolean status."""
    # Setup
    mock_hass.data[DATA_MQTT] = MagicMock()
    mock_unsub = AsyncMock()
    mock_hass.components.mqtt.async_subscribe.return_value = mock_unsub
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Get the message_received callback
    message_received = mock_hass.components.mqtt.async_subscribe.call_args[0][1]
    sensor = mock_async_add_entities.call_args[0][0][0]
    
    # Set hass attribute on sensor for async_write_ha_state to work
    sensor.hass = mock_hass
    sensor.async_write_ha_state = AsyncMock()
    
    # Create mock message with false boolean status
    test_payload = {
        "status": False,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    mock_msg = MagicMock(spec=ReceiveMessage)
    mock_msg.payload = json.dumps(test_payload)
    
    # Process message
    await message_received(mock_msg)
    
    # Verify sensor state updated to False
    assert sensor.native_value is False


@pytest.mark.asyncio
async def test_message_received_string_false(mock_hass, mock_entry, mock_async_add_entities):
    """Test message processing with string that should convert to false."""
    # Setup
    mock_hass.data[DATA_MQTT] = MagicMock()
    mock_unsub = AsyncMock()
    mock_hass.components.mqtt.async_subscribe.return_value = mock_unsub
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Get the message_received callback
    message_received = mock_hass.components.mqtt.async_subscribe.call_args[0][1]
    sensor = mock_async_add_entities.call_args[0][0][0]
    
    # Set hass attribute on sensor for async_write_ha_state to work
    sensor.hass = mock_hass
    sensor.async_write_ha_state = AsyncMock()
    
    # Create mock message with string that should convert to false
    test_payload = {
        "status": "false",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    mock_msg = MagicMock(spec=ReceiveMessage)
    mock_msg.payload = json.dumps(test_payload)
    
    # Process message
    await message_received(mock_msg)
    
    # Verify sensor state updated to False
    assert sensor.native_value is False


@pytest.mark.asyncio
async def test_message_received_unknown_status(mock_hass, mock_entry, mock_async_add_entities):
    """Test message processing with unknown status type."""
    # Setup
    mock_hass.data[DATA_MQTT] = MagicMock()
    mock_unsub = AsyncMock()
    mock_hass.components.mqtt.async_subscribe.return_value = mock_unsub
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Get the message_received callback
    message_received = mock_hass.components.mqtt.async_subscribe.call_args[0][1]
    sensor = mock_async_add_entities.call_args[0][0][0]
    
    # Set hass attribute on sensor for async_write_ha_state to work
    sensor.hass = mock_hass
    sensor.async_write_ha_state = AsyncMock()
    
    # Create mock message with unknown status type
    test_payload = {
        "status": 123,  # Invalid type
        "timestamp": "2024-01-01T12:00:00Z"
    }
    mock_msg = MagicMock(spec=ReceiveMessage)
    mock_msg.payload = json.dumps(test_payload)
    
    # Process message
    await message_received(mock_msg)
    
    # Verify sensor state updated to False (default for unknown types)
    assert sensor.native_value is False


@pytest.mark.asyncio
async def test_async_unload_entry(mock_hass, mock_entry):
    """Test unloading the sensor platform."""
    # Setup with unsubscribe callback
    mock_unsub = AsyncMock()
    mock_hass.data = {DOMAIN: {mock_entry.entry_id: mock_unsub}}
    
    result = await async_unload_entry(mock_hass, mock_entry)
    
    # Verify unsubscribe was called and entry removed
    mock_unsub.assert_called_once()
    assert mock_entry.entry_id not in mock_hass.data[DOMAIN]
    assert result is True


@pytest.mark.asyncio
async def test_async_unload_entry_no_callback(mock_hass, mock_entry):
    """Test unloading when no unsubscribe callback exists."""
    # Setup without unsubscribe callback
    mock_hass.data = {DOMAIN: {}}
    
    result = await async_unload_entry(mock_hass, mock_entry)
    
    # Should still return True
    assert result is True


def test_face_recognizer_sensor_init():
    """Test FaceRecognizerSensor initialization."""
    sensor = FaceRecognizerSensor("test_entry_id")
    
    assert sensor._entry_id == "test_entry_id"
    assert sensor._attr_name == "Face Recognizer Status"
    assert sensor._attr_icon == "mdi:face-recognition"
    assert sensor._attr_native_value is False  # Default should be False
    assert sensor._attr_unique_id == f"{DOMAIN}_status"
    assert sensor._attr_device_info is not None
