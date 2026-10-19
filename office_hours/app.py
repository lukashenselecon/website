"""Private booking API and owner view. Run with Gunicorn behind nginx."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import html
import io
import os
import re
import secrets
import sqlite3
import uuid
import zipfile
from datetime import date, datetime, time, timedelta
from functools import wraps
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, Response, abort, jsonify, redirect, request, send_file
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


BEIJING = ZoneInfo("Asia/Shanghai")
SLOT_TIMES = tuple(f"{hour:02d}:{minute:02d}" for hour, minute in
                   ((10, 0), (10, 15), (10, 30), (10, 45),
                    (11, 0), (11, 15), (11, 30)))
MAX_FILE = 10 * 1024 * 1024
MAX_FILES = 3
ALLOWED_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
SCHEMA = """
CREATE TABLE IF NOT EXISTS bookings (
  id TEXT PRIMARY KEY,
  slot_date TEXT NOT NULL,
  slot_time TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  purpose TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  cancelled_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_booking_per_slot
  ON bookings(slot_date, slot_time) WHERE status = 'active';
CREATE TABLE IF NOT EXISTS uploads (
  id TEXT PRIMARY KEY,
  booking_id TEXT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
  original_name TEXT NOT NULL,
  stored_name TEXT NOT NULL,
  media_type TEXT NOT NULL,
  size_bytes INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS blocked_dates (
  slot_date TEXT PRIMARY KEY,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS access_attempts (
  ip_hash TEXT NOT NULL,
  window_start TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY(ip_hash, window_start)
);
CREATE TABLE IF NOT EXISTS digest_log (
  slot_date TEXT PRIMARY KEY,
  sent_at TEXT NOT NULL
);
"""


def connect_db(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=10000")
    return db


def now_beijing() -> datetime:
    return datetime.now(BEIJING)


def cutoff_for(tuesday: date) -> datetime:
    return datetime.combine(tuesday - timedelta(days=1), time(20), BEIJING)


def slot_end(start: str) -> str:
    hour, minute = (int(part) for part in start.split(":"))
    total = hour * 60 + minute + 15
    return f"{total // 60:02d}:{total % 60:02d}"


def upcoming_tuesdays(now: datetime, count: int = 4) -> list[date]:
    today = now.astimezone(BEIJING).date()
    first = today + timedelta(days=(1 - today.weekday()) % 7)
    dates = []
    while len(dates) < count:
        if now < cutoff_for(first):
            dates.append(first)
        first += timedelta(days=7)
    return dates


def valid_pku_email(raw: str) -> str | None:
    email = raw.strip()
    if len(email) > 254 or not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+", email):
        return None
    domain = email.rsplit("@", 1)[1].lower()
    if domain != "pku.edu.cn" and not domain.endswith(".pku.edu.cn"):
        return None
    if ".." in email or domain.startswith("."):
        return None
    return email.rsplit("@", 1)[0] + "@" + domain


def valid_upload(file_storage) -> tuple[str, bytes, str]:
    name = file_storage.filename.replace("\\", "/").split("/")[-1].strip()
    name = "".join(c for c in name if c.isprintable() and c not in "\r\n")[:120]
    suffix = Path(name).suffix.lower()
    if not name or suffix not in ALLOWED_TYPES:
        raise ValueError("Use a PDF, DOCX, PNG, or JPEG file.")
    content = file_storage.stream.read(MAX_FILE + 1)
    if len(content) > MAX_FILE:
        raise ValueError("Each file must be 10 MB or smaller.")
    magic_ok = {
        ".pdf": content.startswith(b"%PDF-"),
        ".png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        ".jpg": content.startswith(b"\xff\xd8\xff"),
        ".jpeg": content.startswith(b"\xff\xd8\xff"),
        ".docx": False,
    }
    if suffix == ".docx" and zipfile.is_zipfile(io.BytesIO(content)):
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names = archive.namelist()
            magic_ok[".docx"] = ("word/document.xml" in names and
                                  not any(name.lower().endswith("vbaproject.bin") for name in names))
    if not magic_ok[suffix]:
        raise ValueError("The file content does not match its type.")
    return name, content, ALLOWED_TYPES[suffix]


def create_app(config: dict | None = None) -> Flask:
    encoded_admin_password = os.environ.get("OFFICE_HOURS_ADMIN_PASSWORD_B64", "")
    if encoded_admin_password:
        try:
            admin_password = base64.b64decode(encoded_admin_password, validate=True).decode("utf-8")
        except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError("Invalid OFFICE_HOURS_ADMIN_PASSWORD_B64.") from exc
    else:
        admin_password = os.environ.get("OFFICE_HOURS_ADMIN_PASSWORD", "")
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.environ.get("OFFICE_HOURS_DB", "/var/lib/lukas-office-hours/bookings.sqlite3"),
        UPLOAD_DIR=os.environ.get("OFFICE_HOURS_UPLOAD_DIR", "/var/lib/lukas-office-hours/uploads"),
        SIGNING_KEY=os.environ.get("OFFICE_HOURS_SIGNING_KEY", ""),
        ADMIN_USER=os.environ.get("OFFICE_HOURS_ADMIN_USER", "lukas"),
        ADMIN_PASSWORD=admin_password,
        MAX_CONTENT_LENGTH=32 * 1024 * 1024,
    )
    if config:
        app.config.update(config)
    if len(app.config["SIGNING_KEY"]) < 32 or not app.config["ADMIN_PASSWORD"]:
        raise RuntimeError("Set a long OFFICE_HOURS_SIGNING_KEY and OFFICE_HOURS_ADMIN_PASSWORD.")
    db_path = Path(app.config["DATABASE"])
    upload_dir = Path(app.config["UPLOAD_DIR"])
    db_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    upload_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    db = connect_db(str(db_path))
    try:
        db.executescript(SCHEMA)
    finally:
        db.close()
    serializer = URLSafeTimedSerializer(app.config["SIGNING_KEY"], salt="office-hours-entry")

    @app.after_request
    def private_response(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    def booking_dates(db: sqlite3.Connection) -> list[dict]:
        dates = upcoming_tuesdays(now_beijing())
        keys = [d.isoformat() for d in dates]
        booked = {(row["slot_date"], row["slot_time"]) for row in db.execute(
            "SELECT slot_date, slot_time FROM bookings WHERE status='active' AND slot_date BETWEEN ? AND ?",
            (keys[0], keys[-1]))}
        blocked = {row["slot_date"] for row in db.execute(
            "SELECT slot_date FROM blocked_dates WHERE slot_date BETWEEN ? AND ?", (keys[0], keys[-1]))}
        return [{"date": key, "blocked": key in blocked,
                 "slots": [{"time": clock, "end": slot_end(clock),
                            "available": key not in blocked and (key, clock) not in booked}
                           for clock in SLOT_TIMES]} for key in keys]

    def token_identity(value: str) -> dict:
        try:
            data = serializer.loads(value, max_age=30 * 60)
        except (BadSignature, SignatureExpired):
            abort(401)
        if not isinstance(data, dict) or not data.get("name") or not valid_pku_email(data.get("email", "")):
            abort(401)
        return data

    def rate_limited(db: sqlite3.Connection) -> bool:
        # nginx overwrites X-Real-IP; the service listens only on localhost.
        ip = request.headers.get("X-Real-IP") or request.remote_addr or "unknown"
        key = hmac.new(app.config["SIGNING_KEY"].encode(), ip.encode(), hashlib.sha256).hexdigest()
        window = now_beijing().strftime("%Y-%m-%dT%H")
        db.execute("DELETE FROM access_attempts WHERE window_start < ?", (window,))
        db.execute("INSERT INTO access_attempts VALUES (?, ?, 1) "
                   "ON CONFLICT(ip_hash, window_start) DO UPDATE SET count=count+1", (key, window))
        count = db.execute("SELECT count FROM access_attempts WHERE ip_hash=? AND window_start=?",
                           (key, window)).fetchone()["count"]
        return count > 30

    @app.post("/api/office-hours/start")
    def start():
        data = request.get_json(silent=True) or {}
        if data.get("website"):
            return jsonify(code="identity", error="Unable to continue."), 400
        name = str(data.get("name", "")).strip()
        email = valid_pku_email(str(data.get("email", "")))
        if not 1 <= len(name) <= 120 or any(ord(c) < 32 for c in name) or not email:
            return jsonify(code="identity", error="Enter your name and a PKU email address."), 400
        db = connect_db(app.config["DATABASE"])
        try:
            with db:
                if rate_limited(db):
                    return jsonify(code="rate", error="Too many attempts. Please try later."), 429
            dates = booking_dates(db)
        finally:
            db.close()
        token = serializer.dumps({"name": name, "email": email})
        return jsonify(token=token, dates=dates)

    @app.post("/api/office-hours/slots")
    def slots():
        data = request.get_json(silent=True) or {}
        token_identity(str(data.get("token", "")))
        db = connect_db(app.config["DATABASE"])
        try:
            return jsonify(dates=booking_dates(db))
        finally:
            db.close()

    @app.post("/api/office-hours/book")
    def book():
        identity = token_identity(request.form.get("token", ""))
        slot_date = request.form.get("date", "")
        slot_time = request.form.get("time", "")
        purpose = request.form.get("purpose", "").strip()
        if not 1 <= len(purpose) <= 2000:
            return jsonify(code="purpose", error="Please describe the purpose in up to 2000 characters."), 400
        if slot_time not in SLOT_TIMES or slot_date not in [d.isoformat() for d in upcoming_tuesdays(now_beijing())]:
            return jsonify(code="unavailable", error="That slot is no longer open."), 409
        incoming = [item for item in request.files.getlist("attachments") if item.filename]
        if len(incoming) > MAX_FILES:
            return jsonify(code="file_count", error="Attach at most three files."), 400
        try:
            files = [valid_upload(item) for item in incoming]
        except (ValueError, zipfile.BadZipFile) as exc:
            return jsonify(code="file", error=str(exc)), 400

        db = connect_db(app.config["DATABASE"])
        stored = []
        booking_id = uuid.uuid4().hex
        try:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM blocked_dates WHERE slot_date=?", (slot_date,)).fetchone():
                db.rollback()
                return jsonify(code="unavailable", error="That date is unavailable."), 409
            db.execute("INSERT INTO bookings(id, slot_date, slot_time, name, email, purpose, created_at) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (booking_id, slot_date, slot_time, identity["name"], identity["email"],
                        purpose, datetime.now(ZoneInfo("UTC")).isoformat()))
            for original_name, content, media_type in files:
                upload_id = uuid.uuid4().hex
                stored_name = uuid.uuid4().hex
                path = upload_dir / stored_name
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                stored.append(path)
                with os.fdopen(fd, "wb") as output:
                    output.write(content)
                db.execute("INSERT INTO uploads VALUES (?, ?, ?, ?, ?, ?)",
                           (upload_id, booking_id, original_name, stored_name, media_type, len(content)))
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            for path in stored:
                path.unlink(missing_ok=True)
            return jsonify(code="taken", error="That slot has just been booked. Please choose another."), 409
        except Exception:
            db.rollback()
            for path in stored:
                path.unlink(missing_ok=True)
            app.logger.exception("Booking failed")
            return jsonify(code="failed", error="Booking failed. Please try again."), 500
        finally:
            db.close()
        return jsonify(reference=booking_id[:8].upper(), date=slot_date, time=slot_time,
                       end=slot_end(slot_time),
                       location="Guanghua Building 2, Office 343",
                       location_zh="光华管理学院 2 号楼 343 室"), 201

    def admin_required(fn):
        @wraps(fn)
        def guarded(*args, **kwargs):
            auth = request.authorization
            expected_user = app.config["ADMIN_USER"]
            expected_pass = app.config["ADMIN_PASSWORD"]
            if not auth or not (secrets.compare_digest(auth.username or "", expected_user) and
                                secrets.compare_digest(auth.password or "", expected_pass)):
                return Response("Authentication required", 401,
                                {"WWW-Authenticate": 'Basic realm="Office hours"'})
            return fn(*args, **kwargs)
        return guarded

    csrf = hmac.new(app.config["SIGNING_KEY"].encode(), b"owner-actions", hashlib.sha256).hexdigest()

    def require_csrf():
        if not secrets.compare_digest(request.form.get("csrf", ""), csrf):
            abort(403)

    @app.get("/api/office-hours/admin/")
    @admin_required
    def admin_page():
        db = connect_db(app.config["DATABASE"])
        try:
            today = now_beijing().date().isoformat()
            rows = db.execute("SELECT * FROM bookings WHERE slot_date>=? AND status='active' "
                              "ORDER BY slot_date, slot_time", (today,)).fetchall()
            blocked = db.execute("SELECT slot_date FROM blocked_dates WHERE slot_date>=? "
                                 "ORDER BY slot_date", (today,)).fetchall()
            uploads = db.execute("SELECT * FROM uploads WHERE booking_id IN "
                                 "(SELECT id FROM bookings WHERE slot_date>=? AND status='active')",
                                 (today,)).fetchall()
        finally:
            db.close()
        by_booking = {}
        for file in uploads:
            by_booking.setdefault(file["booking_id"], []).append(file)
        E = html.escape
        entries = []
        for row in rows:
            links = " ".join(f'<a href="/api/office-hours/admin/file/{E(file["id"])}">'
                             f'{E(file["original_name"])}</a>' for file in by_booking.get(row["id"], []))
            entries.append(f'<article><h2>{E(row["slot_date"])} at {E(row["slot_time"])}–{slot_end(row["slot_time"])}</h2>'
                           f'<p><strong>{E(row["name"])}</strong> · {E(row["email"])}</p>'
                           f'<p>{E(row["purpose"]).replace(chr(10), "<br>")}</p>'
                           f'<p>Files: {links or "None"}</p>'
                           f'<form method="post" action="/api/office-hours/admin/cancel/{E(row["id"])}">'
                           f'<input type="hidden" name="csrf" value="{csrf}">'
                           '<button type="submit">Cancel booking</button></form></article>')
        blocks = "".join(f'<li>{E(row["slot_date"])} '
                         '<form method="post" action="/api/office-hours/admin/unblock" class="inline">'
                         f'<input type="hidden" name="csrf" value="{csrf}">'
                         f'<input type="hidden" name="date" value="{E(row["slot_date"])}">'
                         '<button type="submit">Unblock</button></form></li>' for row in blocked)
        page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Office hours · private bookings</title><link rel="stylesheet" href="/assets/style.css">
<style>main{{max-width:800px}}article{{border-top:1px solid #ccc;padding:18px 0}}
article h2{{font-size:18px}}.inline{{display:inline}}button{{cursor:pointer}}</style></head><body>
<main><p class="lbl">Private</p><h1>Office hours bookings</h1>
<p>Upcoming bookings: {len(rows)}</p>{''.join(entries) or '<p>No upcoming bookings.</p>'}
<h2 class="sec">Block a Tuesday</h2><form method="post" action="/api/office-hours/admin/block">
<input type="hidden" name="csrf" value="{csrf}"><label for="date">Date</label>
<input id="date" type="date" name="date" required><button type="submit">Block date</button></form>
<ul>{blocks}</ul></main></body></html>'''
        return Response(page, mimetype="text/html")

    @app.post("/api/office-hours/admin/cancel/<booking_id>")
    @admin_required
    def cancel(booking_id):
        require_csrf()
        db = connect_db(app.config["DATABASE"])
        try:
            with db:
                db.execute("UPDATE bookings SET status='cancelled', cancelled_at=? "
                           "WHERE id=? AND status='active'",
                           (datetime.now(ZoneInfo("UTC")).isoformat(), booking_id))
        finally:
            db.close()
        return redirect("/api/office-hours/admin/", code=303)

    @app.post("/api/office-hours/admin/block")
    @admin_required
    def block():
        require_csrf()
        raw = request.form.get("date", "")
        try:
            target = date.fromisoformat(raw)
        except ValueError:
            abort(400)
        if target.weekday() != 1 or target < now_beijing().date() or target > now_beijing().date() + timedelta(days=365):
            abort(400)
        db = connect_db(app.config["DATABASE"])
        try:
            with db:
                if db.execute("SELECT 1 FROM bookings WHERE slot_date=? AND status='active'", (raw,)).fetchone():
                    return Response("Cancel existing bookings before blocking this date.", status=409)
                db.execute("INSERT OR IGNORE INTO blocked_dates VALUES (?, ?)",
                           (raw, datetime.now(ZoneInfo("UTC")).isoformat()))
        finally:
            db.close()
        return redirect("/api/office-hours/admin/", code=303)

    @app.post("/api/office-hours/admin/unblock")
    @admin_required
    def unblock():
        require_csrf()
        raw = request.form.get("date", "")
        try:
            date.fromisoformat(raw)
        except ValueError:
            abort(400)
        db = connect_db(app.config["DATABASE"])
        try:
            with db:
                db.execute("DELETE FROM blocked_dates WHERE slot_date=?", (raw,))
        finally:
            db.close()
        return redirect("/api/office-hours/admin/", code=303)

    @app.get("/api/office-hours/admin/file/<file_id>")
    @admin_required
    def download(file_id):
        db = connect_db(app.config["DATABASE"])
        try:
            file = db.execute("SELECT * FROM uploads WHERE id=?", (file_id,)).fetchone()
        finally:
            db.close()
        if not file:
            abort(404)
        path = upload_dir / file["stored_name"]
        return send_file(path, as_attachment=True, download_name=file["original_name"],
                         mimetype="application/octet-stream", max_age=0)

    return app
