# Serving both editions from one website (Task 16)

## How the site is served now

GitHub Pages serves one site per repo. For this repo the source is the
`gh-pages` branch, root folder, with the classic ("legacy") build: whatever
files are in `gh-pages` are served at
`https://allendowney.github.io/ElementsOfDataScience/`. A folder inside
`gh-pages` becomes a path in the URL. So `gh-pages:v1/index.html` would be
served at `.../ElementsOfDataScience/v1/`.

Two different things could be called "v1". In this plan, `/v1/` is a
**folder in the `gh-pages` branch**, not the `v1` git branch. The site is
still served from `gh-pages` either way. The source for the 1e website lives
on the `v1` branch (`jb/`), and the source for the 2e website will live on
the `v2` branch. Each builds HTML that gets published into `gh-pages`.

`jb/publish.sh` runs `ghp-import -n -p -f _build/html`. Without a prefix,
ghp-import starts the new `gh-pages` commit with `deleteall`, replacing
the whole site. With `-x PREFIX`, it builds on the previous commit and deletes
only the files under `PREFIX` (checked in ghp-import 2.1.0's source,
`start_commit`).

## What links to the site

- The printed 1e book links to the site root three times
  (`allendowney.github.io/ElementsOfDataScience`), and to no individual pages.
  Its chapter links go to Colab.
- Deep links to 1e pages such as `.../07_dataframes.html` may exist on the
  web. We can't enumerate them.

So the root URL must keep working and lead 1e readers to the 1e site. Deep
links to 1e pages are nice to keep, not required.

## Options

**A. 2e at the root, 1e under `/v1/` (recommended).**

- Once, from `v1`: `ghp-import -n -p -x v1 _build/html` publishes the 1e site
  under `/v1/` and leaves the root alone.
- From then on, 1e's `jb/publish.sh` always uses `-x v1`.
- 2e's publish must not wipe `/v1/`, so it can't use a plain `ghp-import`.
  Either copy the current `gh-pages:v1/` into `_build/html/v1/` before
  importing, or publish through a worktree of `gh-pages` with
  `rsync --delete --exclude v1/`.
- A banner on each site points to the other ("Looking for the first
  edition?").
- Old 1e deep links at the root either land on the 2e page of the same name
  or 404. A custom `404.html` at the root could send `/X.html` to `/v1/X.html`.

**B. Each edition under its own prefix; the root redirects.**

- 1e at `/v1/` and 2e at `/v2/`, each published with `-x`, so neither
  touches the other.
- The root holds an `index.html` that redirects to the current edition, and
  optional stubs that redirect old 1e page names to `/v1/`.
- The simplest publishing (each branch only ever writes its own prefix), but
  the canonical URL gains a `/v2/`, and the root files need their own way to
  be published, since plain ghp-import can't touch the root without wiping
  both prefixes.

**C. Publish with GitHub Actions instead of `gh-pages`.**

- Switch Pages to "GitHub Actions" as the source. One workflow checks out
  `v1` and `v2`, builds both (`execute_notebooks: off`, so it is quick), and
  deploys the combined artifact.
- No `gh-pages` bookkeeping, and every push rebuilds the site. But the site
  then changes whenever either branch is pushed, instead of when you choose
  to publish, and it is more machinery than this needs.

## When

None of this is needed to create the `v2` branch. It is needed before 2e
publishes anything to the site. Until then, 1e keeps the root and
`jb/publish.sh` stays as it is.
