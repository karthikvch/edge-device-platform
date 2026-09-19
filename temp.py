python3 - <<'PY'
from pathlib import Path
import sys

sys.path.insert(0, "agent")

from edp_agent.identity import (
    generate_private_key,
    save_private_key,
    generate_csr,
)

device_id = "dev-f87080d8"

key = generate_private_key()

path = Path("/tmp/edp-device/device.key")

save_private_key(key, path)

csr = generate_csr(key, device_id)

Path("/tmp/edp-device/device.csr").write_bytes(csr)

print("Private key:", path)
print("CSR: /tmp/edp-device/device.csr")
PY
