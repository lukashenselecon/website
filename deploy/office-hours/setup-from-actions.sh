#!/usr/bin/env bash
# The manual GitHub Actions workflow transfers these inputs to a private
# staging directory on the server; this script never prints their contents.
set -euo pipefail
umask 077

SOURCE_ROOT="${1:?Source directory is required}"
PASSWORD_FILE="${2:?Admin password file is required}"
MSMTP_FILE="${3:-}"
CONFIG_DIR=/etc/lukas-office-hours
ENV_FILE="$CONFIG_DIR/office-hours.env"
MAIL_FILE="$CONFIG_DIR/msmtprc"

test "$(id -u)" -eq 0 || { echo "Run as root." >&2; exit 1; }
test -s "$PASSWORD_FILE" || { echo "The admin password secret is missing." >&2; exit 1; }
test -f "$SOURCE_ROOT/office_hours/app.py" || { echo "Booking source is missing." >&2; exit 1; }
trap 'rm -f "$PASSWORD_FILE"; if [ -n "$MSMTP_FILE" ]; then rm -f "$MSMTP_FILE"; fi' EXIT

python3 - "$PASSWORD_FILE" <<'PY'
from pathlib import Path
import sys
password = Path(sys.argv[1]).read_bytes()
if len(password) < 20 or b'\n' in password or b'\r' in password:
    raise SystemExit('OFFICE_HOURS_ADMIN_PASSWORD must have at least 20 characters and no line breaks.')
PY

install -d -m 700 -o root -g root "$CONFIG_DIR"
if [ -n "$MSMTP_FILE" ] && [ -s "$MSMTP_FILE" ]; then
    mail_source="$MSMTP_FILE"
elif [ -s "$MAIL_FILE" ]; then
    mail_source="$MAIL_FILE"
elif [ -s /etc/msmtprc ]; then
    mail_source=/etc/msmtprc
else
    echo "No mail configuration found. Set the MSMTP_CONFIG repository secret, then rerun." >&2
    exit 1
fi

# The analytics mail configuration can log to a root-owned path. This copy is
# used by the dedicated officehours account, so omit that optional setting.
mail_tmp=$(mktemp)
awk '$1 != "logfile" { print }' "$mail_source" > "$mail_tmp"
sender=$(awk '$1 == "from" { print $2; exit }' "$mail_tmp")
if [[ ! "$sender" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$ ]]; then
    rm -f "$mail_tmp"
    echo "The msmtp configuration needs a valid 'from' address." >&2
    exit 1
fi
install -m 600 -o root -g root "$mail_tmp" "$MAIL_FILE"
rm -f "$mail_tmp"

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
OFFICE_HOURS_MAIL_FROM=$sender
OFFICE_HOURS_MAIL_TO=lukas.hensel@gsm.pku.edu.cn
OFFICE_HOURS_MSMTP_CONFIG=$MAIL_FILE
EOF
chmod 600 "$ENV_FILE"
chown root:root "$ENV_FILE"

bash "$SOURCE_ROOT/deploy/office-hours/install.sh" "$SOURCE_ROOT"
python3 "$SOURCE_ROOT/deploy/office-hours/configure-nginx.py"

status=$(curl -sS -o /dev/null -w '%{http_code}' \
    -X POST -H 'Content-Type: application/json' -d '{}' \
    http://127.0.0.1:8765/api/office-hours/slots)
test "$status" = 401 || { echo "Local API check returned $status, expected 401." >&2; exit 1; }

printf 'From: %s\nTo: lukas.hensel@gsm.pku.edu.cn\nSubject: Office-hours email test\n\nThe Monday office-hours email account is configured.\n' "$sender" \
    | runuser -u officehours -- msmtp --file="$MAIL_FILE" lukas.hensel@gsm.pku.edu.cn
echo "Booking API is running and a test message was sent to Lukas. Check the inbox."
