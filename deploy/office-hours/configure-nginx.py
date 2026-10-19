"""Add the booking API proxy to the site's nginx vhost with rollback."""

from __future__ import annotations

import glob
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DOMAIN = re.compile(r"(?:^|\s)lukashensel\.com(?:\s|;)")
INCLUDE = "    include /etc/nginx/snippets/office-hours.conf;\n"
PATHS = glob.glob("/etc/nginx/sites-enabled/*") + glob.glob("/etc/nginx/conf.d/*.conf")


def main() -> None:
    subprocess.run(["nginx", "-t"], check=True)
    changes: list[tuple[Path, str]] = []
    found = False
    for name in PATHS:
        path = Path(name)
        try:
            original = path.read_text()
        except (OSError, UnicodeError):
            continue
        if "snippets/office-hours.conf" in original:
            found = True
            continue
        updated = []
        for line in original.splitlines(keepends=True):
            updated.append(line)
            stripped = line.strip()
            if stripped.startswith("server_name") and DOMAIN.search(stripped):
                updated.append(INCLUDE)
                found = True
        replacement = "".join(updated)
        if replacement != original:
            changes.append((path, replacement))

    if not found:
        raise SystemExit("Could not find the lukashensel.com nginx server block.")
    if not changes:
        print("The nginx office-hours include is already present.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="office-hours-nginx-", dir="/root"))
    originals: list[tuple[Path, Path]] = []
    try:
        for index, (path, replacement) in enumerate(changes):
            backup = backup_dir / str(index)
            shutil.copyfile(path, backup)
            originals.append((path, backup))
            path.write_text(replacement)
        subprocess.run(["nginx", "-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
    except Exception:
        for path, backup in originals:
            shutil.copyfile(backup, path)
        subprocess.run(["nginx", "-t"], check=False)
        subprocess.run(["systemctl", "reload", "nginx"], check=False)
        raise
    print(f"nginx reloaded. Previous configuration saved in {backup_dir}.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"nginx setup failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
