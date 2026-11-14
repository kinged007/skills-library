#!/usr/bin/env python3
"""Validate catalog/entries/*.yaml and emit catalog.json (for the future website).
Run: python scripts/build_catalog.py   (needs pyyaml)"""
import json, sys, pathlib, yaml

root = pathlib.Path(__file__).resolve().parent.parent
cats = yaml.safe_load((root / "catalog/taxonomy.yaml").read_text())["categories"]
REPO = "kinged007/skills-library"
out, errs = [], []
for f in sorted((root / "catalog/entries").glob("*.yaml")):
    e = yaml.safe_load(f.read_text())
    n = f.name
    for k in ("id", "type", "title", "summary", "category", "tags", "rating"):
        if k not in e:
            errs.append(f"{n}: missing {k}")
    if e.get("id") != f.stem:
        errs.append(f"{n}: id must equal filename")
    if e.get("category") not in cats:
        errs.append(f"{n}: unknown category {e.get('category')}")
    s = (e.get("rating") or {}).get("score")
    if not isinstance(s, int) or not 1 <= s <= 5:
        errs.append(f"{n}: rating.score must be an integer 1-5")
    if "template" in e and not isinstance(e["template"], bool):
        errs.append(f"{n}: template must be true or false")
    df = e.get("derived_from")
    if df is not None and not all(k in df for k in ("source", "path", "license")):
        errs.append(f"{n}: derived_from needs source, path and license")
    if e.get("type") == "local":
        if not (root / e.get("path", "x") / "SKILL.md").exists():
            errs.append(f"{n}: SKILL.md not found at path")
        e["install"] = f"npx skills add {REPO} --skill {pathlib.Path(e['path']).name}"
        e["url"] = f"https://github.com/{REPO}/tree/main/{e['path']}"
    elif e.get("type") == "external":
        for k in ("source", "path", "skill"):
            if k not in e:
                errs.append(f"{n}: external needs {k}")
        e["install"] = f"npx skills add {e.get('source')} --skill {e.get('skill')}"
        e["url"] = f"https://github.com/{e.get('source')}/tree/{e.get('ref', 'main')}/{e.get('path')}"
    else:
        errs.append(f"{n}: type must be local or external")
    out.append(e)
declared = {pathlib.Path(e["path"]).name for e in out if e.get("type") == "local"}
for p in {p.parent.name for p in (root / "skills").glob("*/SKILL.md")} - declared:
    errs.append(f"skills/{p} has no catalog entry")
if errs:
    print("\n".join(errs))
    sys.exit(1)
(root / "catalog.json").write_text(json.dumps({"categories": cats, "skills": out}, indent=2) + "\n")
print(f"ok: {len(out)} entries")
