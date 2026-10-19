"""Send the owner one Monday-night summary of Tuesday bookings.

The timer may invoke this repeatedly: a successful date is recorded in SQLite,
while a failed send is retried at the next invocation.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

from .app import BEIJING, SCHEMA, connect_db, slot_end


def next_tuesday(today: date) -> date:
    return today + timedelta(days=(1 - today.weekday()) % 7)


def build_message(db: sqlite3.Connection, target: date, sender: str, recipient: str) -> EmailMessage:
    rows = db.execute(
        "SELECT id, slot_time, name, email, purpose FROM bookings "
        "WHERE slot_date=? AND status='active' ORDER BY slot_time", (target.isoformat(),)
    ).fetchall()
    parts = [f"Office hours for Tuesday {target:%d %B %Y} (Beijing time)",
             f"{len(rows)} booking{'s' if len(rows) != 1 else ''}.", ""]
    for row in rows:
        files = db.execute("SELECT id, original_name FROM uploads WHERE booking_id=? ORDER BY original_name",
                           (row["id"],)).fetchall()
        parts.extend([f"{row['slot_time']}–{slot_end(row['slot_time'])} — {row['name']} <{row['email']}>",
                      f"Purpose: {row['purpose']}"])
        if files:
            parts.append("Files:")
            parts.extend(f"  {file['original_name']}: https://lukashensel.com/api/office-hours/admin/file/{file['id']}"
                         for file in files)
        else:
            parts.append("Files: none")
        parts.append("")
    parts.append("Private booking view: https://lukashensel.com/api/office-hours/admin/")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = f"Office hours Tuesday {target:%d %B}: {len(rows)} booking{'s' if len(rows) != 1 else ''}"
    msg.set_content("\n".join(parts))
    return msg


def send_with_msmtp(message: EmailMessage, recipient: str, config_path: str,
                    executable: str = "/usr/bin/msmtp") -> None:
    if not Path(config_path).is_file():
        raise RuntimeError("The private msmtp configuration is missing.")
    result = subprocess.run([executable, f"--file={config_path}", "--", recipient],
                            input=message.as_bytes(), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, timeout=45, check=False)
    if result.returncode:
        raise RuntimeError(f"msmtp returned exit code {result.returncode}.")


def remove_expired_bookings(db_path: str, upload_dir: str, today: date) -> int:
    """Remove booking details and uploads 90 days after the appointment."""
    cutoff = (today - timedelta(days=90)).isoformat()
    db = connect_db(db_path)
    try:
        rows = db.execute("SELECT stored_name FROM uploads WHERE booking_id IN "
                          "(SELECT id FROM bookings WHERE slot_date < ?)", (cutoff,)).fetchall()
        with db:
            count = db.execute("SELECT COUNT(*) FROM bookings WHERE slot_date < ?", (cutoff,)).fetchone()[0]
            db.execute("DELETE FROM bookings WHERE slot_date < ?", (cutoff,))
        for row in rows:
            try:
                (Path(upload_dir) / row["stored_name"]).unlink(missing_ok=True)
            except OSError:
                print("Could not remove one expired upload; check storage permissions.", file=sys.stderr)
        return count
    finally:
        db.close()


def send_digest(db_path: str, target: date, sender: str, recipient: str,
                config_path: str, executable: str = "/usr/bin/msmtp") -> bool:
    db = connect_db(db_path)
    try:
        db.executescript(SCHEMA)
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM digest_log WHERE slot_date=?", (target.isoformat(),)).fetchone():
            db.rollback()
            return False
        message = build_message(db, target, sender, recipient)
        send_with_msmtp(message, recipient, config_path, executable)
        db.execute("INSERT INTO digest_log VALUES (?, ?)",
                   (target.isoformat(), datetime.now(ZoneInfo("UTC")).isoformat()))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send the Tuesday office-hours summary")
    parser.add_argument("--date", help="Tuesday date (YYYY-MM-DD); defaults to the next Tuesday")
    args = parser.parse_args(argv)
    db_path = os.environ.get("OFFICE_HOURS_DB", "/var/lib/lukas-office-hours/bookings.sqlite3")
    upload_dir = os.environ.get("OFFICE_HOURS_UPLOAD_DIR", "/var/lib/lukas-office-hours/uploads")
    sender = os.environ.get("OFFICE_HOURS_MAIL_FROM", "")
    recipient = os.environ.get("OFFICE_HOURS_MAIL_TO", "")
    mail_config = os.environ.get("OFFICE_HOURS_MSMTP_CONFIG", "/etc/lukas-office-hours/msmtprc")
    if not sender or not recipient:
        print("Office-hours mail sender and recipient must be configured.", file=sys.stderr)
        return 1
    today = datetime.now(BEIJING).date()
    if not args.date and today.weekday() not in (0, 1):
        print("Automatic digest runs only on Monday evening or a delayed Tuesday start.")
        return 0
    try:
        target = date.fromisoformat(args.date) if args.date else next_tuesday(today)
    except ValueError:
        parser.error("--date must be YYYY-MM-DD")
    if target.weekday() != 1:
        parser.error("--date must be a Tuesday")
    try:
        remove_expired_bookings(db_path, upload_dir, today)
        sent = send_digest(db_path, target, sender, recipient, mail_config)
    except Exception as exc:
        print(f"Office-hours digest failed: {exc}", file=sys.stderr)
        return 1
    print("Office-hours digest sent." if sent else "Office-hours digest already sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
