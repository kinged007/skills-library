# Skills Library

A curated, rated and categorized library of agent skills (Claude Agent Skills format).
Two kinds of entry:

| type | where the skill lives | installs from |
|---|---|---|
| `local` | `skills/<name>/SKILL.md` in this repo | this repo |
| `external` | upstream repo (e.g. `anthropics/skills`), **reference only, never copied** | the original author, always latest |

## Install

```bash
# list / install our own skills
npx skills add kinged007/skills-library --list
npx skills add kinged007/skills-library --skill skill-review

# install an external skill straight from its author
npx skills add anthropics/skills --skill pdf

# or install all referenced external skills
scripts/install-external.sh
```

Each entry's exact command is in `catalog.json` (`install` field).

## Catalog

`catalog/entries/<id>.yaml`: one file per skill (local or external) with title, summary,
`category` (see `catalog/taxonomy.yaml`), free-form `tags`, and `rating` (score 1-5 plus
quality / usefulness / maturity). Schema: `schema/entry.schema.json`.

`python scripts/build_catalog.py` validates entries and generates `catalog.json`, the single
data source for the future website (filter by category, tag, rating, type).
CI fails if `catalog.json` is stale.

## Add a skill

- **Own:** create `skills/<name>/SKILL.md` and `catalog/entries/<name>.yaml` (`type: local`).
- **Someone else's:** create `catalog/entries/<id>.yaml` with `type: external`, `source`, `path`, `skill`. Don't copy files.
- Run the build script, then commit the entry and `catalog.json`.

## Rating scale

5 essential, 4 very good, 3 useful, 2 niche/rough, 1 avoid. Set `reviewed` when you rate.
