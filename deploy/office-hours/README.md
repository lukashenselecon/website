# Office-hours service deployment

When published, the static sign-up pages use the API at `/api/office-hours/`.
The API is a separate Python service on the existing server. Static `rsync --delete`
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
```

Keep secrets out of Git and chat. The booking service sends no email. The
server's existing analytics mail configuration is separate and is untouched.

## Install

### From GitHub Actions, without the server password

The repository has a manual **Actions → Set up office hours → Run workflow**
action. It uses the same `SERVER_IP` and `SERVER_SSH_KEY` repository secrets as
the site's existing deployment, so a separate SSH login is unnecessary. It
installs the private service only; the public sign-up page remains paused.

Before running it, add an Actions secret named
`OFFICE_HOURS_ADMIN_PASSWORD` under **Settings → Secrets and variables →
Actions**. Choose a new unique password of at least 20 characters; do not put
it in Git, chat, or a workflow input.

Run the action after committing and pushing the workflow. It transfers the
service, creates its private configuration, installs the systemd service and
retention timer, and adds the nginx proxy. It removes the old office-hours mail
configuration and email timer. The workflow checks that the live API returns
401 without a visitor token. A 404 means the proxy is not yet connected.
Re-running the action preserves existing bookings and the signing key; it
updates the admin password to the current secret.

### Direct server installation

The server needs Python 3.10 or newer. Transfer the `office_hours/` and
`deploy/office-hours/` directories to a
temporary source directory on the server, then run as root:

```sh
bash <source-directory>/deploy/office-hours/install.sh <source-directory>
```

The script installs a Gunicorn service on `127.0.0.1:8765`, a weekly retention
timer, and `/etc/nginx/snippets/office-hours.conf`. Add its one-line
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
4. Confirm the private owner report at
   `/api/office-hours/admin/summary?date=YYYY-MM-DD` rejects unauthenticated
   requests and returns Tuesday's bookings when signed in as `lukas`.
5. Confirm `systemctl list-timers lukas-office-hours-maintenance.timer` shows
   a weekly Monday 21:00 Beijing cleanup.

Each Tuesday's bookings close Monday at 20:00 Beijing time. The private report
contains names, email addresses, purposes, and attachment links. With no email
verification, a visitor can enter a made-up PKU address to view availability;
the form is a visibility step rather than an identity check.

The maintenance job deletes booking records and private uploads during the
first weekly run more than 90 days after their appointment. The sign-up form
tells visitors about this period.

## Monday summary in this app

The Codex scheduled task runs at 21:00 on Mondays in Beijing, after the 20:00
booking cutoff. It runs `deploy/office-hours/report-in-app.py` from this local
project and posts the output to the scheduling chat, including a zero-booking
summary. The script retrieves the private report over HTTPS. For local access,
store the existing office-hours admin password in macOS Keychain yourself:

```sh
security add-generic-password -a lukas -s lukas-office-hours \
  -l "Lukas office-hours report" -U -w
```

The final `-w` prompts for the password without putting it in the command or
Git. Do not paste the password into chat. After deploying the new API, run
`python3 deploy/office-hours/report-in-app.py` once locally and allow Keychain
access if macOS asks. The output should list the next Tuesday's bookings.
Keep this computer on and the desktop app running for local scheduled tasks;
review the first Monday run in the app's Scheduled view. A failed fetch should
be reported as an error, never as zero bookings.

For backups, preserve `/var/lib/lukas-office-hours/` and the private
configuration under `/etc/lukas-office-hours/`. Do not place those paths in the
website's `rsync` target or Git repository.
