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

### Current focus (2026-09-23)

Getting `v1` into a clean state before creating the `v2` branch. The second
edition keeps the title, so v2 will be a branch of this repo, made the default
once it is ready (see [v2_plan.md](v2_plan.md)).

- **Done:** **Task 1** (repo survey), **Task 3** (README links), **Task 4** (test workflow; CI green on all three OSes), **Task 5** (working tree: 147 paths → 21 in limbo), **Task 6** (`soln/` self-contained), **Task 11** (`v1.0.1` tag; `v1` protected), **Task 8** (`environment.yml`), **Task 17** (`jupyter_intro` passes)
- **Next:** Task 7
- **Before branching:** Task 7
- **Worth doing, not blocking:** Tasks 9, 10, 13, 14, 15
- **v2 prep:** Tasks 12, 16

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

**Status:** Not started.

The Solutions repo has an older version of `07_dataframes.ipynb`, and its
`manuscript/` directory is deleted locally but still tracked.

- [ ] Move anything it has that this repo lacks (`quizzes/`, the
      `clean_brfss-*` notebooks) into `soln/`, or decide to leave it behind
- [ ] Add a README note pointing to `soln/` here; consider archiving the
      repo on GitHub

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

**Status:** Not started.

The two started as the same text and have drifted. `jb/index.md` mentions the
printed edition (Lulu) and has the cover; the README does not, lists only
notebooks 1–13, and still calls the book "a work in progress". Pick one as
the source and update the other.

## Task 10: Test the solution notebooks too

**Status:** Not started.

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

**Status:** Done 2026-09-24, except the `CLAUDE.md` note, which waits for
Task 15.

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
- [ ] Note in `CLAUDE.md` (Task 15) that files under `data/` and `utils.py`
      on `v1` are downloaded by URL and must not move

## Task 12: Decide the policy on survey microdata in the repo

**Status:** Not started. Decision needed.

`data/` holds respondent-level extracts from NSFG, BRFSS, and GSS, and the
notebooks download them from GitHub. In MarriageNSFG the NSFG files were
purged because the public-use files may not be redistributed. For `v1`,
removing them would break the printed book's notebooks, so this is mostly a
question for v2: download from the source at run time, or keep extracts
that the terms allow (GSS). ANES (see [v2_plan.md](v2_plan.md)) raises the
same question.

## Task 13: Prune stale tracked files at the top level

**Status:** Not started. Low priority.

Pre-v1 files are still tracked at the top level: `nsfg.hdf5`, `gss.hdf5`,
`brfss.hdf5`, `brfss_clean.ipynb`, `nsfg_clean.ipynb`, `central_limit.ipynb`,
the `pew_religion_*` files, a Jekyll `_config.yml`, and `machine_bias_table.png`
(deleted in the working tree, with a copy in `figs/`). No current notebook
references them, but outside links might, so check before removing.

## Task 14: Split `build.sh` into build and publish

**Status:** Not started. Optional.

`build.sh` regenerates the student notebooks, then immediately commits with
the message "Updating notebooks" and pushes. That is why so much of the
history has that message. A build step that stops before `git commit` would
allow a diff review and a test run first.

## Task 15: Write `CLAUDE.md`

**Status:** Not started.

Short working notes for this repo: `soln/` is canonical and the top-level
notebooks are generated; `v1` files are downloaded by URL; how to build,
test, and publish. MarriageNSFG's `CLAUDE.md` is the model.

## Task 16: Keep the 1e website at `/v1/` when v2 takes over

**Status:** Not started. v2 prep; needed before `v2` becomes the default branch.

GitHub Pages serves one site per repo, and `jb/build.sh` publishes with
`ghp-import`, which replaces the whole site. Before v2 publishes, change the
deploy so the 1e build lives at `/v1/`, and add a banner to each site
pointing to the other.

## Task 17: Tag the `%%expect` cell in `jupyter_intro`

**Status:** Done 2026-09-24. Tag added in `soln/` and copied to the top level;
passes under nbmake in both the pip and the `environment.yml` environments.
Consider adding `jupyter_intro.ipynb` to `make tests` along with Task 10.

`jupyter_intro.ipynb` fails under nbmake in every environment tried. Cell 12
(`%%expect SyntaxError` / `abs 42`) uses the magic from `utils.py`, which runs
the cell with `run_cell`, so the `SyntaxError` is recorded as an error output
and nbmake counts that as a failure. The chapter notebooks avoid this because
their `%%expect` cells carry the `raises-exception` tag, which
`remove_soln.py` preserves. Add the tag to that cell in
`soln/jupyter_intro.ipynb` (the build copies it to the top level). CI does
not run `jupyter_intro`, so nothing is red today.
