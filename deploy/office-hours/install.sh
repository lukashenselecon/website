#!/usr/bin/env bash
# Install the booking service on the existing web server. Run as root after
# creating /etc/lukas-office-hours/office-hours.env and msmtprc as documented.
set -euo pipefail

SOURCE_ROOT="${1:?Pass the directory containing office_hours/}"
test "$(id -u)" -eq 0 || { echo "Run as root." >&2; exit 1; }
test -f "$SOURCE_ROOT/office_hours/app.py" || { echo "Booking source is missing." >&2; exit 1; }
test -s /etc/lukas-office-hours/office-hours.env || { echo "Create the private environment file first." >&2; exit 1; }
test -s /etc/lukas-office-hours/msmtprc || { echo "Create the private msmtp configuration first." >&2; exit 1; }
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || {
  echo "Python 3.10 or newer is required on the server." >&2; exit 1;
}

id officehours >/dev/null 2>&1 || useradd --system --home-dir /var/lib/lukas-office-hours --shell /usr/sbin/nologin officehours
install -d -m 700 -o officehours -g officehours /var/lib/lukas-office-hours /var/lib/lukas-office-hours/uploads
install -d -m 700 -o root -g root /etc/lukas-office-hours
chmod 600 /etc/lukas-office-hours/office-hours.env
chown root:root /etc/lukas-office-hours/office-hours.env
chmod 600 /etc/lukas-office-hours/msmtprc
chown officehours:officehours /etc/lukas-office-hours/msmtprc

apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-venv msmtp ca-certificates >/dev/null
install -d -m 755 -o root -g root /opt/lukas-office-hours
rm -rf /opt/lukas-office-hours/office_hours
cp -R "$SOURCE_ROOT/office_hours" /opt/lukas-office-hours/office_hours
chown -R root:root /opt/lukas-office-hours/office_hours
python3 -m venv /opt/lukas-office-hours/venv
/opt/lukas-office-hours/venv/bin/pip install --disable-pip-version-check -r /opt/lukas-office-hours/office_hours/requirements.txt

cat > /etc/systemd/system/lukas-office-hours.service <<'UNIT'
[Unit]
Description=Lukas Hensel office-hours booking service
After=network.target

[Service]
Type=simple
User=officehours
Group=officehours
WorkingDirectory=/opt/lukas-office-hours
EnvironmentFile=/etc/lukas-office-hours/office-hours.env
ExecStart=/opt/lukas-office-hours/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8765 --timeout 60 'office_hours.app:create_app()'
Restart=on-failure
RestartSec=3
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/lukas-office-hours

[Install]
WantedBy=multi-user.target
UNIT

cat > /etc/systemd/system/lukas-office-hours-digest.service <<'UNIT'
[Unit]
Description=Email Tuesday office-hours bookings to Lukas
After=network.target

[Service]
Type=oneshot
User=officehours
Group=officehours
WorkingDirectory=/opt/lukas-office-hours
EnvironmentFile=/etc/lukas-office-hours/office-hours.env
ExecStart=/opt/lukas-office-hours/venv/bin/python -m office_hours.digest
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/lukas-office-hours
UNIT

# Repeated attempts on Monday evening are safe: digest_log suppresses a second
# message after the first accepted send.
cat > /etc/systemd/system/lukas-office-hours-digest.timer <<'UNIT'
[Unit]
Description=Retry office-hours digest during Monday evening

[Timer]
OnCalendar=Mon *-*-* 21:00:00 Asia/Shanghai
OnCalendar=Mon *-*-* 21:15:00 Asia/Shanghai
OnCalendar=Mon *-*-* 21:30:00 Asia/Shanghai
OnCalendar=Mon *-*-* 22:00:00 Asia/Shanghai
OnCalendar=Mon *-*-* 23:00:00 Asia/Shanghai
Persistent=true
Unit=lukas-office-hours-digest.service

[Install]
WantedBy=timers.target
UNIT

install -d -m 755 /etc/nginx/snippets
cat > /etc/nginx/snippets/office-hours.conf <<'NGINX'
location ^~ /api/office-hours/ {
    client_max_body_size 32m;
    proxy_pass http://127.0.0.1:8765;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 60s;
}
NGINX

systemctl daemon-reload
systemctl enable --now lukas-office-hours.service lukas-office-hours-digest.timer
systemctl restart lukas-office-hours.service
systemctl is-active --quiet lukas-office-hours.service

cat <<'NEXT'
Booking service installed. Add this line inside the HTTPS server block for
lukashensel.com, then run nginx -t and reload nginx:

    include /etc/nginx/snippets/office-hours.conf;

Do not add the line twice. Test the live API and Monday email as described in
deploy/office-hours/README.md before publishing the static sign-up page.
NEXT
