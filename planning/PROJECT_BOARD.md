# Elements of Data Science Project Board

Numbered tasks for tracking work. Each task has a permanent number; add new
tasks at the end. Update status as work progresses.

Keep each task short here. When a task needs more than a few paragraphs (a
design, an inventory, a decision with options), write it up in a separate file
in `planning/` and link to it from the task.

Planning documents:

- [repos.md](repos.md): how this repo, ElementsOfDataScienceSolutions, and
  ElementsOfDataScienceBook fit together
- [v2_plan.md](v2_plan.md): the second edition, a companion to *You Would
  Choose Now*
- [working_tree_triage.md](working_tree_triage.md): every untracked and
  modified path, and what to do with it
- [site_versions.md](site_versions.md): serving the 1e and 2e websites
  side by side (Task 16)

### Current focus (2026-09-24)

Getting `v1` into a clean state before creating the `v2` branch. The second
edition keeps the title, so v2 will be a branch of this repo, made the default
once it is ready (see [v2_plan.md](v2_plan.md)).

- **Done:** **Task 1** (repo survey), **Task 3** (README links), **Task 4** (test workflow; CI green on all three OSes), **Task 5** (working tree: 147 paths → 21 in limbo), **Task 6** (`soln/` self-contained), **Task 11** (`v1.0.1` tag; `v1` protected), **Task 8** (`environment.yml`), **Task 17** (`jupyter_intro` passes), **Task 7** (Solutions repo superseded), **Task 18** (`resampling_example_gun` fixed), **Task 19** (pandas 3: chained `inplace`, positional `to_hdf`), **Tasks 10, 14, 15** (soln tests in CI, build/publish split, `CLAUDE.md`), **Task 9** (README), **Task 12** (keep extracts), **Task 13** (top level pruned)
- **Next:** ready to create the `v2` branch; nothing on the board blocks it
- **Before branching:** none left
- **v2 prep:** Task 16

---

## Task 1: Survey the three EDS repos

**Status:** Done 2026-09-23. Write-up in [repos.md](repos.md).

`soln/` in this repo is the canonical copy of the solution notebooks. The
Solutions repo is an older copy (see Task 7). The solutions being public is
intentional.

## Task 2: Plan the second edition

**Status:** Draft, 2026-09-23. Plan in [v2_plan.md](v2_plan.md).

Decided: keep the title, so v2 is a `v2` branch here, not a new repo. Still
open: timing relative to YWCN, ANES licensing, and the others listed in the
plan.

## Task 3: Point the README links at `v1`

**Status:** Done 2026-09-23 (`600a0aa`).

All 26 Colab and download links in `README.md` pointed to `master`, which
holds the pre-publication notebooks from March 2024. They now point to `v1`.
Each target was checked to exist on `origin/v1`.

## Task 4: Update the test workflow; confirm the tests pass

**Status:** Done 2026-09-23 (`51d3fe6`). CI run `35936598928` passed on
Ubuntu, Windows, and macOS.

The monthly scheduled run has passed every month from February to September
2026, so the tests have been running. But the workflow is out of date:
`actions/checkout@v4` and `setup-python@v5` run on Node 20, which GitHub has
deprecated, and it tests only Python 3.11 on Ubuntu.

- [x] Bring `.github/workflows/tests.yml` in line with ThinkStats (`301f61b`):
      actions v7, Python 3.13, `fail-fast: false`, pip caching keyed on both
      requirements files. (The commit message says 3.12/3.13; 3.12 was
      dropped from the matrix before the commit.)
- [x] Put Windows and macOS back in the matrix. They had been excluded
      because of Unicode on Windows and `pytables` installs on macOS. Chapters
      4–6 call `open('2600-0.txt')` without an encoding, which fails under
      Windows' default cp1252, so the workflow sets `PYTHONUTF8=1`. `tables`
      now ships macOS wheels. Both fixes work: all three OSes pass.
- [x] Run the tests locally: **14/14 pass** (2m 34s) in a clean Python 3.13
      environment built from `requirements-dev.txt` (pandas 3.0.6, numpy
      2.5.3, matplotlib 3.11.2, geopandas 1.1.4), on a clean export of
      `origin/v1`
