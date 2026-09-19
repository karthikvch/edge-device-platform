from pathlib import Path

import requests


def request_certificate(
    edp_url: str,
    device_id: str,
    csr_path: Path,
    certificate_path: Path,
    ca_certificate_path: Path,
) -> None:
    csr = csr_path.read_text()

    response = requests.post(
        f"{edp_url}/api/v1/devices/{device_id}/certificate",
        json={"csr": csr},
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    certificate_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ca_certificate_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    certificate_path.write_text(
        data["certificate"]
    )

    ca_certificate_path.write_text(
        data["ca_certificate"]
    )

    print(
        f"Certificate provisioned for {device_id}"
    )