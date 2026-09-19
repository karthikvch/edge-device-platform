# Edge Device Platform (EDP) — Phase 1

Goal: Claim Code -> Device Identity -> MQTT TLS authentication -> Heartbeat -> ONLINE

This is a local MVP. AWS is not required.

target is:

Claim Code → Device Identity → MQTT mTLS → Heartbeat → ONLINE

## Phase 1 Architecture — Local Machine

Below is the Phase 1 architecture for local development (monospace diagram):

```text
                        LOCAL MACHINE
  ┌──────────────────────────────────────────────────────────────┐
  │                         EDP Backend (FastAPI)               │
  │  ┌──────────────────────┬──────────────────────┬───────────┐│
  │  │ Device Registry      │ Claim Service        │ Cert svc  ││
  │  └──────────────────────┴──────────────────────┴───────────┘│
  │                              │                                │
  │                          Certificate Service                  │
  │                              │                                │
  │                          Mosquitto (MQTT/TLS)                 │
  └──────────────────────────────┼─────────────────────────────────┘
                                 │
                               MQTT
                                 │
                    ┌────────────▼───────────┐
                    │      Edge Agent        │
                    │     (Linux device)     │
                    └────────────────────────┘
```

You can run the backend, database and MQTT broker locally with Docker Compose.


## Stack
- FastAPI
- PostgreSQL (local MVP registry)
- Mosquitto MQTT
- Python Edge Agent
- OpenSSL development CA
- Docker Compose

## Run

Prerequisites: Docker Compose, Python 3.11+, OpenSSL, curl.

1. Generate development certificates:
```bash
./scripts/generate-certs.sh
```

Note: the script places broker/server certificates under `certs/server/` and device certificates under `certs/devices/`. The compose configuration expects the broker/server certificate and key at `certs/server/server.crt` and `certs/server/server.key`.

2. Start services:
```bash
docker compose up -d --build
```

3. Create the agent environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r agent/requirements.txt
```

4. Start the agent:
```bash
python -m agent.edp_agent.main
```

5. The agent prints a claim code. In another terminal, use the printed curl command.

6. Check devices:
```bash
curl http://localhost:8000/api/v1/devices
```

## Important
The certificate flow in this first repository is intentionally a development scaffold. The next production step is to implement real certificate issuance and bind MQTT certificate identities to device identities. Do not use the generated private keys or this CA process in production.

## Phase 1 Definition of Done
- Unique device identity
- Claim code
- Device claim
- MQTT TLS/mTLS
- Heartbeat
- ONLINE status
- last_seen