- [x] Push and confirm a green run on all three legs

## Task 5: Triage the working tree

**Status:** Done 2026-09-24 (`2151a4e`..`718a97c`). Outcome and the limbo
list are at the top of [working_tree_triage.md](working_tree_triage.md).

`git status` shows 147 paths: 13 modified or deleted tracked files and 134
untracked paths, including 92 MB of another repo's clone
(`DS10-Python-HW/`), a 158 MB HDF file, and 45 MB of website build output.
Real changes are invisible in the noise. Goal: every path is tracked,
ignored, or deleted, apart from a short, named list left in limbo.

- [x] Add `.gitignore` rules for runtime downloads, build output, and
      separate clones
- [x] Track the website build sources that were untracked
      (`jb/_toc.yml`, `jb/build.sh`, `jb/prep_notebooks.py`)
- [x] Review and commit, or restore, the modified tracked files
- [x] Delete the obvious junk (each file checked first; see the outcome notes)
- [x] Record what is left in limbo (21 paths)

## Task 6: Make `soln/` self-contained

**Status:** Done 2026-09-24 (`a2fe490`, plus the `utils.py` links).

Only the 14 chapter notebooks in `soln/` are tracked. `build.sh` also copies
`soln/utils.py`, `soln/jupyter_intro.ipynb`, `soln/geo_example.ipynb`, and
`soln/clustering_soln.ipynb`, all untracked, so the build depends on files
that exist only on this machine. The data-cleaning notebooks (`clean_*.ipynb`)
that build `data/` are also untracked here; they are tracked only in the
Solutions repo.

- [x] Track the files `build.sh` reads, and the `clean_*.ipynb` notebooks
- [x] The top-level `utils.py` is canonical (the notebooks download it from
      `raw/v1/utils.py`). `soln/utils.py` and `jb/utils.py` are relative
      symlinks to it, and `build.sh` no longer copies it. Checked:
      `soln/03_arrays.ipynb` passes under nbmake through the link.
- [x] Gitignore the data that the notebooks in `soln/` download when run

## Task 7: Mark the Solutions repo as superseded

**Status:** Done 2026-09-24. The Solutions repo README now says it is
unmaintained and points to `soln/` (Solutions commit `f4e4085`, rebuilt on
top of a shorter README note made on GitHub in May 2025). The repo is
not archived on GitHub.

The Solutions repo has an older version of `07_dataframes.ipynb`, and its
`manuscript/` directory is deleted locally but still tracked.

- [x] `quizzes/`: the seven quiz notebooks (as committed there, `887e660`)
      are in `archive/quizzes/`. Their data files were never committed and
      were not copied.
- [x] The `clean_brfss-*` notebooks were already in `soln/` (Task 5).
- [x] Extra notebooks in `soln/`, with the convention that `soln/X_soln.ipynb`
      is the source and `examples/X.ipynb` has the solutions removed:
      - `odds_soln.ipynb` tracked; it is the source of `examples/odds.ipynb`
        (10 solution cells). The duplicate `examples/odds_soln.ipynb` was
        deleted.
      - `testing_means_soln.ipynb` tracked. It has 12 solution cells and no
        counterpart in `examples/`. A top-level `testing_means.ipynb` existed
        from 2020 until `e5f8829` (May 2025) deleted it.
      - `resampling_example_gun.ipynb` tracked, and
        `examples/resampling_example_gun.ipynb` generated from it with the
        one solution removed. Both failed; fixed in Task 18.
      - `resampling.ipynb` renamed `missing_values.ipynb` (no solutions).
        `examples/resampling.ipynb` is still the same notebook under the old
        name. It fails outside this machine: it reads a local `gss_eda.hdf5`
        and never downloads it.
- [x] README note in the Solutions repo. Not archived on GitHub.

## Task 8: Refresh `environment.yml`

**Status:** Done 2026-09-24.

