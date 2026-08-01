# Phase 1 — Start with Onboarding

Before OTA, let's establish the platform foundation.

```text
                         EDP
                  ┌───────────────┐
                  │ React Console │
                  └───────┬───────┘
                          │ REST
                  ┌───────▼───────┐
                  │  Spring Boot  │
                  │    Backend    │
                  └───┬───────┬───┘
                      │       │
               PostgreSQL   AWS IoT Core
                              │
                            MQTT
                              │
                       ┌──────▼──────┐
                       │ Python Agent│
                       └─────────────┘
```

## Architecture recommendation

I recommend a modular monolith, not microservices, for the MVP.

A sensible repository structure is:

```
edge-device-platform/
├── backend/
│   ├── src/
│   ├── pom.xml
│   └── Dockerfile
│
├── agent/
│   ├── src/
│   ├── tests/
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   └── package.json
│
├── infrastructure/
│   ├── docker/
│   └── terraform/          # later
│
├── docs/
│   ├── architecture/
│   ├── api/
│   └── decisions/
│
├── docker-compose.yml
└── README.md
```

## Backend module organization

Inside Spring Boot, keep domain boundaries clear even though they're in one application:

```
com.edp.platform
├── device
│   ├── api
│   ├── application
│   ├── domain
│   └── infrastructure
│
├── onboarding
├── ota
├── monitoring
├── command
├── identity
└── common
```

This makes it much easier to extract a module into a microservice later if there's a real reason.

## Sprint 1 — first vertical slice

Your first vertical slice should be:

- Create Device
- Generate onboarding information
- Agent starts
- Agent authenticates
- Connect AWS IoT Core
- Publish heartbeat
- Backend receives status
- Device becomes ONLINE

## First REST endpoints

- `POST /api/v1/devices`
- `GET /api/v1/devices`
- `GET /api/v1/devices/{deviceId}`

And initially only two MQTT topics are enough:

- `edp/devices/{deviceId}/heartbeat`
- `edp/devices/{deviceId}/status`

Don't design 30 topics yet.

## First database model

Start with one important table:

```
device
--------------------------------
id                  UUID
device_id           VARCHAR
name                VARCHAR
status              ENUM
software_version    VARCHAR
last_seen_at        TIMESTAMP
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

Later we'll add certificates, device groups, OTA campaigns, jobs, telemetry, etc.

## First milestone

I wouldn't even build the React dashboard immediately.

First prove:

- Python Agent
- AWS IoT Core
- Spring Boot
- PostgreSQL

Agent sends:

```json
{
  "deviceId": "edge-001",
  "timestamp": "2026-08-01T10:30:00Z",
  "version": "1.0.0",
  "status": "ONLINE"
}
```

and Spring Boot successfully persists/updates the device state.

Once that works end-to-end, we have the foundation for OTA.

Then we move in this order:

- Onboarding → OTA → Monitoring → Remote Operations
