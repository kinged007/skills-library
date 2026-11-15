#!/usr/bin/env python3
"""Build the website data file docs/catalog.json from the catalog entries.

Run: python scripts/build_site.py   (needs pyyaml)

What it does:
  1. Runs scripts/build_catalog.py so catalog.json is validated and current.
  2. Reads catalog.json and, for every `local` entry, embeds the full
     skills/<name>/SKILL.md body as `body` (so the site renders our own
     skills offline and with zero fetches).
  3. For every `external` entry, computes `rawUrl` — the live upstream
     SKILL.md on raw.githubusercontent.com. The site fetches it in the
     browser at view time. External skill files are NEVER vendored here
     (core repo rule: references install from their authors, always latest).
  4. Writes docs/catalog.json: {generated_at, categories, skills}.

docs/catalog.json is GENERATED. Never edit by hand. CI checks it is fresh.
"""
import datetime
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "scripts"))

# Step 1: validate entries + regenerate catalog.json (exits non-zero on error).
r = subprocess.run([sys.executable, str(root / "scripts" / "build_catalog.py")],
                   capture_output=True, text=True)
sys.stdout.write(r.stdout)
sys.stderr.write(r.stderr)
if r.returncode != 0:
    sys.exit(r.returncode)

data = json.loads((root / "catalog.json").read_text())
skills = []
for e in data["skills"]:
    e = dict(e)
    if e.get("type") == "local":
        body_path = root / e["path"] / "SKILL.md"
        e["body"] = body_path.read_text()
    elif e.get("type") == "external":
        e["rawUrl"] = (
            f"https://raw.githubusercontent.com/{e['source']}"
            f"/{e.get('ref', 'main')}/{e['path']}/SKILL.md"
        )
    skills.append(e)

out = {
    "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"),
    "categories": data["categories"],
    "skills": skills,
}
docs = root / "docs"
docs.mkdir(exist_ok=True)
(docs / "catalog.json").write_text(json.dumps(out, indent=2) + "\n")
(docs / ".nojekyll").write_text("")
own = sum(1 for s in skills if s["type"] == "local")
print(f"ok: {len(skills)} entries ({own} own, "
      f"{len(skills) - own} references) -> docs/catalog.json")
