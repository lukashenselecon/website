# Visitor statistics

The site's numbers come from nginx's own access log, read by
[GoAccess](https://goaccess.io/), and are published as a password-protected
page at **https://lukashensel.com/stats/**, with a short summary emailed every
Monday morning.

Nothing is added to the pages themselves. There is no tracking script, no
cookie, no request to any other company's server. That matters for three
reasons: visitors in mainland China are counted exactly like everyone else
(Google Analytics is blocked there, so it would have shown a large part of the
audience as nonexistent), nothing slows the pages down or can be blocked by an
ad-blocker, and no visitor data leaves the server, so no cookie banner is
needed. IP addresses are anonymised before they are stored.

## What is in the report

Visitors and pageviews by day, which pages and which paper PDFs were opened
and how often, where people came from (search, Twitter/X, Scholar, a
university page), countries, browsers and operating systems, and any broken
links people hit.

Known crawlers are excluded, so the figures are closer to real readers than a
raw log count. They are still approximate: a person switching between phone
and laptop counts twice, and a crawler with an honest-looking user agent slips
through.

## How it runs

| Piece | Where |
| --- | --- |
| GoAccess settings | `/etc/goaccess/lukashensel.conf` |
| Refresh script | `/usr/local/bin/update-stats` (cron, at :07 and :37) |
| Accumulated history | `/var/lib/goaccess/` |
| The page itself | `/var/www/stats/index.html` |
| Password file | `/etc/nginx/.stats_htpasswd` |
| nginx location block | `/etc/nginx/snippets/stats.conf` |
| Weekly email | `/usr/local/bin/weekly-digest` (cron, Mondays 08:00 Beijing) |
| Mail account | `/etc/msmtprc` |

History lives in GoAccess's own database, so it keeps building up even though
the raw logs are rotated away after a couple of weeks. Requests to `/stats/`
are not logged, so reading the statistics does not show up in them.

`/var/www/stats/` sits outside the web root that the deploy workflow
synchronises, so deploying the site never overwrites or deletes the report.

## Installing, or changing the password

In the GitHub repo, under **Settings → Secrets and variables → Actions**:

| Secret | Needed | What it is |
| --- | --- | --- |
| `STATS_PASSWORD` | yes | password for the stats page |
| `MSMTP_CONFIG` | only for the email | the mail account, see below |
| `DIGEST_MAIL_TO` | only for the email | where the weekly summary goes |

Then **Actions → Set up analytics → Run workflow**. Running it again is
harmless and is also how you change the password or the mail settings.

Or, from a terminal with SSH access to the server:

```sh
scp -r deploy/analytics root@<server-ip>:/root/site-analytics
ssh root@<server-ip> "STATS_USER='lukas' STATS_PASS='<password>' \
  bash /root/site-analytics/setup-analytics.sh"
```

## The weekly email

`MSMTP_CONFIG` is the whole contents of an
[msmtp](https://marlam.de/msmtp/) configuration file. Any provider that
accepts authenticated SMTP works. Aliyun blocks outbound port 25, so use 465
or 587.

With a Gmail app password (Google account → Security → 2-Step Verification →
App passwords):

```
defaults
auth on
tls on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile /var/log/msmtp.log

account default
host smtp.gmail.com
port 465
tls_starttls off
from lukashenselecon@gmail.com
user lukashenselecon@gmail.com
password <the 16-character app password>
```

Set `from` to an address the provider will actually let you send as,
otherwise the mail is rejected or lands in spam.

To check it without waiting for Monday:

```sh
ssh root@<server-ip> /usr/local/bin/weekly-digest
```

## Removing it

```sh
ssh root@<server-ip> 'bash -s' < deploy/analytics/remove-analytics.sh
```

The setup script backs up `/etc/nginx` to `/root/nginx-backup-*.tar.gz` before
touching anything, and rolls the backup back automatically if nginx rejects the
new configuration.
