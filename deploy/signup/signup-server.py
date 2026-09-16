#!/usr/bin/env python3
"""
Tiny sign-up service for lukashensel.com.

Standard library only. nginx forwards two things here:
  POST /api/signup/<event>   the public form (see cycling.html)
  GET  /signups/...          the password-protected list (auth is done by nginx)

Responses are kept in one CSV per event under $SIGNUP_DIR. A second sign-up
with the same email address replaces the earlier one, so students can correct
their details by simply submitting the form again.
"""
import csv, html, io, os, sys, threading
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

BJ = timezone(timedelta(hours=8))
DATA_DIR = os.environ.get("SIGNUP_DIR", "/var/lib/signup")
PORT = int(os.environ.get("SIGNUP_PORT", "8790"))

# ---------------------------------------------------------------- events ----
# To run another sign-up later, add an entry here and a page in build.py.
EVENTS = {
    "cycling": {
        "title": "Cycling trip, Sat 26 Sep 2026 (Future Leaders Cohort 7)",
        "deadline": datetime(2026, 9, 23, 23, 59, 59, tzinfo=BJ),
        "page": "/cycling",
        "fields": [
            # (name, label, required, max length, allowed values or None)
            ("name",   "Name",              True,  80,  None),
            ("email",  "Email",             True,  120, None),
            ("wechat", "WeChat ID",         False, 60,  None),
            ("bike",   "Shared-bike app",   True,  20,  ("ready", "not-yet", "help")),
            ("early",  "Exploring before",  False, 10,  ("yes", "maybe", "no")),
            ("note",   "Note",              False, 500, None),
        ],
    },
}
LABELS = {"ready": "Ready", "not-yet": "Not yet, will set up", "help": "Needs help",
          "yes": "Yes", "maybe": "Maybe", "no": "No"}

LOCK = threading.Lock()


def csv_path(slug):
    return os.path.join(DATA_DIR, slug + ".csv")


def columns(ev):
    return ["submitted_bj"] + [f[0] for f in ev["fields"]] + ["lang"]


def load(slug):
    path = csv_path(slug)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(slug, ev, rows):
    path = csv_path(slug)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns(ev), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def clean(v):
    # Strip control characters and guard against formula injection when the
    # CSV is opened in Excel.
    v = "".join(ch for ch in v if ch == "\n" or ch >= " ").strip()
    if v[:1] in ("=", "+", "-", "@"):
        v = "'" + v
    return v


