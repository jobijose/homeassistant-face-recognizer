#!/usr/bin/env python3
"""Test script to publish face recognition events to MQTT."""

import json
import sys
import uuid
from datetime import datetime

from paho.mqtt.client import Client


def publish_recognition_event(
    status: str = "yes",
    host: str = "mqtt",
    port: int = 1883,
    topic: str = "face_recognizer/events",
) -> None:
    """Publish a face recognition event to MQTT."""
    # Validate status
    if status.lower() not in ["yes", "no"]:
        print("❌ Invalid status. Use 'yes' or 'no'")
        return

    # Create event payload
    event_payload = {
        "type": "update",
        "status": status.lower(),
        "timestamp": datetime.now().isoformat(),
        "event_id": str(uuid.uuid4()),
    }

    # Connect to MQTT broker
    client = Client(client_id=f"test-publisher-{uuid.uuid4()}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"✓ Connected to MQTT broker at {host}:{port}")
            # Publish message
            result = client.publish(topic, json.dumps(event_payload))
            if result.rc == 0:
                print("✓ Published event successfully")
                print(f"  Type: {event_payload['type']}")
                print(f"  Status: {event_payload['status']}")
                print(f"  Timestamp: {event_payload['timestamp']}")
                print(f"  Event ID: {event_payload['event_id']}")
            else:
                print(f"❌ Failed to publish message (rc={result.rc})")
            client.disconnect()
        else:
            print(f"❌ Connection failed (rc={rc})")

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print(f"⚠ Unexpected disconnection: {rc}")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(host, port, keepalive=60)
        client.loop_start()
        # Give it time to publish
        import time

        time.sleep(2)
        client.loop_stop()
    except ConnectionRefusedError:
        print(f"❌ Could not connect to MQTT broker at {host}:{port}")
        print("   Make sure the MQTT broker is running")
    except Exception as e:
        print(f"❌ Error: {e}")


def interactive_mode():
    """Interactive mode for publishing events."""
    print("\n🎯 Face Recognition Event Publisher (Interactive Mode)")
    print("=" * 50)

    while True:
        print("\nOptions:")
        print("  1. Publish 'yes' (face recognized)")
        print("  2. Publish 'no' (face not recognized)")
        print("  3. Exit")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            publish_recognition_event(status="yes")
        elif choice == "2":
            publish_recognition_event(status="no")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode
        status = sys.argv[1].lower()
        publish_recognition_event(status=status)
    else:
        # Interactive mode
        interactive_mode()
