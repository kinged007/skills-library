# AGENTS.md

Guide for AI agents contributing to this repo. Humans: see README.md.

## What this repo is

A curated, rated and categorized library of agent skills (Claude Agent Skills format).
It does three jobs:

1. **Installable source.** `npx skills add kinged007/skills-library` discovers skills under `skills/<name>/SKILL.md`.
2. **Catalog data.** `catalog.json` is the single data source for the site: skills with title, summary, category, tags and rating.
3. **A live website.** https://kinged007.github.io/skills-library/ is built from that data, deployed by `.github/workflows/pages.yml` on every push to `main`. Search + filter by category, tag, rating, source and type, with a copyable install command and full skill text per entry.

## Two kinds of entry

| type | skill files live | installs from |
|---|---|---|
| `local` | `skills/<name>/SKILL.md` in this repo | this repo |
| `external` | upstream repo only. **Never copy the files here.** | the original author, always latest |

The no-copy rule for external skills is the core design decision. A reference keeps installs up to date and avoids forking someone else's work. If you want to modify an external skill, create a new `local` skill that credits the original in `notes`.

It is also a licence rule, not a style preference. Some upstreams (the 90n pack in `polar-bear-org/claude-skills`) allow internal use but forbid public redistribution, and the live site is public. `scripts/build_catalog.py` therefore fails the build if an external entry stores skill text in any field, and if an entry carries a field the schema does not declare. Pass the build and the site is safe to publish; CI green does **not** mean an upstream licence is cleared.

## Layout

```
skills/<name>/SKILL.md        local skill (plus any bundled files it needs)
catalog/entries/<id>.yaml     one entry per skill, local AND external
catalog/taxonomy.yaml         allowed categories (source of truth)
schema/entry.schema.json      entry schema (ENFORCED: undeclared fields fail the build)
scripts/build_catalog.py      validates entries, generates catalog.json
scripts/build_site.py         generates docs/catalog.json, the deployed payload
scripts/install-external.sh   installs every external skill from its author
catalog.json                  GENERATED. Never edit by hand.
docs/                         GitHub Pages artifact. docs/catalog.json is GENERATED.
.github/workflows/validate.yml  CI: build must pass and catalog.json must be current
.github/workflows/pages.yml     CI: rebuild + redeploy the site on every push to main
```

`catalog.json` (repo root) and `docs/catalog.json` have **different shapes**. Root is the build output of `build_catalog.py` and holds `categories` + `skills`. The deployed copy is written by `build_site.py` and adds `generated_at`, plus per-entry `body` (local skills only), `rawUrl`, `install` and `url`. Editing either by hand is a mistake: run `python scripts/build_site.py`.

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

Never paste upstream skill text into any field. `notes` is for your own review commentary, one line, at most 600 characters; the build rejects multi-line or oversized `title`, `summary` and `notes` on external entries.

## Catalog fields

- `title`, `summary`: one line each. The summary says what the skill does.
- `category`: exactly one, from `catalog/taxonomy.yaml`. To add a category, edit the taxonomy first and say so in the commit message. Prefer an existing category over `other`.
- `tags`: lowercase, kebab-case, at most 10. For external skills put the author/org tag first, then topic tags (ci, security, observability, shipping, interview, testing...). Avoid generic tags such as agent-skills or skills. Reuse tags already in catalog/entries/ before inventing new ones.
- `template`: optional boolean, `local` only. `true` means the skill must be filled in per project (it has a Project config block) before use. The website filters on this field, so do not also add a `template` tag.
- `derived_from`: optional `{source, path, license}` on a `local` skill adapted from someone else's work. Only for skills whose licence allows modification; keep the original licence and credit in the skill's footer and in `NOTICE`. Prefer an `external` reference when you do not need to change the skill.
- `rating`: integers 1-5.
  - `score` is the overall verdict: 5 essential, 4 very good, 3 useful, 2 niche or rough, 1 avoid.
  - `quality`, `usefulness`, `maturity` are the sub-scores.
  - `reviewed` is an ISO date, set whenever you rate. Use the actual current date.
- `notes`: caveats, provenance, credit to the original author.

Rate honestly. Read the skill before you rate it, and don't inflate scores. If you haven't reviewed a skill, say so in `notes`. Don't make up a score.

Any field not listed above (and not declared in `schema/entry.schema.json`) is a build error, at any depth, including inside `rating` and `derived_from`. That is deliberate: every field is copied into the published site payload, so an undeclared one would publish verbatim.

## Before every commit

```bash
pip install pyyaml        # once
python scripts/build_catalog.py
python scripts/build_site.py
git add catalog.json docs/catalog.json catalog/ schema/ skills/
```

The build fails on: missing fields, `id` not matching the filename, unknown category, score outside 1-5, a local `path` without `SKILL.md`, an external entry missing `source`/`path`/`skill`, a skill in `skills/` with no entry, an undeclared field, or external skill text stored in any field. CI runs the same build and then compares `catalog.json` and `docs/catalog.json`, so **always commit both regenerated files together with the entry change**.

## Conventions

- One skill (or one catalog change) per commit, with a message like `add skill: <name>`, `reference: <id>`, `rate: <id> 4->5`.
- Don't rename or delete an entry `id` without a reason. The website and install links may depend on it.
- Never commit secrets, tokens or personal data in skills or notes.
- Don't change the schema, taxonomy or build script as a side effect of adding a skill. Do that in a separate commit, and update README.md and this file if the contract changes.
- Skill content should be generic and reusable, not tied to one person's accounts.

## Verify your work

- `python scripts/build_catalog.py` prints `ok: N entries`.
- `python scripts/build_site.py` prints `ok: N entries (M own, K references)`.
- `git status` shows `catalog.json` and `docs/catalog.json` in the commit.
- For a new local skill, `npx skills add <this repo> --list` should show it. For a new external one, `url` in `catalog.json` should open the real upstream folder.
- Say what you couldn't verify, such as the CI result or an upstream path you couldn't reach.
