# AGENTS.md

Guide for AI agents contributing to this repo. Humans: see README.md.

## What this repo is

A curated, rated and categorized library of agent skills (Claude Agent Skills format).
It does two jobs:

1. **Installable source.** `npx skills add kinged007/skills-library` discovers skills under `skills/<name>/SKILL.md`.
2. **Catalog data.** `catalog.json` is the single data source for a future website that filters skills by category, tag, rating and type.

## Two kinds of entry

| type | skill files live | installs from |
|---|---|---|
| `local` | `skills/<name>/SKILL.md` in this repo | this repo |
| `external` | upstream repo only. **Never copy the files here.** | the original author, always latest |

The no-copy rule for external skills is the core design decision. A reference keeps installs up to date and avoids forking someone else's work. If you want to modify an external skill, create a new `local` skill that credits the original in `notes`.

## Layout

```
skills/<name>/SKILL.md        local skill (plus any bundled files it needs)
catalog/entries/<id>.yaml     one entry per skill, local AND external
catalog/taxonomy.yaml         allowed categories (source of truth)
schema/entry.schema.json      entry schema (ENFORCED: undeclared fields fail the build)
scripts/build_catalog.py      validates entries, generates catalog.json
scripts/install-external.sh   installs every external skill from its author
catalog.json                  GENERATED. Never edit by hand.
.github/workflows/validate.yml  CI: build must pass and catalog.json must be current
```

## Add your own skill

1. Create `skills/<name>/SKILL.md` with frontmatter `name` (matching the folder, kebab-case) and a `description` that says what it does and when to use it.
2. Create `catalog/entries/<name>.yaml` with `type: local` and `path: skills/<name>`. The entry `id` must equal the filename, and `<name>` must equal the folder name, because the install command uses the folder name.
3. Fill in the catalog fields (below).
4. Run the build and commit.

## Reference an external skill

1. Find the skill in the upstream repo and confirm that the folder exists and has a `SKILL.md`.
2. Create `catalog/entries/<id>.yaml` with `type: external` and:
   - `source`: GitHub `owner/repo`
   - `path`: folder inside that repo, e.g. `skills/pdf`
   - `skill`: the name passed to `npx skills add --skill`
   - `ref`: branch or tag tracked (informational)
3. Prefix the `id` with the author or org when the name could collide, e.g. `anthropic-pdf`.
4. No script changes needed: install-external.sh reads external entries from catalog.json.
5. Run the build and commit.

For a repo with many skills, add one entry per skill. Don't vendor the repo.

## Catalog fields

- `title`, `summary`: one line each. The summary says what the skill does.
- `category`: exactly one, from `catalog/taxonomy.yaml`. To add a category, edit the taxonomy first and say so in the commit message. Prefer an existing category over `other`.
- `tags`: lowercase, kebab-case, at most 10. For external skills put the author/org tag first, then topic tags (ci, security, observability, shipping, interview, testing...). Avoid generic tags such as agent-skills or skills. Reuse tags already in catalog/entries/ before inventing new ones.
- `template`: optional boolean. `true` means the skill must be filled in per project (it has a Project config block) before use. The website filters on this field, so do not also add a `template` tag.
- `derived_from`: optional `{source, path, license}` on a `local` skill adapted from someone else's work. Only for skills whose licence allows modification; keep the original licence and credit in the skill's footer and in `NOTICE`. Prefer an `external` reference when you do not need to change the skill.
- `rating`: integers 1-5.
  - `score` is the overall verdict: 5 essential, 4 very good, 3 useful, 2 niche or rough, 1 avoid.
  - `quality`, `usefulness`, `maturity` are the sub-scores.
  - `reviewed` is an ISO date, set whenever you rate. Use the actual current date.
- `notes`: caveats, provenance, credit to the original author.

Rate honestly. Read the skill before you rate it, and don't inflate scores. If you haven't reviewed a skill, say so in `notes`. Don't make up a score.

## Before every commit

```bash
pip install pyyaml        # once
python scripts/build_catalog.py
git add catalog.json catalog/ skills/
```

The build fails on: missing fields, `id` not matching the filename, unknown category, score outside 1-5, a local `path` without `SKILL.md`, an external entry missing `source`/`path`/`skill`, or a skill in `skills/` with no entry. CI runs the same build and then `git diff --exit-code catalog.json`, so **always commit the regenerated `catalog.json` together with the entry change**.

## Conventions

- One skill (or one catalog change) per commit, with a message like `add skill: <name>`, `reference: <id>`, `rate: <id> 4->5`.
- Don't rename or delete an entry `id` without a reason. The website and install links may depend on it.
- Never commit secrets, tokens or personal data in skills or notes.
- Don't change the schema, taxonomy or build script as a side effect of adding a skill. Do that in a separate commit, and update README.md and this file if the contract changes.
- Skill content should be generic and reusable, not tied to one person's accounts.

## Verify your work

- `python scripts/build_catalog.py` prints `ok: N entries`.
- `git status` shows `catalog.json` in the commit.
- For a new local skill, `npx skills add <this repo> --list` should show it. For a new external one, `url` in `catalog.json` should open the real upstream folder.
- Say what you couldn't verify, such as the CI result or an upstream path you couldn't reach.
