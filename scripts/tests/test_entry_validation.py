#!/usr/bin/env python3
"""Regression tests for issue #6: uncapped external reference fields.

source/path/ref/skill are upstream locators, not our commentary. Without
length caps one entry published 120,702 chars (10,000 per field plus derived
install/url/rawUrl copies). Caps (path 200 / source 100 / ref 40 / skill 100)
cost no honest entry - real maxima at HEAD are 72/37/4/50.

Run: python -m unittest discover -s scripts/tests  (needs pyyaml)
"""
import json
import pathlib
import subprocess
import sys
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CAPS = {"path": 200, "source": 100, "ref": 40, "skill": 100}


def build_catalog():
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_catalog.py")],
        capture_output=True, text=True,
    )


def base_external_entry():
    e = yaml.safe_load((ROOT / "catalog/entries/90n-critical-path.yaml").read_text())
    assert e["type"] == "external"
    return e


class RefCapsTest(unittest.TestCase):
    def test_schema_has_maxlength(self):
        schema = json.loads((ROOT / "schema/entry.schema.json").read_text())
        props = schema.get("properties", {})
        for field, cap in CAPS.items():
            self.assertEqual(
                (props.get(field) or {}).get("maxLength"), cap,
                f"schema properties.{field}.maxLength must be {cap}",
            )

    def test_build_enforces_schema_agreement(self):
        # build_catalog fails fast if schema maxLength drifts from MAX_REF_FIELD.
        text = (ROOT / "scripts/build_catalog.py").read_text()
        for field, cap in CAPS.items():
            self.assertIn(f'"{field}": {cap}', text)

    def test_oversized_ref_field_rejected(self):
        for field in CAPS:
            probe = ROOT / f"catalog/entries/zz-probe-{field}.yaml"
            e = base_external_entry()
            e["id"] = probe.stem
            e[field] = "a" * 10_000
            probe.write_text(yaml.safe_dump(e, sort_keys=False))
            try:
                r = build_catalog()
                self.assertNotEqual(
                    r.returncode, 0,
                    f"{field} of 10,000 chars must be rejected",
                )
                self.assertIn(f"external {field} is 10000 chars", r.stdout)
            finally:
                probe.unlink(missing_ok=True)
        # Tree is clean again: honest data builds.
        r = build_catalog()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("ok: 290 entries", r.stdout)

    def test_honest_entries_within_caps(self):
        for f in (ROOT / "catalog/entries").glob("*.yaml"):
            e = yaml.safe_load(f.read_text())
            if e.get("type") != "external":
                continue
            for field, cap in CAPS.items():
                v = e.get(field)
                if isinstance(v, str):
                    self.assertLessEqual(
                        len(v), cap, f"{f.name}: {field} exceeds cap",
                    )

    def test_published_total_bounded_derived_included(self):
        # Acceptance #4: derived install/url/rawUrl count too. Worst case under
        # caps is ~3.1k of locator+derived text; honest max today is ~13k
        # (local body). 20k bounds both with headroom, no honest entry near it.
        data = json.loads((ROOT / "docs/catalog.json").read_text())
        worst = 0
        for s in data["skills"]:
            total = sum(len(v) for v in s.values() if isinstance(v, str))
            total += sum(len(t) for t in s.get("tags", []) if isinstance(t, str))
            worst = max(worst, total)
        self.assertLess(worst, 20_000, f"max entry total {worst} exceeds bound")


if __name__ == "__main__":
    unittest.main()
