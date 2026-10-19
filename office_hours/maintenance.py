"""Remove private booking records and uploads after their retention period."""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from .app import BEIJING, SCHEMA, connect_db


def remove_expired_bookings(db_path: str, upload_dir: str, today: date) -> int:
    cutoff = (today - timedelta(days=90)).isoformat()
    db = connect_db(db_path)
    try:
        db.executescript(SCHEMA)
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


def main() -> int:
    db_path = os.environ.get("OFFICE_HOURS_DB", "/var/lib/lukas-office-hours/bookings.sqlite3")
    upload_dir = os.environ.get("OFFICE_HOURS_UPLOAD_DIR", "/var/lib/lukas-office-hours/uploads")
    try:
        removed = remove_expired_bookings(db_path, upload_dir, datetime.now(BEIJING).date())
    except (OSError, sqlite3.Error) as exc:
        print(f"Office-hours retention cleanup failed: {exc}", file=sys.stderr)
        return 1
    print(f"Removed {removed} expired booking records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
