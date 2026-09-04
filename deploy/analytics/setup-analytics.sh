#!/usr/bin/env bash
#
# Visitor statistics for lukashensel.com.
#
# Reads nginx's own access log with GoAccess and publishes a password-protected
# report at https://lukashensel.com/stats/. Nothing is added to the pages
# themselves: no JavaScript, no cookies, no third-party requests, so visitors
# inside mainland China are counted exactly like everyone else and nothing can
# be blocked by a firewall or an ad-blocker.
#
# Run as root on the web server. Safe to run again at any time.

set -euo pipefail

DOMAIN="${DOMAIN:-lukashensel.com}"
STATS_USER="${STATS_USER:-lukas}"
STATS_PASS="${STATS_PASS:-}"
TZ_NAME="${TZ_NAME:-Asia/Shanghai}"

# Optional weekly email digest. Leave MSMTP_CONFIG empty to skip it.
MSMTP_CONFIG="${MSMTP_CONFIG:-}"
MAIL_TO="${MAIL_TO:-}"
MAIL_FROM="${MAIL_FROM:-stats@$DOMAIN}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

STATS_DIR=/var/www/stats
DB_DIR=/var/lib/goaccess
CONF=/etc/goaccess/lukashensel.conf
SNIPPET=/etc/nginx/snippets/stats.conf
HTPASSWD=/etc/nginx/.stats_htpasswd
UPDATER=/usr/local/bin/update-stats
GEO_DB="$DB_DIR/GeoLite2-Country.mmdb"

say() { printf '\n== %s\n' "$1"; }

[ "$(id -u)" -eq 0 ] || { echo "This has to run as root."; exit 1; }
[ -n "$STATS_PASS" ] || { echo "Set STATS_PASS to the password you want for the stats page."; exit 1; }

# ---------------------------------------------------------------- install ---
say "Installing GoAccess"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq goaccess apache2-utils cron >/dev/null
systemctl enable --now cron >/dev/null 2>&1 || true
goaccess --version | head -1

# Not every build of GoAccess understands every option, and an unknown key in
# the config file is fatal, so ask this build what it supports.
supports() { goaccess --help 2>&1 | grep -q -- "--$1"; }

# ------------------------------------------------------------- access log ---
say "Locating the access log"
SITE_FILES=$(grep -rls "$DOMAIN" /etc/nginx/sites-enabled /etc/nginx/conf.d 2>/dev/null || true)
LOG=""
if [ -n "$SITE_FILES" ]; then
  LOG=$(grep -hs -E '^[[:space:]]*access_log[[:space:]]+/' $SITE_FILES 2>/dev/null \
        | awk '{print $2}' | tr -d ';' | head -1 || true)
fi
LOG="${LOG:-/var/log/nginx/access.log}"
echo "using $LOG"
[ -f "$LOG" ] || echo "note: $LOG does not exist yet; it will be picked up once nginx writes to it"

# -------------------------------------------------------- country lookups ---
mkdir -p "$DB_DIR" "$STATS_DIR"
if [ ! -s "$GEO_DB" ]; then
  say "Fetching the country lookup database"
  if curl -fsSL -m 90 -o "$GEO_DB.tmp" \
       https://raw.githubusercontent.com/P3TERX/GeoLite.mmdb/download/GeoLite2-Country.mmdb; then
    mv "$GEO_DB.tmp" "$GEO_DB"
    echo "installed"
  else
    rm -f "$GEO_DB.tmp"
    echo "could not download it; the report will simply leave out the country panel"
  fi
fi

# ------------------------------------------------------------ goaccess.conf --
say "Writing the GoAccess configuration"
mkdir -p /etc/goaccess
{
  echo "# Managed by deploy/analytics/setup-analytics.sh in the website repo."
  echo "log-format COMBINED"
  echo "persist true"
  echo "restore true"
  echo "db-path $DB_DIR"
  echo "html-report-title lukashensel.com"
  echo "no-progress true"
  echo "agent-list false"
  for ext in .css .js .svg .woff2 .woff .ttf .jpg .jpeg .png .ico .webp .map; do
    echo "static-file $ext"
  done
} > "$CONF"

