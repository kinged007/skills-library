---
name: pr-screenshots
description: Fetch the screenshots a CI-published gallery produced for a pull request and print them as Markdown images, so one can go in the PR description. Use for a UI change in a repo whose CI posts a per-PR screenshot gallery with a history.json and manifest.json; needs setup first.
---

# PR screenshots from a CI gallery

Optional companion to `pr-watch`. It only works with a CI setup that publishes, for
each PR, a gallery site and a bot comment linking to it. This is a template: set
the two variables below to match your CI, or adapt the script.

## What your CI must provide

- A conversation comment on the PR, posted by a bot account, that contains an HTML
  marker comment (for example `<!-- my-screenshots -->`) and a link of the form
  `https://<host>/<base>/prs/<number>/index.html`.
- `<host>/<base>/history.json`: an array of runs, newest first, each with
  `pullRequestNumber`, `sha` and `screenshotsUrl` (the run's `index.html`).
- `manifest.json` next to that `index.html`, with `screenshots[]` entries holding
  `captureType` (`checkpoint` for the frames worth sharing), `source`, `title` and
  `fileName`.

## Use

```bash
export PR_SCREENSHOTS_MARKER='<!-- my-screenshots -->'   # required
export PR_SCREENSHOTS_BOT='github-actions[bot]'          # default
"<directory of this SKILL.md>/pr-screenshots" [PR] [FILTER]
```

Output is one line per checkpoint: `<source>\t<Markdown image>`. Filter by the spec or
checkpoint name you wrote, pick the frame that shows the change, and put it in the
PR description (`gh api -X PATCH repos/{owner}/{repo}/pulls/<n> -F body=@<file>`).
A warning on stderr means the newest gallery is for an older commit than the PR
head; wait for CI or say so. Leave out frames that show private data.

Needs `gh`, `jq`, `curl`.

Adapted from `pr-watch/pr-screenshots` in <https://github.com/elie222/rakazo>
(Apache-2.0); the marker and bot account are now configurable.
