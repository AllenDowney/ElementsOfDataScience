# Working tree triage (Task 5)

## Outcome (2026-09-24)

Done in `2151a4e`..`718a97c`. `git status` went from 147 paths to 22. The
tables below are the original plan; the outcome differs from it in these
ways:

- `machine_bias_table.png` was **restored** at the top level, not left
  deleted, because it is identical to the `figs/` copy and outside links may
  use `raw/v1/machine_bias_table.png`. The `figs/` copy is tracked too.
- Of the Recidivism figures, only `figs/calibration1.png` and
  `figs/machine_bias_table.png` were tracked. They are the two the print book
  includes. `confusion_matrix{1,2}.png` are not referenced, so they are in limbo.
- `figs/resampling_alternative.{png,svg}` are referenced nowhere, so they are
  in limbo.
- `soln/GSS.dat.gz` needed an extra rule (`soln/*.dat.gz`), and the
  `data/*FemPreg*` rule was narrowed so it does not match the tracked codebook
  PDF.
- Deleted files were checked first. `soln/jntools.py`, `soln/test.sh`, and
  `soln/remove_header.py` are identical to copies in
  `~/ElementsOfDataScienceSolutions`, and `remove_header.py` was tracked, not
  deleted. The deleted `prep_notebooks.py` differed from `jb/prep_notebooks.py`
  only in its glob. `Untitled.ipynb` had no cells.
- `eds.gss.hdf5` and `nsfg_sample.hdf5` are now ignored by `/*.hdf5`, not in
  limbo. They are still on disk.

**Left in limbo (16 paths).** Since the first pass, `scripts/` moved to
`archive/video_scripts/`, and Task 7 dealt with the `soln/` extras and
`examples/odds_soln.ipynb`:

| Path | Why it is waiting |
|---|---|
| `EDS_notebooks.zip` (modified) | Commit with the next `build.sh` run |
| `examples/scrub_code.py` | Duplicate of the Solutions repo's `scrub_code.py` |
| `unfilled/04_worldview.ipynb`, `unfilled/build.sh`, `unfilled/remove_soln.py` | Belong in PACS, or in v2 |
| `figs/confusion_matrix{1,2}.png`, `figs/resampling_alternative.{png,svg}` | Not referenced anywhere |
| `eds_cover_small.png` | Not referenced anywhere |
| `feedback/` | Early copies of chapters 1–2 |
| `hypothesis.ipynb`, `trig.ipynb`, `family_survey.ipynb`, `deaths2008.csv`, `all_sandwich_data.csv` | Old experiments (2019–2020) |

## Original plan

Snapshot 2026-09-23: `git status` lists 147 paths, of which 13 are modified or
deleted tracked files and 134 are untracked. This file proposes what to do
with each one. "Runtime download" means a notebook fetches the file into its
working directory when it runs. The 2026-09-23 local test run of the top-level
notebooks, in a clean export of `origin/v1`, created exactly these:
`2600-0.txt`, `2015_2017_FemPregData.dat`, `2015_2017_FemPregSetup.dct`,
`brfss.hdf`, `brfss_2021.hdf`, `gss_extract_2022.hdf`, and `nsfg.hdf`.

Actions: **track** (commit it), **ignore** (add to `.gitignore`), **delete**,
**restore** (`git restore`, discarding the local change), **limbo** (leave it
for now, and say why).

## Modified or deleted tracked files

| Path | What changed | Action |
|---|---|---|
| `README.md` | Task 3 link fix | track |
| `jb/index.md`, `jb/_config.yml` | The Lulu print-edition notice and cover, `v1` links, repository button pointing to `tree/v1`. The live site was probably built from this uncommitted version | track |
| `examples/resample_logit.ipynb`, `examples/correlation2.ipynb` | Real text edits ($\rho$ → $r$, number formatting, citation order) plus re-execution | track |
| `examples/anderson.ipynb`, `examples/cocoa_soln.ipynb` | Added `savefig` calls; the PNGs they write are untracked (below) | track, or restore if the figures were one-off |
| `examples/air_pollution_soln.ipynb` | Re-executed outputs | review, then track or restore |
| `examples/resampling.ipynb`, `examples/vaccine.ipynb` | Kernel metadata only | restore |
| `brfss.hdf5` | Binary rewrite, same size; pre-v1 file (Task 13) | restore |
| `EDS_notebooks.zip` | Rebuilt by `build.sh` | track with the next build |
| `machine_bias_table.png` | Deleted; an untracked copy is in `figs/` | limbo until Task 13 (outside links may use the top-level path) |

## Untracked: website build (`jb/`)

| Path | Action | Why |
|---|---|---|
| `jb/_toc.yml`, `jb/build.sh`, `jb/prep_notebooks.py` | **track** | The site cannot be rebuilt without them |
| `jb/_build/` (45 MB) | ignore | Build output |
| `jb/[01]*.ipynb`, `jb/anderson.ipynb`, `jb/resample_logit.ipynb`, `jb/utils.py` | ignore | Copied in by `jb/build.sh` |
| `prep_notebooks.py` (top level) | delete | Older duplicate of `jb/prep_notebooks.py` |

## Untracked: `soln/` (see Task 6)

