"""Tests for Face Recognizer sensor."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

from custom_components.face_recognizer.const import (
    ATTR_EVENT_ID,
    ATTR_STATUS,
    ATTR_TIMESTAMP,
    STATUS_NO,
    STATUS_YES,
)
from custom_components.face_recognizer.sensor import FaceRecognizerSensor


def test_sensor_initialization() -> None:
    """Test sensor initialization."""
    sensor = FaceRecognizerSensor("test_entry")
    assert sensor._attr_native_value == STATUS_NO
    assert sensor.last_timestamp is None
    assert sensor.last_event_id is None


def test_validate_event_success() -> None:
    """Test valid event validation."""
    sensor = FaceRecognizerSensor("test_entry")
    event = {
        "type": "update",
        "status": "yes",
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }
    assert sensor.validate_event(event) is True


def test_validate_event_missing_field() -> None:
    """Test event validation with missing field."""
    sensor = FaceRecognizerSensor("test_entry")
    event = {
        "type": "update",
        "status": "yes",
        "timestamp": datetime.now().isoformat(),
    }
    assert sensor.validate_event(event) is False


def test_validate_event_invalid_status() -> None:
    """Test event validation with invalid status."""
    sensor = FaceRecognizerSensor("test_entry")
    event = {
        "type": "update",
        "status": "maybe",
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }
    assert sensor.validate_event(event) is False


def test_validate_event_yes_status() -> None:
    """Test event validation with 'yes' status."""
    sensor = FaceRecognizerSensor("test_entry")
    event = {
        "type": "update",
        "status": "YES",
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }
    assert sensor.validate_event(event) is True


def test_validate_event_no_status() -> None:
    """Test event validation with 'no' status."""
    sensor = FaceRecognizerSensor("test_entry")
    event = {
        "type": "update",
        "status": "NO",
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }
    assert sensor.validate_event(event) is True


def test_process_event_recognized() -> None:
    """Test processing recognized event."""
    sensor = FaceRecognizerSensor("test_entry")
    timestamp = datetime.now().isoformat()
    event_id = str(uuid.uuid4())

    sensor.async_write_ha_state = MagicMock()

    sensor.process_event(STATUS_YES, timestamp, event_id)

    assert sensor.recognition_status is True
    assert sensor.last_timestamp == timestamp
    assert sensor.last_event_id == event_id
    assert sensor.last_status == STATUS_YES
    assert sensor._attr_native_value == STATUS_YES
    sensor.async_write_ha_state.assert_called_once()


def test_process_event_unrecognized() -> None:
    """Test processing unrecognized event."""
    sensor = FaceRecognizerSensor("test_entry")
    timestamp = datetime.now().isoformat()
    event_id = str(uuid.uuid4())

    sensor.async_write_ha_state = MagicMock()

    sensor.process_event(STATUS_NO, timestamp, event_id)

    assert sensor.recognition_status is False
    assert sensor.last_timestamp == timestamp
    assert sensor.last_event_id == event_id
    assert sensor.last_status == STATUS_NO
    assert sensor._attr_native_value == STATUS_NO
    sensor.async_write_ha_state.assert_called_once()


def test_extra_state_attributes() -> None:
    """Test extra state attributes."""
    sensor = FaceRecognizerSensor("test_entry")
    timestamp = datetime.now().isoformat()
    event_id = str(uuid.uuid4())

    sensor.last_timestamp = timestamp
    sensor.last_event_id = event_id
    sensor.last_status = STATUS_YES

    attrs = sensor.extra_state_attributes

    assert attrs[ATTR_TIMESTAMP] == timestamp
    assert attrs[ATTR_EVENT_ID] == event_id
    assert attrs[ATTR_STATUS] == STATUS_YES
