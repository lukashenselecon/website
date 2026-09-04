#!/usr/bin/env bash
#
# Emails a short weekly summary of site traffic.
# Installed by setup-analytics.sh; recipients live in /etc/goaccess/digest.env
# and the mail account in /etc/msmtprc.

set -uo pipefail

CONF=/etc/goaccess/digest.conf
ENV_FILE=/etc/goaccess/digest.env
LOG=__LOG__

[ -r "$ENV_FILE" ] || { echo "no $ENV_FILE; nothing to send"; exit 0; }
# shellcheck disable=SC1090
. "$ENV_FILE"

WORK=$(mktemp -d /tmp/digest.XXXXXX)
trap 'rm -rf "$WORK"' EXIT

days_ago() {  # the log-style date N days back
  date -d "$1 days ago" +'%d/%b/%Y' 2>/dev/null || date -v-"$1"d +'%d/%b/%Y'
}

: > "$WORK/this"; : > "$WORK/prev"
for d in 1 2 3 4 5 6 7;      do days_ago "$d" >> "$WORK/this"; done
for d in 8 9 10 11 12 13 14; do days_ago "$d" >> "$WORK/prev"; done

zcat -f ${LOG}* 2>/dev/null > "$WORK/all.log" || true
[ -s "$WORK/all.log" ] || { echo "no log data"; exit 0; }

grep -F -f "$WORK/this" "$WORK/all.log" > "$WORK/this.log" || true
grep -F -f "$WORK/prev" "$WORK/all.log" > "$WORK/prev.log" || true

if [ ! -s "$WORK/this.log" ]; then
  echo "no traffic in the last seven days; nothing to send"
  exit 0
fi

report() {  # $1 = log file, $2 = json out
  [ -s "$1" ] || return 1
  rm -rf "$WORK/db"; mkdir -p "$WORK/db"
  goaccess "$1" --config-file="$CONF" --db-path="$WORK/db" -o "$2" >/dev/null 2>&1
}

report "$WORK/this.log" "$WORK/this.json" || { echo "goaccess failed"; exit 1; }
report "$WORK/prev.log" "$WORK/prev.json" || true

python3 /usr/local/lib/site-digest.py "$WORK/this.json" "$WORK/prev.json" > "$WORK/body.txt" || exit 1

SUBJECT=$(head -1 "$WORK/body.txt")
{
  echo "From: $MAIL_FROM"
  echo "To: $MAIL_TO"
  echo "Subject: $SUBJECT"
  echo "MIME-Version: 1.0"
  echo "Content-Type: text/plain; charset=utf-8"
  echo
  tail -n +2 "$WORK/body.txt"
} | msmtp --file=/etc/msmtprc "$MAIL_TO"