# Older builds reject options they do not know, and one bad line makes GoAccess
# refuse to run at all, so add the nice-to-have settings one at a time and keep
# only the ones this build actually accepts.
SAMPLE='127.0.0.1 - - [01/Jan/2026:12:00:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
conf_works() {
  rm -rf /tmp/goaccess-check
  mkdir -p /tmp/goaccess-check
  printf '%s\n' "$SAMPLE" \
    | goaccess - --config-file="$CONF" --db-path=/tmp/goaccess-check \
        -o /tmp/goaccess-check/out.html >/dev/null 2>&1
}
try_option() {
  cp "$CONF" "$CONF.bak"
  echo "$1" >> "$CONF"
  if conf_works; then
    rm -f "$CONF.bak"
  else
    mv "$CONF.bak" "$CONF"
    echo "  skipped unsupported option: $1"
  fi
}

if ! conf_works; then
  echo "GoAccess will not accept even the basic configuration; stopping here."
  exit 1
fi
try_option "real-os true"
try_option "ignore-crawlers true"
try_option "anonymize-ip true"
try_option "tz $TZ_NAME"
if [ -s "$GEO_DB" ]; then try_option "geoip-database $GEO_DB"; fi
rm -rf /tmp/goaccess-check

# --------------------------------------------------------------- updater ----
say "Installing the hourly updater"
cat > "$UPDATER" <<UPD
#!/usr/bin/env bash
# Refreshes /var/www/stats/index.html from the nginx access log.
set -euo pipefail
LOG="$LOG"
CONF="$CONF"
OUT="$STATS_DIR/index.html"