PAGE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>{title}</title>
<link rel="stylesheet" href="/assets/style.css"></head>
<body><main id="main">{body}</main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "signup"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.headers.get("X-Real-IP", "-"), fmt % args))

    def send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def message(self, code, lang, title, text, back):
        link = ('<p><a class="lk" href="%s">%s</a></p>'
                % (back, "返回报名页面" if lang == "zh" else "Back to the form"))
        body = "<h1>%s</h1><p>%s</p>%s" % (html.escape(title), text, link)
        self.send(code, PAGE.format(lang="zh-Hans" if lang == "zh" else "en",
                                    title=html.escape(title), body=body))

    # ------------------------------------------------------------ public ---
    def do_POST(self):
        parts = self.path.split("?")[0].strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "signup"] or parts[2] not in EVENTS:
            return self.send(404, "not found", "text/plain")
        slug = parts[2]
        ev = EVENTS[slug]
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = 0
        if n <= 0 or n > 8000:
            return self.send(400, "bad request", "text/plain")
        form = parse_qs(self.rfile.read(n).decode("utf-8", "replace"))
        get = lambda k: (form.get(k) or [""])[0]
        lang = "zh" if get("lang") == "zh" else "en"
        zh = lang == "zh"
        back = ("/zh" if zh else "") + ev["page"]

        if get("website"):  # honeypot, filled only by bots
            return self.send(303, "", extra={"Location": back + "-thanks"})

        if datetime.now(BJ) > ev["deadline"]:
            return self.message(410, lang, "报名已截止" if zh else "Sign-up has closed",
                                "报名已于 9 月 23 日截止。如仍想参加，请在班级微信群里联系 Lukas。" if zh else
                                "The deadline was Wednesday, September 23. If you would still like "
                                "to join, message Lukas in the class WeChat group.", back)

        row, problems = {}, []
        for name, label, required, maxlen, allowed in ev["fields"]:
            v = clean(get(name))[:maxlen]
            if required and not v:
                problems.append(label)
            if allowed and v and v not in allowed:
                problems.append(label)
            row[name] = v
        email = row.get("email", "")
        if email and ("@" not in email or " " in email or "." not in email.split("@")[-1]):
            problems.append("Email")
        if problems:
            return self.message(400, lang, "请检查表格" if zh else "Please check the form",
                                ("以下内容缺失或有误：" if zh else "Missing or invalid: ")
                                + html.escape(", ".join(dict.fromkeys(problems))), back)

        row["email"] = email.lower()
        row["lang"] = lang
        row["submitted_bj"] = datetime.now(BJ).strftime("%Y-%m-%d %H:%M")
        with LOCK:
            rows = [r for r in load(slug) if r.get("email", "").lower() != row["email"]]
            rows.append(row)
            save(slug, ev, rows)
        self.send(303, "", extra={"Location": back + "-thanks"})

    # ----------------------------------------------- behind nginx auth only ---
    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/signups/", "/signups/index.html"):
            return self.index()
        if path.startswith("/signups/") and path.endswith(".csv"):
            slug = path[len("/signups/"):-4]
            if slug in EVENTS:
                buf = io.StringIO()
                w = csv.DictWriter(buf, fieldnames=columns(EVENTS[slug]), extrasaction="ignore")
                w.writeheader()
                w.writerows(load(slug))
                return self.send(200, "﻿" + buf.getvalue(), "text/csv; charset=utf-8",
                                 {"Content-Disposition": 'attachment; filename="%s-signups.csv"' % slug})
        self.send(404, "not found", "text/plain")

    def index(self):
        out = ["<h1>Sign-ups</h1>"]
        now = datetime.now(BJ)
        for slug, ev in EVENTS.items():
            rows = sorted(load(slug), key=lambda r: r.get("submitted_bj", ""))
            state = "open" if now <= ev["deadline"] else "closed"
            out.append('<h2 class="sec">%s</h2>' % html.escape(ev["title"]))
            bikes = {}
            for r in rows:
                bikes[r.get("bike")] = bikes.get(r.get("bike"), 0) + 1
            out.append('<p><b>%d signed up</b> &middot; sign-up %s (deadline %s Beijing time) &middot; '
                       '<a class="lk" href="/signups/%s.csv">Download CSV</a></p>'
                       % (len(rows), state, ev["deadline"].strftime("%a %d %b, %H:%M"), slug))
            if rows:
                out.append('<p class="meta">Shared-bike app: %s</p>' % ", ".join(
                    "%s %d" % (LABELS.get(k, k or "?"), v) for k, v in bikes.items()))
                heads = ["#", "Signed up"] + [f[1] for f in ev["fields"]]
                t = ['<div style="overflow-x:auto"><table style="border-collapse:collapse;font-size:14px">',
                     "<tr>" + "".join('<th style="text-align:left;padding:4px 10px;border-bottom:1px solid #ccc">%s</th>'
                                      % h for h in heads) + "</tr>"]
                for i, r in enumerate(rows, 1):
                    cells = [str(i), r.get("submitted_bj", "")] + [
                        LABELS.get(r.get(f[0], ""), r.get(f[0], "")) for f in ev["fields"]]
                    t.append("<tr>" + "".join('<td style="padding:4px 10px;border-bottom:1px solid #eee;vertical-align:top">%s</td>'
                                              % html.escape(c) for c in cells) + "</tr>")
                t.append("</table></div>")
                out.append("".join(t))
        self.send(200, PAGE.format(lang="en", title="Sign-ups", body="\n".join(out)))


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    print("listening on 127.0.0.1:%d, data in %s" % (PORT, DATA_DIR), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
