#!/usr/bin/env python3
"""Regenerate preview/index.html from the testing branch's index.html.

Run this from a checkout of main whenever testing has changes worth
previewing, then commit and push preview/index.html:

    python3 scripts/sync-preview.py
    git add preview/index.html
    git commit -m "Sync preview with testing"
    git push origin main
"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "preview" / "index.html"

BANNER = (
    '<div style="background:#7c3aed;color:#fff;text-align:center;'
    'font:700 .75rem/1.4 -apple-system,BlinkMacSystemFont,sans-serif;'
    'padding:6px 10px">🧪 PREVIEW BUILD — mirrors the testing branch, not the live app</div>\n'
)


def main():
    raw = subprocess.run(
        ["git", "show", "testing:index.html"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True,
    ).stdout

    out_lines = []
    skip_script = False
    for line in raw.splitlines(keepends=True):
        if "data-goatcounter=" in line:
            skip_script = True
        if skip_script:
            if "</script>" in line:
                skip_script = False
            continue
        if '<link rel="manifest"' in line:
            continue
        out_lines.append(line.replace('href="icons/', 'href="../icons/'))
    html = "".join(out_lines)

    html = html.replace(
        "<title>Progression Report</title>",
        "<title>Progression Report (Preview)</title>",
    )
    html = html.replace(
        '<meta name="apple-mobile-web-app-title" content="Progression Report">',
        '<meta name="apple-mobile-web-app-title" content="Progression Report (Preview)">\n'
        '<meta name="robots" content="noindex, nofollow">',
    )
    html = html.replace("<body>\n", "<body>\n" + BANNER, 1)

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(html)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