`environment.yml` pinned **Python 3.7**, listed `descartes` and `xlrd`, and
omitted `plotly`, `shapely`, and `geodatasets`, which `requirements.txt` has.
It also ships to readers inside `EDS_notebooks.zip`.

- [x] Rewrote it from what the notebooks actually import: Python 3.13
      (matching CI), conda-forge only, the chapter dependencies, then a
      commented group for the extra notebooks (`scikit-learn`, `plotly`,
      `xlrd`, `lxml`), with `statadict` from pip. `descartes` is gone; nothing
      uses it.
- [x] Added `statadict` to `requirements.txt`. Chapter 7 and `utils.py` need
      it; until now it was pip-installed from inside the notebook.
- [x] `make create_environment` / `update_environment` now use
      `environment.yml` (with mamba). They used to create an empty Python 3.11
      env.
- [x] Checked: `mamba env create` solves in about 1.5 minutes (pandas 3.0.6,
      numpy 2.5.3, geopandas 1.1.4). In that env the 14 chapter notebooks,
      `clustering`, and `geo_example` pass. `jupyter_intro` failed in every
      environment tried, including the old one; fixed in Task 17.
- [ ] `EDS_notebooks.zip` still contains the old `environment.yml` until the
      next `build.sh` run.

## Task 9: Reconcile the README with `jb/index.md`

**Status:** Done 2026-09-24. `jb/index.md` was current. After Task 3's link
fix, the README lacked only its cover image and the Lulu print notice. The
README is now the index plus two deliberate differences: it keeps the license
paragraph (GitHub doesn't show the site's footer), and it floats the cover
with `<img align="right">` (GitHub strips `style`). Also fixed the index typo
"The notebooks contains". That fix reaches the website at the next
`make publish-site`.

## Task 10: Test the solution notebooks too

**Status:** Done 2026-09-24. `make tests-soln` runs `soln/[01]*.ipynb`; CI runs it
on Ubuntu and macOS (not Windows, because of the `soln/utils.py` symlink).
`make tests` now includes `jupyter_intro.ipynb`. Locally: 15 and 14 passed.
`examples/` is still untested.

CI runs `pytest --nbmake [01]*.ipynb` on the generated student notebooks, in
which each solution cell is replaced by `# Solution goes here`. So the
solution code is never executed in CI, and neither is anything in
`examples/`. Add `soln/[01]*.ipynb` to `make tests`, and perhaps a separate
job for `examples/`.

A local run on 2026-09-23 (Python 3.13, clean export of `origin/v1` plus
`utils.py`) passed all 14 `soln/` notebooks in 3m 16s, so adding them
should not turn CI red.

Caveat: `soln/utils.py` is now a symlink (Task 6). Git on Windows checks
symlinks out as plain text files unless `core.symlinks` is enabled, so a
Windows leg that runs `soln/` notebooks would fail to import `utils`. Run the
`soln/` tests on Ubuntu and macOS only, or copy `utils.py` into `soln/` in the
workflow step.

## Task 11: Protect `v1`

**Status:** Done 2026-09-24.

The printed first edition links to Colab through `blob/v1/...`, and every
notebook downloads `utils.py` and `data/*` from `raw/v1/...`. Deleting `v1`
or force-pushing to it would break the printed book.

- [x] Tag the published state. Tags follow the print version numbers.
      `v1.0.1` (annotated) is on `4e3b461`, the last commit before print
      1.0.1 was finalized (Book repo `1ec3aca`, 2024-08-10). The 21 later
      commits (post-print fixes and this cleanup) are untagged until the next
      real release. The older `v1.0` tag is unrelated: it marks the
      April 2021 spring-course snapshot (`952704e`, same as the `spring2021`
      branch).
- [x] GitHub ruleset `23938388` ("Protect v1") blocks deletion and
      non-fast-forward pushes on `v1`, with no bypass actors, so it applies
      to the owner too. Normal pushes still work. Other branches are
      unaffected.
- [x] Note in `CLAUDE.md` (Task 15) that files under `data/` and `utils.py`
      on `v1` are downloaded by URL and must not move

## Task 12: Decide the policy on survey microdata in the repo

