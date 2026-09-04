#!/usr/bin/env python3
"""Turns a GoAccess JSON report into a short plain-text weekly email.

First line of the output is the subject; everything after it is the body.
Usage: site-digest.py this-week.json [previous-week.json]
"""

import json
import sys

SITE = "lukashensel.com"
WIDTH = 62


def load(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return json.load(fh)
    except Exception:
        return None


def rows(report, panel, n=8):
    if not report or panel not in report:
        return []
    out = []
    for row in report[panel].get("data", [])[:n]:
        label = row.get("data")
        hits = row.get("hits", {}).get("count", 0)
        visitors = row.get("visitors", {}).get("count", 0)
        if label is not None:
            out.append((str(label), hits, visitors))
    return out


def countries(report, n=6):
    """GoAccess groups countries under continents; the countries are what matter."""
    if not report or "geolocation" not in report:
        return []
    flat = []
    for cont in report["geolocation"].get("data", []):
        items = cont.get("items")
        if items:
            for item in items:
                flat.append((str(item.get("data", "")).strip(),
                             item.get("hits", {}).get("count", 0),
                             item.get("visitors", {}).get("count", 0)))
        else:
            flat.append((str(cont.get("data", "")).strip(),
                         cont.get("hits", {}).get("count", 0),
                         cont.get("visitors", {}).get("count", 0)))
    flat.sort(key=lambda r: r[1], reverse=True)
    return flat[:n]


def change(now, before):
    if not before:
        return ""
    delta = round(100.0 * (now - before) / before)
    if delta == 0:
        return " (flat on the week before)"
    return " (%s%d%% on the week before)" % ("+" if delta > 0 else "", delta)


def section(title, entries, unit="views"):
    if not entries:
        return []
    lines = ["", title, "-" * len(title)]
    width = max(len(label) for label, _, _ in entries)
    width = min(width, WIDTH - 12)
    for label, hits, _ in entries:
        if len(label) > width:
            label = label[: width - 1] + "…"
        lines.append("  %-*s  %5d %s" % (width, label, hits, unit))
    return lines


def main():
    this = load(sys.argv[1])
    prev = load(sys.argv[2]) if len(sys.argv) > 2 else None
    if not this:
        sys.exit(1)

    g = this.get("general", {})
    pg = (prev or {}).get("general", {})
    visitors = g.get("unique_visitors", 0)
    views = g.get("valid_requests", 0)

    subject = "%s: %d visitors last week" % (SITE, visitors)

    body = [
        "%s to %s" % (g.get("start_date", "?"), g.get("end_date", "?")),
        "",
        "  %d visitors%s" % (visitors, change(visitors, pg.get("unique_visitors", 0))),
        "  %d pageviews%s" % (views, change(views, pg.get("valid_requests", 0))),
    ]

    pages = [r for r in rows(this, "requests", 12) if not r[0].lower().endswith(".pdf")]
    body += section("Most read pages", pages[:6])

    pdfs = [r for r in rows(this, "requests", 40) if r[0].lower().endswith(".pdf")]
    body += section("Papers downloaded", pdfs[:8], unit="downloads")

    body += section("Where people came from", rows(this, "referring_sites", 6), unit="visits")
    body += section("Countries", countries(this), unit="visits")

    missing = rows(this, "not_found", 5)
    if missing:
        body += section("Links that led nowhere", missing, unit="hits")

    body += [
        "",
        "Full report: https://%s/stats/" % SITE,
        "Known crawlers are excluded and IP addresses are anonymised.",
    ]

    print(subject)
    print("\n".join(body))


if __name__ == "__main__":
    main()
