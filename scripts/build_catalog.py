#!/usr/bin/env python3
"""Validate catalog/entries/*.yaml and emit catalog.json (for the future website).
Run: python scripts/build_catalog.py   (needs pyyaml)

Allowed fields come from schema/entry.schema.json — that file is the single
source of truth. It used to be documentation only (nothing read it), so a field
absent from the schema still published verbatim on the site. Now an undeclared
field at any depth is a hard error, which is what keeps upstream skill text from
ever reaching the published payload.
"""
import json, sys, pathlib, yaml

root = pathlib.Path(__file__).resolve().parent.parent
cats = yaml.safe_load((root / "catalog/taxonomy.yaml").read_text())["categories"]
REPO = "kinged007/skills-library"

schema = json.loads((root / "schema/entry.schema.json").read_text())
errs = []
if schema.get("additionalProperties") is not False:
    errs.append(
        "schema/entry.schema.json: additionalProperties must be false; unknown "
        "entry fields are published verbatim, so the schema has to be closed"
    )
props = set(schema.get("properties", {}))
if set(schema.get("required") or []) - props:
    errs.append("schema/entry.schema.json: required names a field it does not declare")

# Fields that only make sense for one entry type. Everything else in the schema
# is allowed for both. Listing these here (rather than allowlists per type) means
# a property added to the schema is valid everywhere by default, and narrowing it
# is a deliberate edit.
TYPE_ONLY = {"local": {"template", "derived_from"}, "external": {"source", "ref", "skill"}}
ALLOWED = {t: (props - set().union(*TYPE_ONLY.values())) | TYPE_ONLY[t] for t in TYPE_ONLY}
for t, keys in TYPE_ONLY.items():
    if keys - props:
        errs.append(f"schema/entry.schema.json: {t}-only fields missing: {sorted(keys - props)}")


def check_keys(value, node, where, n):
    """Reject keys the schema does not declare, at any depth.

    Top-level is handled by ALLOWED (it narrows by type); this covers nested
    objects such as rating and derived_from, where an extra key would still be
    copied into the published payload.
    """
    if not isinstance(value, dict):
        return
    declared = set(node.get("properties") or {})
    closed = node.get("additionalProperties") is False
    if closed:
        for k in sorted(set(value) - declared):
            errs.append(
                f"{n}: {where}{k!r} is not in schema/entry.schema.json; undeclared "
                "fields are published verbatim, so declare it there first"
            )
    for k, v in value.items():
        child = (node.get("properties") or {}).get(k) or {}
        if child.get("type") == "array":
            items = child.get("items") or {}
            for i, item in enumerate(v or []):
                check_keys(item, items, f"{where}{k}[{i}].", n)
        else:
            check_keys(v, child, f"{where}{k}.", n)


# External entries are references: they hold OUR review commentary, never the
# upstream skill text (90n forbids public redistribution). Multi-line block
# scalars are how a pasted body looks, so they are rejected outright.
MAX_FIELD = {"title": 160, "summary": 400, "notes": 600}
# Reference locators are short by nature (real maxima at HEAD: path 72,
# source 37, ref 4, skill 50), so these caps cannot fail on honest data -
# they only stop an uncapped field carrying upstream text into the published
# payload (and its derived install/url/rawUrl copies). Mirrors maxLength in
# schema/entry.schema.json, which the build enforces: walking the schema only
# checks keys, so length needs this explicit gate.
MAX_REF_FIELD = {"path": 200, "source": 100, "ref": 40, "skill": 100}
for _k, _limit in MAX_REF_FIELD.items():
    _declared = ((schema.get("properties") or {}).get(_k) or {}).get("maxLength")
    if _declared != _limit:
        errs.append(
            f"schema/entry.schema.json: properties.{_k}.maxLength must be {_limit} "
            f"(got {_declared}); schema and build_catalog.MAX_REF_FIELD must agree"
        )
# Longest real tag today is 30 chars and the widest entry has 10, so these caps
# cannot fail on honest data - they only stop a tag being used as a text slot.
MAX_TAG_LEN = 40
MAX_TAGS = 12