files=()
if [ -f "\$LOG.1" ]; then files+=("\$LOG.1"); fi
if [ -f "\$LOG" ];   then files+=("\$LOG");   fi
if [ \${#files[@]} -eq 0 ]; then exit 0; fi

tmp=\$(mktemp /tmp/stats.XXXXXX.html)
if zcat -f "\${files[@]}" | goaccess - --config-file="\$CONF" -o "\$tmp"; then
  mv "\$tmp" "\$OUT"
  chmod 644 "\$OUT"
else
  rm -f "\$tmp"
  exit 1
fi
UPD
chmod 755 "$UPDATER"

cat > /etc/cron.d/site-stats <<'CRON'
# Rebuild the site statistics page twice an hour.
7,37 * * * * root /usr/local/bin/update-stats >/dev/null 2>&1
CRON
chmod 644 /etc/cron.d/site-stats

# ----------------------------------------------------------- weekly email ---
if [ -n "$MSMTP_CONFIG" ] && [ -n "$MAIL_TO" ] && [ -f "$HERE/site-digest.py" ]; then
  say "Setting up the weekly email digest"
  apt-get install -y -qq msmtp msmtp-mta ca-certificates >/dev/null

  printf '%s\n' "$MSMTP_CONFIG" > /etc/msmtprc
  chmod 600 /etc/msmtprc
  chown root:root /etc/msmtprc

  printf 'MAIL_TO=%s\nMAIL_FROM=%s\n' "$MAIL_TO" "$MAIL_FROM" > /etc/goaccess/digest.env
  chmod 600 /etc/goaccess/digest.env

  # The digest reports a fixed week, so it must not read from or write to the
  # cumulative database the dashboard keeps.
  grep -v -E '^(persist|restore|db-path) ' "$CONF" > /etc/goaccess/digest.conf

  install -m 755 "$HERE/site-digest.py" /usr/local/lib/site-digest.py
  sed "s|__LOG__|$LOG|" "$HERE/weekly-digest.sh" > /usr/local/bin/weekly-digest
  chmod 755 /usr/local/bin/weekly-digest

  cat > /etc/cron.d/site-stats-digest <<'CRON'
# Weekly traffic summary, Monday morning Beijing time.
CRON_TZ=Asia/Shanghai
0 8 * * 1 root /usr/local/bin/weekly-digest >/dev/null 2>&1
CRON
  chmod 644 /etc/cron.d/site-stats-digest
  echo "digest will go to $MAIL_TO every Monday at 08:00 Beijing time"
else
  echo
  echo "(no mail settings given, so the weekly email digest was not installed)"
fi

# ------------------------------------------------------------------ nginx ---
say "Backing up the nginx configuration"
BACKUP="/root/nginx-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
tar czf "$BACKUP" /etc/nginx 2>/dev/null || true
echo "$BACKUP"

say "Creating the password file"
if [ -f "$HTPASSWD" ]; then
  htpasswd -b "$HTPASSWD" "$STATS_USER" "$STATS_PASS" >/dev/null 2>&1
else
  htpasswd -bc "$HTPASSWD" "$STATS_USER" "$STATS_PASS" >/dev/null 2>&1
fi
chown root:www-data "$HTPASSWD" 2>/dev/null || true
chmod 640 "$HTPASSWD"

say "Adding the /stats/ location to nginx"
mkdir -p /etc/nginx/snippets
cat > "$SNIPPET" <<'SNIP'
# Password-protected visitor statistics. Included from the server block.
location = /stats { return 301 /stats/; }

location /stats/ {
    alias /var/www/stats/;
    index index.html;
    autoindex off;
    auth_basic "Site statistics";
    auth_basic_user_file /etc/nginx/.stats_htpasswd;
    add_header X-Robots-Tag "noindex, nofollow, noarchive" always;

    # Looking at the statistics should not itself show up in the statistics.
    access_log off;
}
SNIP

python3 - "$DOMAIN" <<'PY'
import glob, sys
domain = sys.argv[1]
include = "    include /etc/nginx/snippets/stats.conf;\n"
changed = []
for path in glob.glob('/etc/nginx/sites-enabled/*') + glob.glob('/etc/nginx/conf.d/*.conf'):
    try:
        text = open(path).read()
    except OSError:
        continue
    if domain not in text or 'snippets/stats.conf' in text:
        continue
    out = []
    for line in text.splitlines(keepends=True):
        out.append(line)
        stripped = line.strip()
        if stripped.startswith('server_name') and domain in stripped:
            out.append(include)
    new = ''.join(out)
    if new != text:
        open(path, 'w').write(new)
        changed.append(path)
print('edited: ' + (', '.join(changed) if changed else 'nothing (already in place?)'))
PY

if nginx -t; then
  systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null || nginx -s reload
  echo "nginx reloaded"
else
  echo "nginx rejected the new configuration; restoring the backup"
  tar xzf "$BACKUP" -C /
  systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null || nginx -s reload || true
  exit 1
fi

# --------------------------------------------------------- first full run ---
say "Building the first report from the logs already on disk"
chown -R www-data:www-data "$STATS_DIR"
chmod 755 "$STATS_DIR"
mapfile -t old < <(ls -1tr ${LOG}* 2>/dev/null || true)
if [ ${#old[@]} -gt 0 ]; then
  tmp=$(mktemp /tmp/stats.XXXXXX.html)
  if zcat -f "${old[@]}" | goaccess - --config-file="$CONF" -o "$tmp"; then
    mv "$tmp" "$STATS_DIR/index.html"
    chmod 644 "$STATS_DIR/index.html"
  else
    rm -f "$tmp"
    echo "GoAccess could not parse the log. If nginx uses a custom log_format,"
    echo "adjust the log-format line in $CONF."
  fi
else
  echo "no log files yet; the first report will appear within half an hour"
fi

say "Done"
echo "  https://$DOMAIN/stats/   user: $STATS_USER"
echo "  refreshed at :07 and :37 past the hour"
if [ -f /usr/local/bin/weekly-digest ]; then
  echo "  weekly email to $MAIL_TO, Mondays 08:00"
fi
echo "  config:  $CONF"
echo "  updater: $UPDATER"