| Path | Action | Why |
|---|---|---|
| `soln/utils.py`, `soln/jupyter_intro.ipynb`, `soln/geo_example.ipynb`, `soln/clustering_soln.ipynb` | **track** | `build.sh` copies them |
| `soln/clean_*.ipynb`, `soln/brfss_validate.ipynb` | **track** | They build the files in `data/` |
| `soln/header.ipynb`, `soln/add_header.py`, `soln/remove_header.py` | track | Notebook header tooling |
| `soln/odds_soln.ipynb`, `soln/testing_means_soln.ipynb`, `soln/resampling.ipynb`, `soln/resampling_example_gun.ipynb` | limbo | Extra exercises; decide with Task 7 |
| `soln/*.dat`, `*.dct`, `*.ASC.gz` (BRFSS, 163 MB), `*.hdf`, `*.hdf5`, `*.tar.gz`, `2600-0.txt`, `penguins_raw.csv` | ignore | Raw inputs and runtime downloads |
| `soln/fig09-*.pdf`, `soln/fig09-*.png` | ignore | Figure output |
| `soln/README.md`, `soln/LICENSE`, `soln/build.sh`, `soln/test.sh`, `soln/rename.py`, `soln/scrub.sh`, `soln/scrub_code.py`, `soln/jntools.py` | delete | Left over from copying the Solutions repo in; superseded by the top-level scripts |
| `soln/scrub_code.py~` | delete | Editor backup |

## Untracked: runtime downloads and data at the top level

| Path | Action |
|---|---|
| `2600-0.txt`, `2015_2017_FemPreg*`, `brfss.hdf`, `brfss_2021.hdf`, `nsfg.hdf`, `gss_extract_2022.hdf` | ignore (runtime downloads, confirmed by the test run) |
| `GSS.dat.gz`, `GSS.dct`, `gss_eda.hdf` | ignore. Local copies of files tracked in `data/`; the chapter notebooks do not create them |
| `examples/brfss.hdf5`, `examples/gss_eda.hdf`, `examples/*.csv`, `examples/*.xls` | ignore (runtime downloads in `examples/`) |
| `data/2013_2015_FemPreg*`, `data/2015_2017_FemPreg*`, `data/CodebookPDFs_Nov2020/` (43 MB), `data/GSS.do`, `data/brfss_2019.hdf`, `data/gss_eda.tar.gz` | ignore, using explicit paths. `data/` itself stays tracked, because notebooks download from it |
| `eds.gss.hdf5` (158 MB), `nsfg_sample.hdf5` | limbo, then ignore or delete. Old extracts; nothing references them |
| `nlsy97/` (16 MB) | ignore. NLSY97 extract for an unfinished example |

## Untracked: other

| Path | Action | Why |
|---|---|---|
| `DS10-Python-HW/` (92 MB) | ignore | A separate clone of `stat10/DS10-Python-HW` |
| `figs/resampling_alternative.{png,svg}` | track | Figure source from 2024; check where it is used |
| `figs/calibration1.png`, `figs/confusion_matrix{1,2}.png`, `figs/machine_bias_table.png` | track | Probably figures for the Recidivism chapters of the print book; the Book pipeline copies all of `figs/` |
| `examples/anderson{1,2}.png`, `examples/cocoa{1,2}.png` | ignore | Written by the `savefig` calls above |
| `examples/odds_soln.ipynb`, `examples/scrub_code.py` | limbo | Duplicates of files in `soln/` |
| `examples/scrub_code.py` | Duplicate of the Solutions repo's `scrub_code.py` |
| `unfilled/04_worldview.ipynb`, `unfilled/build.sh`, `unfilled/remove_soln.py` | limbo | An unfilled copy of PACS `04_worldview`; belongs in PACS, or in v2 |
| `eds_cover_small.png` | limbo | Not referenced anywhere yet |
| `scripts/` (chapter script text files and a zip) | limbo | Purpose unclear |
| `feedback/` | limbo | Early copies of chapters 1–2, apparently for collecting feedback |
| `hypothesis.ipynb`, `trig.ipynb`, `family_survey.ipynb`, `deaths2008.csv`, `all_sandwich_data.csv` | limbo | Old experiments (2019–2020) |
| `Untitled.ipynb`, `mv.sh` | delete | Scratch files |
| `planning/` | **track** | This folder |

## Proposed `.gitignore` additions

```gitignore
# separate repos cloned inside this one
DS10-Python-HW/

# website build: output, and files copied in by jb/build.sh
jb/_build/
jb/*.ipynb
jb/utils.py

# data the notebooks download when they run (top level and subfolders);
# data/ itself is tracked because notebooks download from it on GitHub
/*.hdf
/*.hdf5
!/brfss.hdf5
!/gss.hdf5
!/nsfg.hdf5
/2600-0.txt
/*FemPreg*
/GSS.dat.gz
/GSS.dct
soln/*.hdf
soln/*.hdf5
soln/*.dat
soln/*.dct
soln/*.ASC.gz
soln/*.tar.gz
soln/2600-0.txt
soln/penguins_raw.csv
soln/fig*.pdf
soln/fig*.png
examples/*.hdf
examples/*.hdf5
examples/*.csv
examples/*.xls
examples/*.png

# raw inputs kept locally
data/*FemPreg*
data/CodebookPDFs_*/
data/GSS.do
data/brfss_2019.hdf
data/gss_eda.tar.gz
nlsy97/

# editor backups
*~
```

The `!` lines keep the three pre-v1 top-level HDF files tracked until Task 13
decides their fate. `examples/*.csv` would hide any CSV an example is meant to
ship, but none is tracked there now.
