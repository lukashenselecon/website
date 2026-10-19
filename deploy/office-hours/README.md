# Office-hours service deployment

The static pages in `build.py` link to the API at `/api/office-hours/`. The API
is a separate Python service on the existing server. Static `rsync --delete`
deployments exclude its source, database, uploads, and secrets. **Install and
verify this service before publishing the new static pages.**

## Private configuration

On the server, create `/etc/lukas-office-hours/office-hours.env` as root with
mode `0600`. It must contain:

```text
OFFICE_HOURS_SIGNING_KEY=<random secret of at least 32 characters>
OFFICE_HOURS_ADMIN_USER=lukas
OFFICE_HOURS_ADMIN_PASSWORD=<long unique password>
OFFICE_HOURS_DB=/var/lib/lukas-office-hours/bookings.sqlite3
OFFICE_HOURS_UPLOAD_DIR=/var/lib/lukas-office-hours/uploads
OFFICE_HOURS_MAIL_FROM=<address allowed by the configured SMTP account>
OFFICE_HOURS_MAIL_TO=lukas.hensel@gsm.pku.edu.cn
OFFICE_HOURS_MSMTP_CONFIG=/etc/lukas-office-hours/msmtprc
```

Keep secrets out of Git and chat. The mail account must be able to send from
`OFFICE_HOURS_MAIL_FROM`. Put its `msmtp` configuration in
`/etc/lukas-office-hours/msmtprc`; the installer gives it to the dedicated
`officehours` user with mode `0600`. The existing analytics configuration at
`/etc/msmtprc`, if present and suitable, can be copied privately. If it has a
`logfile` setting, use a path writable by `officehours` or remove that setting. The booking
system sends no messages to visitors. The Monday digest goes only to Lukas.

## Install

The server needs Python 3.10 or newer. Transfer the `office_hours/` and
`deploy/office-hours/` directories to a
temporary source directory on the server, then run as root:

```sh
bash <source-directory>/deploy/office-hours/install.sh <source-directory>
```

The script installs a Gunicorn service on `127.0.0.1:8765`, a Monday evening
systemd timer, and `/etc/nginx/snippets/office-hours.conf`. Add its one-line
`include` to the HTTPS `lukashensel.com` server block after backing up the
nginx configuration. Run `nginx -t`, reload nginx, and verify the API before
publishing the static pages. Only `/api/office-hours/` is proxied; the regular
website remains static.

The private owner view is at
`https://lukashensel.com/api/office-hours/admin/`. It uses the admin password
from the environment file. It lists upcoming bookings, lets Lukas cancel a
booking or block a Tuesday, and serves private attachments. Uploaded files are
never under the public web root. Use HTTPS for all access.

## Verify before publication

1. Confirm the service is active with `systemctl status lukas-office-hours`.
2. Confirm `curl -i -X POST -H 'Content-Type: application/json' -d '{}' https://lukashensel.com/api/office-hours/slots` receives 401.
3. Confirm a valid PKU address reaches the seven slots per Tuesday and another
   domain is rejected. Use a test booking, then cancel it in the owner view.
4. Test the configured `msmtp` account from the server, then run the digest
   for a chosen future Tuesday with `python -m office_hours.digest --date
   YYYY-MM-DD` as `officehours`, using the same private environment file as the
   service. Verify that the summary arrives in the Guanghua inbox. A successful
   send is recorded in SQLite, so choose a different date for another test.
5. Confirm `systemctl list-timers lukas-office-hours-digest.timer` shows a
   Monday 21:00 Beijing run. Additional attempts at 21:15, 21:30, 22:00, and
   23:00 retry a failed send; successful dates are sent only once.

Each Tuesday's bookings close Monday at 20:00 Beijing time. The digest contains
names, email addresses, purposes, and file names, with a link to the password
protected owner view. It sends even if there are zero bookings. With no email
verification, a visitor can enter a made-up PKU address to view availability;
the form is a visibility step rather than an identity check.

The digest job also deletes booking records and private uploads during the
first weekly run more than 90 days after their appointment. The sign-up form
tells visitors about this period.

For backups, preserve `/var/lib/lukas-office-hours/` and the private
configuration under `/etc/lukas-office-hours/`. Do not place those paths in the
website's `rsync` target or Git repository.
