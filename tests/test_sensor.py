"""Tests for the Face Recognizer sensor platform."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.mqtt import DATA_MQTT
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.face_recognizer.sensor import (
    FaceRecognizerSensor,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.face_recognizer.const import DOMAIN, EVENT_RECOGNITION, MQTT_TOPIC


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.bus = MagicMock()
    hass.bus.async_fire = AsyncMock()
    hass.components = MagicMock()
    hass.components.mqtt = MagicMock()
    hass.components.mqtt.async_subscribe = AsyncMock()
    return hass


@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    return entry


@pytest.fixture
def mock_async_add_entities():
    """Create a mock async_add_entities function."""
    return MagicMock()


@pytest.mark.asyncio
async def test_async_setup_entry_mqtt_not_available(mock_hass, mock_entry, mock_async_add_entities):
    """Test that setup fails gracefully when MQTT is not available."""
    # MQTT not in hass.data
    mock_hass.data = {}
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Should not add entities or subscribe to MQTT
    mock_async_add_entities.assert_not_called()
    mock_hass.components.mqtt.async_subscribe.assert_not_called()


@pytest.mark.asyncio
async def test_async_setup_entry_mqtt_available(mock_hass, mock_entry, mock_async_add_entities):
    """Test successful setup when MQTT is available."""
    # MQTT available
    mock_hass.data[DATA_MQTT] = MagicMock()
    mock_unsub = AsyncMock()
    mock_hass.components.mqtt.async_subscribe.return_value = mock_unsub
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Should add entities and subscribe to MQTT
    mock_async_add_entities.assert_called_once()
    mock_hass.components.mqtt.async_subscribe.assert_called_once_with(
        MQTT_TOPIC, 
        mock_hass.components.mqtt.async_subscribe.call_args[0][1]  # message_received callback
    )
    
    # Should store unsubscribe callback
    assert mock_hass.data[DOMAIN][mock_entry.entry_id] == mock_unsub


@pytest.mark.asyncio
async def test_async_setup_entry_mqtt_subscription_fails(mock_hass, mock_entry, mock_async_add_entities):
    """Test setup when MQTT subscription fails."""
    # MQTT available but subscription fails
    mock_hass.data[DATA_MQTT] = MagicMock()
    mock_hass.components.mqtt.async_subscribe.side_effect = Exception("Connection failed")
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Should still add entities but store None for unsubscribe callback
    mock_async_add_entities.assert_called_once()
    assert mock_hass.data[DOMAIN][mock_entry.entry_id] is None


@pytest.mark.asyncio
async def test_message_received_valid_json(mock_hass, mock_entry, mock_async_add_entities):
    """Test message processing with valid JSON payload."""
    # Setup
    mock_hass.data[DATA_MQTT] = MagicMock()
    mock_unsub = AsyncMock()
    mock_hass.components.mqtt.async_subscribe.return_value = mock_unsub
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Get the message_received callback
    message_received = mock_hass.components.mqtt.async_subscribe.call_args[0][1]
    sensor = mock_async_add_entities.call_args[0][0][0]  # First entity added
    
    # Set hass attribute on sensor for async_write_ha_state to work
    sensor.hass = mock_hass
    sensor.async_write_ha_state = AsyncMock()
    
    # Create mock message
    test_payload = {
        "status": True,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    mock_msg = MagicMock(spec=ReceiveMessage)
    mock_msg.payload = json.dumps(test_payload)
    
    # Process message
    await message_received(mock_msg)
    
    # Verify sensor state updated
    assert sensor.native_value is True
    assert sensor.extra_state_attributes == {"timestamp": "2024-01-01T12:00:00Z"}
    sensor.async_write_ha_state.assert_called_once()
    
    # Verify event fired
    mock_hass.bus.async_fire.assert_called_once_with(
        EVENT_RECOGNITION,
        {
            "status": True,
            "timestamp": "2024-01-01T12:00:00Z",
            "raw": test_payload,
        }
    )


@pytest.mark.asyncio
async def test_message_received_invalid_json(mock_hass, mock_entry, mock_async_add_entities):
    """Test message processing with invalid JSON payload."""
    # Setup
    mock_hass.data[DATA_MQTT] = MagicMock()
    mock_unsub = AsyncMock()
    mock_hass.components.mqtt.async_subscribe.return_value = mock_unsub
    
    await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)
    
    # Get the message_received callback
    message_received = mock_hass.components.mqtt.async_subscribe.call_args[0][1]
    
    # Create mock message with invalid JSON
    mock_msg = MagicMock(spec=ReceiveMessage)
    mock_msg.payload = "invalid json"
    
    # Process message - should not raise exception
    await message_received(mock_msg)
    
    # Verify no event was fired
    mock_hass.bus.async_fire.assert_not_called()


@pytest.mark.asyncio
async def test_message_received_string_status(mock_hass, mock_entry, mock_async_add_entities):
    """Test message processing with string status."""
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
