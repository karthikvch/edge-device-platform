#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERT_DIR="$ROOT/certs"

mkdir -p "$CERT_DIR/ca" "$CERT_DIR/server" "$CERT_DIR/devices/dev-001"

openssl genrsa -out "$CERT_DIR/ca/ca.key" 4096
openssl req -x509 -new -nodes -key "$CERT_DIR/ca/ca.key"   -sha256 -days 365 -out "$CERT_DIR/ca/ca.crt"   -subj "/CN=EDP Development CA"

openssl genrsa -out "$CERT_DIR/server/server.key" 2048
openssl req -new -key "$CERT_DIR/server/server.key"   -out "$CERT_DIR/server/server.csr" -subj "/CN=localhost"

cat > "$CERT_DIR/server/server.ext" <<EOF
subjectAltName=DNS:localhost,IP:127.0.0.1
extendedKeyUsage=serverAuth
EOF

openssl x509 -req -in "$CERT_DIR/server/server.csr"   -CA "$CERT_DIR/ca/ca.crt" -CAkey "$CERT_DIR/ca/ca.key"   -CAcreateserial -out "$CERT_DIR/server/server.crt"   -days 365 -sha256 -extfile "$CERT_DIR/server/server.ext"

openssl genrsa -out "$CERT_DIR/devices/dev-001/device.key" 2048
openssl req -new -key "$CERT_DIR/devices/dev-001/device.key"   -out "$CERT_DIR/devices/dev-001/device.csr" -subj "/CN=dev-001"

cat > "$CERT_DIR/devices/dev-001/device.ext" <<EOF
extendedKeyUsage=clientAuth
EOF

openssl x509 -req -in "$CERT_DIR/devices/dev-001/device.csr"   -CA "$CERT_DIR/ca/ca.crt" -CAkey "$CERT_DIR/ca/ca.key"   -CAcreateserial -out "$CERT_DIR/devices/dev-001/device.crt"   -days 365 -sha256 -extfile "$CERT_DIR/devices/dev-001/device.ext"

rm -f "$CERT_DIR/server/server.csr" "$CERT_DIR/server/server.ext"
rm -f "$CERT_DIR/devices/dev-001/device.csr" "$CERT_DIR/devices/dev-001/device.ext"
rm -f "$CERT_DIR/ca/ca.srl"

echo "Development certificates generated."