**Status:** Decided 2026-09-24: keep the extracts in `data/` as they are.
The notebooks download them from GitHub.

## Task 13: Prune stale tracked files at the top level

**Status:** Done 2026-09-24.

- `brfss_clean.ipynb` and `nsfg_clean.ipynb` → `archive/pre_v1_cleaning/`.
  They are the 2017 BRFSS and 2013–2015 NSFG predecessors of the
  `soln/clean_*` notebooks, not duplicates.
- `nsfg.hdf5`, `gss.hdf5`, `brfss.hdf5` removed from `v1`. No chapter used
  them; the chapters download `data/*.hdf`. The only user,
  `examples/correlation2.ipynb`, downloaded `brfss.hdf5` from `raw/master/`.
  It is now pinned to `raw/852dd2e/` (the same file) and passes.
- `central_limit.ipynb` and the three `pew_religion_*` files →
  `examples/`. `central_limit` passes there.
- `_config.yml` (a Jekyll theme) deleted: Pages serves from `gh-pages`.
- Kept, though nothing in the repo uses them, because images are the
  likeliest targets of outside links: `eds_interior_page.png`,
  `run_on_colab_small.png`, `machine_bias_table.png`.

## Task 14: Split `build.sh` into build and publish

**Status:** Done 2026-09-24. `build.sh` and `jb/build.sh` now only build;
`publish.sh` (commit message required) and `jb/publish.sh` push. Makefile
targets: `notebooks`, `publish MSG=...`, `site`, `publish-site`. Two fixes on
the way:

- `zip -r` added to the existing archive, so dropped files stayed in it. The
  zip is now rebuilt from scratch.
- The old `git add` list left out `EDS_notebooks.zip`, so the committed zip
  was still the one from `3342ec3` (2021-05-11, 16 files). The rebuilt zip
  (18 files, with the Python 3.13 `environment.yml`) is committed with this
  task.

Rebuilding changed none of the generated notebooks: they were already in step
with `soln/`.

`remove_soln.py` only processes `[01]*.ipynb`, so the published
`clustering.ipynb` (built from `soln/clustering_soln.ipynb`) keeps its 8
solutions. Decided 2026-09-24 to leave it that way.

`build.sh` regenerates the student notebooks, then immediately commits with
the message "Updating notebooks" and pushes. That is why so much of the
history has that message. A build step that stops before `git commit` would
allow a diff review and a test run first.

## Task 15: Write `CLAUDE.md`

**Status:** Done 2026-09-24. The Task 11 note (`data/` and `utils.py` must not
move) is in it.

Short working notes for this repo: `soln/` is canonical and the top-level
notebooks are generated; `v1` files are downloaded by URL; how to build,
test, and publish. MarriageNSFG's `CLAUDE.md` is the model.
Leave out its "Writing markdown" rules (unwrapped paragraphs, no bold);
they don't apply here (decided 2026-09-24).

Include the notebook-editing workflow (decided 2026-09-24). The `.ipynb` is the
canonical source. For non-trivial edits:

1. `jupytext --to md -o <scratch>/X.md soln/X.ipynb` (keep the `.md` out of
   the repo)
2. edit the `.md`
3. `jupytext --to ipynb --update -o soln/X.ipynb <scratch>/X.md`. `--update`
   keeps outputs and metadata; plain `--to ipynb` discards them.
4. `jupyter nbconvert --to notebook --execute --inplace soln/X.ipynb`
5. strip the per-cell `execution` timestamps that nbconvert adds
6. if an `examples/` copy is generated from it, regenerate that

## Task 16: Keep the 1e website at `/v1/` when v2 takes over

**Status:** Not started. Options in [site_versions.md](site_versions.md).
Needed before 2e publishes anything to the site, not before the `v2` branch
is created.

`/v1/` here is a folder in the `gh-pages` branch, which Pages keeps serving
from; it is not the `v1` git branch. `ghp-import -x v1` replaces only that
folder, while the current `jb/publish.sh` (no prefix) replaces the whole site.
Recommended: 2e at the root, 1e under `/v1/`, and a 2e publish step that
preserves `/v1/`.
