"""Copies the app's changelog (PL + EN) into site/changelog.json for the "Zmiany" / "Changes" page.

Usage: python3 -I site/sync_changelog.py ../deadlock-assist   (path to the app repo), then rebuild the site.
Runs automatically in the app's release workflow (adam2s/deadlock-assist, .github/workflows/release.yml).
"""
import json
import re
import sys
from pathlib import Path


def strings(block):
    """The double-quoted strings of a TS array body, in order."""
    return [json.loads(m) for m in re.findall(r'"(?:[^"\\]|\\.)*"', block)]


def main():
    app = Path(sys.argv[1])
    pl_src = (app / "src" / "changelog.ts").read_text()
    en_src = (app / "src" / "changelogEn.ts").read_text()
    en = {
        m.group(1): strings(m.group(2))
        for m in re.finditer(r'^\s*"(\d+\.\d+\.\d+)":\s*\[(.*?)\],?\s*$', en_src, re.M | re.S)
    }
    releases = []
    pattern = r'version:\s*"([^"]+)",\s*date:\s*"([^"]+)",\s*changes:\s*\[(.*?)\]\s*,?\s*\}'
    for version, day, body in re.findall(pattern, pl_src, re.S):
        pl = strings(body)
        if len(en.get(version, [])) != len(pl):
            sys.exit(f"{version}: English text missing or has a different number of changes")
        releases.append({"version": version, "date": day, "pl": pl, "en": en[version]})
    if not releases:
        sys.exit("no releases found")
    out = Path(__file__).with_name("changelog.json")
    out.write_text(json.dumps(releases, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(releases)} versions, newest {releases[0]['version']} → {out}")


main()
