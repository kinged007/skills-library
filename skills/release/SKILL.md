---
name: release
description: Template skill. Prepare a release by drafting the changelog section from the pull requests merged since the last tag, bumping the version, opening the release PR, and tagging it once merged. Fill in the Project config block first. Use when asked to cut, prepare, or ship a release or a new version.
---

# Release

> **Template.** Copy this skill into your project and fill in the Project config
> below. The flow (gather, draft, release PR, tag) is general; the file names,
> headings and workflow names are yours to set.

## Project config

| Setting | Value (example) |
| --- | --- |
| Changelog | `CHANGELOG.md`, Keep a Changelog layout with a `## [Unreleased]` heading |
| Version file(s) to bump | `package.json` (list every file that carries the version) |
| Tag pattern | `vX.Y.Z`, tagged on the release PR's merge commit |
| Release PR title | `Release vX.Y.Z` |
| PR body headings to read | `## What`, `## Why`, `## Risk` (or whatever your PR template uses) |
| Section order | Security, Added, Changed, Removed, Fixed (add an operator-notes section if you ship self-hosted software) |
| Audience | who reads the changelog: end users, operators, API consumers |
| Leave out | refactors, tests, CI, internal tooling, docs-only changes, fixes to bugs never released |
| What the tag triggers | your release workflow (builds, GitHub release text, image publishing) |
| Feature PRs and the changelog | feature PRs never touch it; the release writes it in one pass (drop this row if your project edits it per PR) |

## 1. Gather

```sh
git fetch origin --tags
last="$(git describe --tags --abbrev=0 --match 'v[0-9]*.[0-9]*.[0-9]*' origin/main)"
git log --format='%s' "$last"..origin/main | grep -oE '\(#[0-9]+\)$' | tr -d '(#)'
```

This reads PR numbers from squash-merge subjects ending in `(#123)`. If your project
merges differently, list the merged PRs another way (`gh pr list --state merged
--search "merged:>=<last tag date>"`). Adjust the tag glob to your tag pattern.

Read each pull request's title and the configured body headings
(`gh pr view N --json title,body,labels`). With many PRs, fan the reading out to
parallel subagents, each returning candidate entries for its slice.

## 2. Draft the section

Pick the version: patch for fixes, minor when users get new capability or operators
must act, major for breaking changes. Replace the `## [Unreleased]` content (fold in
anything already there) with `## [X.Y.Z] - YYYY-MM-DD` above the previous release, and
leave an empty `## [Unreleased]` on top.

- Use the configured section order.
- Include what the audience would notice. Drop everything in the Leave out row.
- One entry per change, merging PRs that are steps of one feature. Say what changed
  for the reader in plain words, link the relevant doc, and name settings exactly.
- Every security fix gets an entry. If the repo is public: no metrics, private hosts,
  or account details.

## 3. Release PR

Bump every configured version file to the new version in the same branch and open the
PR with the configured title. The maintainer reviews the changelog wording there.
Right before it merges, rerun the gather against current `main` and add entries for
anything merged since, because the tag covers everything up to the release PR's merge
commit.

## 4. Tag

After the PR merges, tag its merge commit and push the tag:

```sh
sha="$(gh pr view <release PR> --json mergeCommit -q .mergeCommit.oid)"
git fetch origin main && git tag vX.Y.Z "$sha" && git push origin vX.Y.Z
```

The tag runs whatever your release workflow does. If it refuses a tag without a
matching changelog section, that is why the section must be merged first.

---

Adapted from the `release` skill in <https://github.com/elie222/rakazo> (Apache-2.0).
Changes: project-specific names replaced by a Project config block.
