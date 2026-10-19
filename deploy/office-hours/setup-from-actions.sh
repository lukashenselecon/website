#!/usr/bin/env bash
# The manual GitHub Actions workflow transfers the admin password to a private
# staging directory on the server; this script never prints its contents.
set -euo pipefail
umask 077

SOURCE_ROOT="${1:?Source directory is required}"
PASSWORD_FILE="${2:?Admin password file is required}"
CONFIG_DIR=/etc/lukas-office-hours
ENV_FILE="$CONFIG_DIR/office-hours.env"

test "$(id -u)" -eq 0 || { echo "Run as root." >&2; exit 1; }
test -s "$PASSWORD_FILE" || { echo "The admin password secret is missing." >&2; exit 1; }
test -f "$SOURCE_ROOT/office_hours/app.py" || { echo "Booking source is missing." >&2; exit 1; }
trap 'rm -f "$PASSWORD_FILE"' EXIT

python3 - "$PASSWORD_FILE" <<'PY'
from pathlib import Path
import sys
password = Path(sys.argv[1]).read_bytes()
if len(password) < 20 or b'\n' in password or b'\r' in password:
    raise SystemExit('OFFICE_HOURS_ADMIN_PASSWORD must have at least 20 characters and no line breaks.')
PY

install -d -m 700 -o root -g root "$CONFIG_DIR"
signing_key=""
if [ -f "$ENV_FILE" ]; then
    signing_key=$(sed -n 's/^OFFICE_HOURS_SIGNING_KEY=//p' "$ENV_FILE" | head -n 1)
fi
if [ "${#signing_key}" -lt 32 ]; then
    signing_key=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
fi
admin_password_b64=$(base64 -w0 < "$PASSWORD_FILE")
cat > "$ENV_FILE" <<EOF
OFFICE_HOURS_SIGNING_KEY=$signing_key
OFFICE_HOURS_ADMIN_USER=lukas
OFFICE_HOURS_ADMIN_PASSWORD_B64=$admin_password_b64
OFFICE_HOURS_DB=/var/lib/lukas-office-hours/bookings.sqlite3
OFFICE_HOURS_UPLOAD_DIR=/var/lib/lukas-office-hours/uploads
EOF
chmod 600 "$ENV_FILE"
chown root:root "$ENV_FILE"

bash "$SOURCE_ROOT/deploy/office-hours/install.sh" "$SOURCE_ROOT"
python3 "$SOURCE_ROOT/deploy/office-hours/configure-nginx.py"

status=""
for ((attempt = 1; attempt <= 20; attempt++)); do
    status=$(curl --connect-timeout 2 --max-time 3 -s -o /dev/null -w '%{http_code}' \
        -X POST -H 'Content-Type: application/json' -d '{}' \
        http://127.0.0.1:8765/api/office-hours/slots) || status=""
    if [ "$status" = 401 ]; then
        break
    fi
    sleep 1
done
if [ "$status" != 401 ]; then
    echo "Local API did not become ready (last HTTP status: ${status:-connection failed})." >&2
    systemctl status lukas-office-hours.service --no-pager -l >&2 || true
    journalctl -u lukas-office-hours.service -n 60 --no-pager >&2 || true
    exit 1
fi

echo "Booking API is running. The private owner report is ready for the app task."