out = []
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

    t = e.get("type")
    if t not in ALLOWED:
        errs.append(f"{n}: type must be local or external")
    else:
        for k in sorted(set(e) - ALLOWED[t]):
            errs.append(
                f"{n}: field {k!r} is not allowed on {t} entries; undeclared fields "
                "are published verbatim, so declare it in schema/entry.schema.json first"
            )
    check_keys({k: v for k, v in e.items() if k in props}, schema, "", n)
    tags = e.get("tags")
    if isinstance(tags, list) and any(not isinstance(t, str) for t in tags):
        errs.append(f"{n}: tags must be plain strings; structured tags would publish their fields")
    # A tag is a label, not a field. Unbounded, one tag can carry a whole
    # upstream body and publish it through a key nobody thinks to watch.
    if isinstance(tags, list):
        if len(tags) > MAX_TAGS:
            errs.append(f"{n}: {len(tags)} tags (limit {MAX_TAGS}); tags are labels, not prose")
        for tg in tags:
            if isinstance(tg, str) and len(tg) > MAX_TAG_LEN:
                errs.append(
                    f"{n}: tag of {len(tg)} chars (limit {MAX_TAG_LEN}); a tag is a label, "
                    "and unbounded text here publishes just like a body field"
                )

    if t == "local":
        if not (root / e.get("path", "x") / "SKILL.md").exists():
            errs.append(f"{n}: SKILL.md not found at path")
        _pv = e.get("path")
        if isinstance(_pv, str) and len(_pv) > MAX_REF_FIELD["path"]:
            errs.append(
                f"{n}: path is {len(_pv)} chars (limit {MAX_REF_FIELD['path']}); "
                "paths are locators, not text slots"
            )
        e["install"] = f"npx skills add {REPO} --skill {pathlib.Path(e['path']).name}"
        e["url"] = f"https://github.com/{REPO}/tree/main/{e['path']}"
    elif t == "external":
        for k in ("source", "path", "skill"):
            if k not in e:
                errs.append(f"{n}: external needs {k}")
        # References install from the original author and are never vendored.
        # Some upstream licences (90n) forbid public redistribution, so storing
        # upstream skill text here would be a licence breach, not a style issue.
        for k in ("body", "content", "skill_md", "text"):
            if str(e.get(k) or "").strip():
                errs.append(
                    f"{n}: external entries must not store skill text ({k}); "
                    "references point at the author, never copy"
                )
        for k, limit in MAX_REF_FIELD.items():
            v = e.get(k)
            if not isinstance(v, str):
                continue
            if len(v) > limit:
                errs.append(
                    f"{n}: external {k} is {len(v)} chars (limit {limit}); "
                    "reference locators are short, and the excess publishes "
                    "verbatim plus three derived copies (install/url/rawUrl)"
                )
        for k, limit in MAX_FIELD.items():
            v = e.get(k)
            if not isinstance(v, str):
                continue
            if len(v) > limit:
                errs.append(
                    f"{n}: external {k} is {len(v)} chars (limit {limit}); "
                    "this field is our own commentary, not the skill text"
                )
            if "\n" in v.strip():
                errs.append(
                    f"{n}: external {k} must be a single line; multi-line text here "
                    "is how a copied upstream body looks"
                )
        e["install"] = f"npx skills add {e.get('source')} --skill {e.get('skill')}"
        e["url"] = f"https://github.com/{e.get('source')}/tree/{e.get('ref', 'main')}/{e.get('path')}"
    out.append(e)

declared = {pathlib.Path(e["path"]).name for e in out if e.get("type") == "local"}
for p in {p.parent.name for p in (root / "skills").glob("*/SKILL.md")} - declared:
    errs.append(f"skills/{p} has no catalog entry")
if errs:
    print("\n".join(errs))
    sys.exit(1)
(root / "catalog.json").write_text(json.dumps({"categories": cats, "skills": out}, indent=2) + "\n")
print(f"ok: {len(out)} entries")
