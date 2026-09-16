# Sign-up forms

A small form service for student events, currently the Cohort 7 cycling trip
(Saturday, September 26, 2026; sign-up closes Wednesday, September 23 at 23:59
Beijing time).

* Public form: **https://lukashensel.com/cycling** (and `/zh/cycling`).
  Not linked from the menu and not in the sitemap; share the link directly.
* Responses: **https://lukashensel.com/signups/**, same login as `/stats/`,
  with a CSV download that opens cleanly in Excel.

Only a name is asked. Submitting the same name twice keeps one entry.
After the deadline the form answers with a "sign-up has closed" page.

## First-time setup

Run **Actions → Set up sign-up forms → Run workflow** once. It uses the
existing `SERVER_SSH_KEY`, `SERVER_IP` and `STATS_PASSWORD` secrets.

## Pieces

| Piece | Where |
| --- | --- |
| Service | `/usr/local/lib/signup-server.py`, systemd unit `site-signup` (port 8790, localhost only) |
| Responses | `/var/lib/signup/<event>.csv` |
| nginx locations | `/etc/nginx/snippets/signup.conf` |

## Another event later

Add an entry to `EVENTS` in `signup-server.py`, a page in `build.py`, push,
and run the setup workflow again.
