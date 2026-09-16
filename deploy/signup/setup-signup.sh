#!/usr/bin/env bash
#
# Sign-up forms for lukashensel.com.
#
# Installs a small Python service (standard library only) that receives the
# form on /cycling and saves the answers on the server, plus a
# password-protected list at https://lukashensel.com/signups/ that uses the
# same login as /stats/. Nothing leaves the server and nothing on the page
# needs JavaScript or a third-party service, so it works in mainland China.
#
# Run as root on the web server. Safe to run again at any time; existing
# sign-ups are kept.

set -euo pipefail

DOMAIN="${DOMAIN:-lukashensel.com}"
STATS_USER="${STATS_USER:-lukas}"
STATS_PASS="${STATS_PASS:-}"
PORT=8790
HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
HTPASSWD=/etc/nginx/.stats_htpasswd
SNIPPET=/etc/nginx/snippets/signup.conf
ZONE=/etc/nginx/conf.d/signup-ratelimit.conf

say() { printf '\n== %s\n' "$1"; }
[ "$(id -u)" -eq 0 ] || { echo "This has to run as root."; exit 1; }
command -v python3 >/dev/null || { apt-get update -qq; apt-get install -y -qq python3 >/dev/null; }

say "Installing the service"
install -m 755 "$HERE/signup-server.py" /usr/local/lib/signup-server.py
cat > /etc/systemd/system/site-signup.service <<UNIT
[Unit]
Description=Sign-up forms for $DOMAIN
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/lib/signup-server.py
Environment=SIGNUP_DIR=/var/lib/signup SIGNUP_PORT=$PORT PYTHONUNBUFFERED=1
DynamicUser=yes
StateDirectory=signup
Restart=always
RestartSec=2
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
MemoryMax=64M

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable site-signup >/dev/null 2>&1
systemctl restart site-signup
sleep 1
systemctl is-active site-signup

say "Backing up the nginx configuration"
BACKUP="/root/nginx-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
tar czf "$BACKUP" /etc/nginx 2>/dev/null || true
echo "$BACKUP"

say "Password for /signups/"
if [ -n "$STATS_PASS" ]; then
  command -v htpasswd >/dev/null || apt-get install -y -qq apache2-utils >/dev/null
  if [ -f "$HTPASSWD" ]; then
    htpasswd -b "$HTPASSWD" "$STATS_USER" "$STATS_PASS" >/dev/null 2>&1
  else
    htpasswd -bc "$HTPASSWD" "$STATS_USER" "$STATS_PASS" >/dev/null 2>&1
  fi
  chown root:www-data "$HTPASSWD" 2>/dev/null || true
  chmod 640 "$HTPASSWD"
  echo "set for user $STATS_USER"
elif [ -f "$HTPASSWD" ]; then
  echo "reusing the /stats/ login"
else
  echo "No password file yet. Add the STATS_PASSWORD repository secret and run again."
  exit 1
fi

say "Adding the locations to nginx"
# Rate limiting needs a zone in the http block. Debian and Ubuntu load
# conf.d/*.conf there; if this server does not, skip the limit.
LIMIT=""
if nginx -T 2>/dev/null | grep -qE 'include[[:space:]]+/etc/nginx/conf\.d/\*\.conf'; then
  echo 'limit_req_zone $binary_remote_addr zone=signup:1m rate=10r/m;' > "$ZONE"
  LIMIT="    limit_req zone=signup burst=5 nodelay;"
fi
mkdir -p /etc/nginx/snippets
cat > "$SNIPPET" <<SNIP
# Sign-up forms (deploy/signup in the website repo). Included from the server block.
location ^~ /api/signup/ {
    limit_except POST { deny all; }
$LIMIT
    client_max_body_size 16k;
    proxy_pass http://127.0.0.1:$PORT;
    proxy_set_header X-Real-IP \$remote_addr;
}

location = /signups { return 301 /signups/; }

location ^~ /signups/ {
    auth_basic "Sign-ups";
    auth_basic_user_file $HTPASSWD;
    add_header X-Robots-Tag "noindex, nofollow, noarchive" always;
    proxy_pass http://127.0.0.1:$PORT;
    access_log off;
}
SNIP

python3 - "$DOMAIN" <<'PY'
import glob, sys
domain = sys.argv[1]
include = "    include /etc/nginx/snippets/signup.conf;\n"
changed = []
for path in glob.glob('/etc/nginx/sites-enabled/*') + glob.glob('/etc/nginx/conf.d/*.conf'):
    try:
        text = open(path).read()
    except OSError:
        continue
    if domain not in text or 'snippets/signup.conf' in text:
        continue
    out = []
    for line in text.splitlines(keepends=True):
        out.append(line)
        s = line.strip()
        if s.startswith('server_name') and domain in s:
            out.append(include)
    new = ''.join(out)
    if new != text:
        open(path, 'w').write(new)
        changed.append(path)
print('edited: ' + (', '.join(changed) if changed else 'nothing (already in place?)'))
PY

if nginx -t; then
  systemctl reload nginx 2>/dev/null || nginx -s reload
  echo "nginx reloaded"
else
  echo "nginx rejected the new configuration; restoring the backup"
  rm -f "$ZONE"
  tar xzf "$BACKUP" -C /
  systemctl reload nginx 2>/dev/null || nginx -s reload || true
  exit 1
fi

say "Checking"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
       --data 'website=bot' -H "Host: $DOMAIN" http://127.0.0.1/api/signup/cycling || true)
echo "form endpoint answered $code (303 or 301 is fine)"

say "Done"
echo "  form:     https://$DOMAIN/cycling"
echo "  list:     https://$DOMAIN/signups/   (same login as /stats/)"
echo "  data:     /var/lib/signup/cycling.csv"
echo "  logs:     journalctl -u site-signup"
