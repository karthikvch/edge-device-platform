import os
import socket
import time

import requests
import paho.mqtt.client as mqtt

EDP_URL = os.getenv("EDP_URL", "http://localhost:8000")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))

CA_CERT = "certs/ca/ca.crt"
CLIENT_CERT = "certs/devices/dev-001/device.crt"
CLIENT_KEY = "certs/devices/dev-001/device.key"


def register():
    response = requests.post(
        f"{EDP_URL}/api/v1/devices/register", timeout=10
    )
    response.raise_for_status()
    return response.json()


def claim(claim_code):
    response = requests.post(
        f"{EDP_URL}/api/v1/devices/claim",
        json={"claim_code": claim_code},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def heartbeat(device_id):
    response = requests.post(
        f"{EDP_URL}/api/v1/devices/heartbeat",
        json={"device_id": device_id},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def connect_mqtt(device_id):
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=device_id,
    )
    client.tls_set(
        ca_certs=CA_CERT,
        certfile=CLIENT_CERT,
        keyfile=CLIENT_KEY,
    )
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    return client


def main():
    print(f"Edge Agent starting on host: {socket.gethostname()}")

    registration = register()
    device_id = registration["device_id"]
    claim_code = registration["claim_code"]

    print(f"Device ID : {device_id}")
    print(f"Claim Code: {claim_code}")
    print()
    print("Claim the device using:")
    print(
        f'curl -X POST {EDP_URL}/api/v1/devices/claim '
        '-H "Content-Type: application/json" '
        f'-d \'{{"claim_code":"{claim_code}"}}\''
    )
    print()
    input("Press ENTER after claiming the device...")

    print("Claim result:", claim(claim_code))

    print("Connecting to MQTT using mTLS...")
    client = connect_mqtt(device_id)
    print("MQTT connected.")

    try:
        while True:
            result = heartbeat(device_id)
            print("Heartbeat:", result)
            time.sleep(10)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
