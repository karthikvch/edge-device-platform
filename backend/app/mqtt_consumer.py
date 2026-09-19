import json
import os
import ssl
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import psycopg


DATABASE_URL = os.getenv(
    "EDP_DATABASE_URL",
    "postgresql://edp:edp@postgres:5432/edp",
)

MQTT_HOST = os.getenv(
    "EDP_MQTT_HOST",
    "mosquitto",
)

MQTT_PORT = int(
    os.getenv(
        "EDP_MQTT_PORT",
        "8883",
    )
)

MQTT_CA = os.getenv(
    "EDP_MQTT_CA",
    "/app/certs/mqtt/ca.crt",
)

MQTT_CERT = os.getenv(
    "EDP_MQTT_CERT",
    "/app/certs/mqtt/backend.crt",
)

MQTT_KEY = os.getenv(
    "EDP_MQTT_KEY",
    "/app/certs/mqtt/backend.key",
)

MQTT_TOPIC = "edp/devices/+/heartbeat"


def update_device_heartbeat(
    device_id: str,
) -> None:
    now = datetime.now(timezone.utc)

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE devices
                SET
                    status = %s,
                    last_seen = %s
                WHERE device_id = %s
                """,
                (
                    "ONLINE",
                    now,
                    device_id,
                ),
            )

            if cursor.rowcount == 0:
                print(
                    f"Unknown device heartbeat: {device_id}"
                )
                return

        conn.commit()

    print(
        f"Device {device_id} is ONLINE "
        f"at {now.isoformat()}"
    )


def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties,
):
    print(
        f"Connected to MQTT broker: {reason_code}"
    )

    client.subscribe(MQTT_TOPIC)

    print(
        f"Subscribed to: {MQTT_TOPIC}"
    )


def on_message(
    client,
    userdata,
    message,
):
    print(
        f"MQTT message received: "
        f"{message.topic}"
    )

    try:
        payload = json.loads(
            message.payload.decode("utf-8")
        )

        device_id = payload.get("device_id")

        if not device_id:
            print("Heartbeat missing device_id")
            return

        update_device_heartbeat(device_id)

    except json.JSONDecodeError:
        print("Invalid JSON heartbeat")

    except Exception as exc:
        print(
            f"Failed to process heartbeat: {exc}"
        )


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="edp-backend",
    )

    client.tls_set(
        ca_certs=MQTT_CA,
        certfile=MQTT_CERT,
        keyfile=MQTT_KEY,
        tls_version=ssl.PROTOCOL_TLS_CLIENT,
    )

    client.on_connect = on_connect
    client.on_message = on_message

    print(
        f"Connecting to MQTT "
        f"{MQTT_HOST}:{MQTT_PORT}"
    )

    client.connect(
        host="mosquitto",
        port=MQTT_PORT,
        keepalive=60,
    )

    client.loop_forever()


if __name__ == "__main__":
    main()