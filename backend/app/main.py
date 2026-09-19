import os
import time
from datetime import datetime, timezone

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.certificate_service import (
    issue_device_certificate,
)

class CertificateRequest(BaseModel):
    csr: str

DATABASE_URL = os.getenv(
    "EDP_DATABASE_URL",
    "postgresql://edp:edp@postgres:5432/edp",
)

app = FastAPI(
    title="Edge Device Platform",
    version="0.1.0",
)


def get_db():
    return psycopg.connect(DATABASE_URL)


def init_db():
    for attempt in range(10):
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS devices (
                            id SERIAL PRIMARY KEY,
                            device_id VARCHAR(100) UNIQUE NOT NULL,
                            device_type VARCHAR(100) NOT NULL,
                            status VARCHAR(30) NOT NULL,
                            claim_code VARCHAR(100) UNIQUE NOT NULL,
                            claimed_at TIMESTAMPTZ,
                            last_seen TIMESTAMPTZ,
                            created_at TIMESTAMPTZ NOT NULL
                        )
                        """
                    )
                conn.commit()

            print("Database initialized successfully.")
            return

        except psycopg.OperationalError as exc:
            print(
                f"Database not ready "
                f"(attempt {attempt + 1}/10): {exc}"
            )
            time.sleep(2)

    raise RuntimeError("Could not connect to PostgreSQL")


init_db()


class ClaimRequest(BaseModel):
    claim_code: str


class HeartbeatRequest(BaseModel):
    device_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/devices/register")
def register_device():
    import secrets

    device_id = f"dev-{secrets.token_hex(4)}"
    claim_code = secrets.token_hex(3).upper()
    now = datetime.now(timezone.utc)

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO devices
                (
                    device_id,
                    device_type,
                    status,
                    claim_code,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    device_id,
                    "linux-edge",
                    "UNCLAIMED",
                    claim_code,
                    now,
                ),
            )

        conn.commit()

    return {
        "device_id": device_id,
        "claim_code": claim_code,
        "status": "UNCLAIMED",
    }


@app.post("/api/v1/devices/claim")
def claim_device(request: ClaimRequest):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    device_id,
                    status
                FROM devices
                WHERE claim_code = %s
                """,
                (request.claim_code.upper(),),
            )

            device = cursor.fetchone()

            if device is None:
                raise HTTPException(
                    status_code=404,
                    detail="Invalid claim code",
                )

            device_id, status = device

            if status != "UNCLAIMED":
                raise HTTPException(
                    status_code=409,
                    detail="Device has already been claimed",
                )

            now = datetime.now(timezone.utc)

            cursor.execute(
                """
                UPDATE devices
                SET
                    status = %s,
                    claimed_at = %s
                WHERE device_id = %s
                """,
                (
                    "CLAIMED",
                    now,
                    device_id,
                ),
            )

        conn.commit()

    return {
        "device_id": device_id,
        "status": "CLAIMED",
    }


@app.post("/api/v1/devices/heartbeat")
def heartbeat(request: HeartbeatRequest):
    now = datetime.now(timezone.utc)

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT device_id
                FROM devices
                WHERE device_id = %s
                """,
                (request.device_id,),
            )

            device = cursor.fetchone()

            if device is None:
                raise HTTPException(
                    status_code=404,
                    detail="Unknown device",
                )

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
                    request.device_id,
                ),
            )

        conn.commit()

    return {
        "device_id": request.device_id,
        "status": "ONLINE",
        "last_seen": now.isoformat(),
    }


@app.get("/api/v1/devices")
def list_devices():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    device_id,
                    device_type,
                    status,
                    claim_code,
                    claimed_at,
                    last_seen,
                    created_at
                FROM devices
                ORDER BY id
                """
            )

            rows = cursor.fetchall()

    return [
        {
            "device_id": row[0],
            "device_type": row[1],
            "status": row[2],
            "claim_code": row[3],
            "claimed_at": row[4],
            "last_seen": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]
@app.post("/api/v1/devices/{device_id}/certificate")
def provision_certificate(
    device_id: str,
    request: CertificateRequest,
):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT device_id, status
                FROM devices
                WHERE device_id = %s
                """,
                (device_id,),
            )

            device = cursor.fetchone()

            if device is None:
                raise HTTPException(
                    status_code=404,
                    detail="Device not found",
                )

            _, status = device

            if status != "CLAIMED":
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Device must be CLAIMED "
                        "before certificate provisioning"
                    ),
                )

    try:
        certificate = issue_device_certificate(
            device_id=device_id,
            csr_pem=request.csr,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    issued_at = certificate["issued_at"]
    expires_at = certificate["expires_at"]
    serial = certificate["serial"]

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE devices
                SET
                    status = %s,
                    certificate_serial = %s,
                    certificate_issued_at = %s,
                    certificate_expires_at = %s
                WHERE device_id = %s
                """,
                (
                    "CERTIFICATE_PROVISIONED",
                    serial,
                    issued_at,
                    expires_at,
                    device_id,
                ),
            )

        conn.commit()

    return {
        "device_id": device_id,
        "status": "CERTIFICATE_PROVISIONED",
        "certificate": certificate["certificate"],
        "ca_certificate": certificate["ca_certificate"],
        "certificate_serial": serial,
        "certificate_issued_at": issued_at,
        "certificate_expires_at": expires_at,
    }