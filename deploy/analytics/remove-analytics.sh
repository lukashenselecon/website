#!/usr/bin/env bash
#
# Undoes setup-analytics.sh. Run as root on the web server.
# The site itself is untouched.

set -uo pipefail
DOMAIN="${DOMAIN:-lukashensel.com}"

[ "$(id -u)" -eq 0 ] || { echo "This has to run as root."; exit 1; }

tar czf "/root/nginx-backup-$(date +%Y%m%d-%H%M%S).tar.gz" /etc/nginx 2>/dev/null || true

sed -i '/snippets\/stats.conf/d' /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*.conf 2>/dev/null || true
rm -f /etc/nginx/snippets/stats.conf /etc/nginx/.stats_htpasswd /etc/msmtprc
rm -f /etc/cron.d/site-stats /etc/cron.d/site-stats-digest
rm -f /usr/local/bin/update-stats /usr/local/bin/weekly-digest
rm -f /usr/local/lib/site-digest.py
rm -f /etc/goaccess/lukashensel.conf /etc/goaccess/digest.conf /etc/goaccess/digest.env
rm -rf /var/www/stats /var/lib/goaccess

if nginx -t; then
  systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null || nginx -s reload
  echo "Removed. GoAccess itself is still installed; 'apt-get remove goaccess' takes it out."
else
  echo "nginx configuration test failed. Restore one of /root/nginx-backup-*.tar.gz"
  exit 1
fi
