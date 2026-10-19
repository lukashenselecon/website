#!/usr/bin/env python3
"""Print Tuesday's private bookings for the Monday Codex scheduled task."""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


SERVICE = "lukas-office-hours"
OWNER_URL = "https://lukashensel.com/api/office-hours/admin/"


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def markdown(value: str) -> str:
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", clean(value))


def format_report(data: dict) -> str:
    target = datetime.fromisoformat(data["date"])
    bookings = data["bookings"]
    lines = [f"Office hours — Tuesday {target:%d %B %Y} (Beijing time)",
             f"{len(bookings)} booking{'s' if len(bookings) != 1 else ''}.", ""]
    for booking in bookings:
        lines.append(f"- {markdown(booking['time'])}–{markdown(booking['end'])}: "
                     f"{markdown(booking['name'])} ({markdown(booking['email'])})")
        lines.append(f"  Purpose: {markdown(booking['purpose'])}")
        if booking["files"]:
            links = ", ".join(f"[{markdown(item['name'])}]({item['url']})"
                              for item in booking["files"])
            lines.append(f"  Attachments: {links}")
    lines.extend(["", f"[Private booking view]({OWNER_URL})"])
    return "\n".join(lines)


def main() -> int:
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    target = today + timedelta(days=(1 - today.weekday()) % 7)
    try:
        found = subprocess.run(
            ["security", "find-generic-password", "-a", "lukas", "-s", SERVICE, "-w"],
            capture_output=True, check=True, timeout=15,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("Office-hours Keychain access is unavailable. Set up the local Keychain item "
              "as described in deploy/office-hours/README.md, then run this script again.",
              file=sys.stderr)
        return 1
    password = found.stdout.decode("utf-8").rstrip("\n")
    credentials = base64.b64encode(f"lukas:{password}".encode()).decode("ascii")
    request = Request(
        f"{OWNER_URL}summary?date={target.isoformat()}",
        headers={"Authorization": f"Basic {credentials}", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            data = json.load(response)
    except HTTPError as exc:
        if exc.code == 401:
            print("The office-hours admin password in Keychain was rejected.", file=sys.stderr)
        else:
            print(f"The office-hours report returned HTTP {exc.code}.", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Could not retrieve the office-hours report: {exc}", file=sys.stderr)
        return 1
    print(format_report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
