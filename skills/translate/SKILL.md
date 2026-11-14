---
name: translate
description: Template skill. Fill untranslated strings in gettext (.po) translation catalogs, such as Lingui projects, and open or update the translation pull request. Fill in the Project config block first. Use when asked to translate the app, fill translation gaps, or update the translation catalog pull request.
---

# Translate the catalogs

> **Template.** Copy this skill into your project and fill in the Project config
> below; every step refers to those values. Written for Lingui-style `.po` catalogs
> (ICU plurals, numbered tags), and it works for plain gettext too.

## Project config

Replace each value before first use. Keep this block at the top of your copy.

| Setting | Value (example) |
| --- | --- |
| Locales folder | `locales` (one subfolder per locale) |
| Catalog file | `messages.po` |
| Source locale | `en` |
| Extract command | `npm run extract` (adds new strings, drops removed ones, keeps translations) |
| Compile / validate | `npx lingui compile --strict` |
| Extra tests | the project's i18n tests, if any |
| Sync branch | `i18n/catalog-sync` (if a workflow keeps one; otherwise none) |
| Own branch pattern | `i18n/translate-<date>` |
| PR title | `Translate new strings` |
| Brand names to keep as-is | your product name |
| Merge policy | squash-merge only when asked, after checks and review comments are done |

`catalog-gaps.ts`, next to this file, finds and fills empty entries without touching
anything else. It needs Node 22.6+ (`node --experimental-strip-types`) or 23.6+. It
reads the layout from the environment, so export these once per shell:

```sh
export CATALOG_LOCALES_DIR=<locales folder> CATALOG_FILE=<catalog file> CATALOG_SOURCE_LOCALE=<source locale>
GAPS="node <directory of this SKILL.md>/catalog-gaps.ts"
```

Run from the repo root.

## 1. Pick the branch

If a sync branch is configured and has an open pull request
(`gh pr list --head <sync branch> --state open`), check it out; otherwise branch
`<own branch pattern>` from `origin/main`. Either way, bring in the newest strings
before translating:

1. Merge `origin/main`. If a catalog conflicts, keep the branch's copy
   (`git checkout --ours -- <file>`) so its translations survive, and finish the merge.
2. Run the extract command. It must keep every existing translation.
3. Fill in anything main translated that the branch had not, for each locale:
   `git show origin/main:<locales folder>/<locale>/<catalog file> > /tmp/main-<locale>.po`,
   then `$GAPS apply <locale> /tmp/main-<locale>.po`.
4. Commit the result.

Run `$GAPS check`. If it exits 0, push what step 1 committed if you are on the sync
branch (your own branch needs no pull request when nothing changed), and stop.
Otherwise translate the gaps and fix any reported mismatch.

## 2. Translate

For each locale with gaps, `$GAPS list <locale>` prints the empty entries with their
source files and placeholder notes. With several locales, fan out one subagent per
locale (pair the small ones).

- Read the catalog's existing translations first and match their terms, tone and
  formality. Keep brand names as they are.
- Keep every placeholder (`{name}`, `{0}`), numbered tag (`<0>…</0>`, `<1/>`) and
  plural `#`. In `plural`/`select` messages keep the structure and variable, translate
  only the branch text, and use the language's own plural categories (Russian
  one/few/many/other, Hebrew one/two/other, Japanese, Korean and Chinese only other).
- Short labels stay short. Read the source file when the meaning is unclear. Use the
  source text for code, URLs and example values.

Write translations as JSON objects `{ "<key>": "<translation>" }`, about 120 per file,
using the exact `key` from `list`. Apply each file with
`$GAPS apply <locale> <file.json>`; it only fills entries that are still empty.

## 3. Verify

- `$GAPS check` exits 0.
- The compile / validate command passes, and so do the extra tests.
- Only translations changed:
  `git diff -U0 -- <locales folder> | grep -E '^[-+][^-+]' | grep -vE '^[-+]msgstr '`
  prints nothing.

## 4. Ship

Commit only the catalog files and push. On the sync branch, that push starts CI and
stops the sync workflow from overwriting the branch until it merges. On your own
branch, open a pull request with the configured title that says which locales changed
and that no native speaker reviewed them.

Take it to green with the `pr-watch` skill if it is installed. Merge only as the
merge policy allows.

---

Adapted from the `translate` skill in <https://github.com/elie222/rakazo>
(Apache-2.0). Changes: paths, commands and branch names moved into a Project config
block; `catalog-gaps.ts` reads its layout from environment variables.
