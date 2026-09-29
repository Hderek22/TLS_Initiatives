#!/usr/bin/env python3
"""Regenerate preview/ from the testing branch: index.html plus a mirror of sop/.

Run this from a checkout of main whenever testing has changes worth
previewing, then commit and push preview/:

    python3 scripts/sync-preview.py
    git add preview/
    git commit -m "Sync preview with testing"
    git push origin main
"""
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "preview" / "index.html"
SOP_OUT = REPO_ROOT / "preview" / "sop"


def mirror_sops():
    """Copy testing's sop/ into preview/sop/ so the preview uses testing's SOP files, not main's."""
    paths = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "testing", "sop/"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True,
    ).stdout.split()
    if SOP_OUT.exists():
        shutil.rmtree(SOP_OUT)
    SOP_OUT.mkdir(parents=True)
    for path in paths:
        data = subprocess.run(
            ["git", "show", f"testing:{path}"], cwd=REPO_ROOT, check=True, capture_output=True,
        ).stdout
        (SOP_OUT / Path(path).name).write_bytes(data)
    print(f"Mirrored {len(paths)} SOP file(s) into {SOP_OUT}")

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

    # Purple-accented icons/theme so the preview build is visually distinct from the
    # live green app if added to a home screen — see icons/icon-*-preview.png.
    html = html.replace('href="../icons/icon-512.png"', 'href="../icons/icon-512-preview.png"')
    html = html.replace('href="../icons/icon-180.png"', 'href="../icons/icon-180-preview.png"')
    html = html.replace(
        '<meta name="theme-color" content="#14532d">',
        '<meta name="theme-color" content="#2a1453">',
    )

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
    mirror_sops()


if __name__ == "__main__":
    main()
