# Working in this repo

*Elements of Data Science* (EDS): an introduction to data science for people
with no programming experience, as Jupyter notebooks that readers run on
Colab. The first edition is in print (Lulu), and a second edition is planned
as a companion to *You Would Choose Now* (`planning/v2_plan.md`).

`planning/PROJECT_BOARD.md` holds the numbered tasks and is the place to
record findings; `planning/` also holds the longer write-ups, including
`repos.md`, which explains how this repo relates to ElementsOfDataScienceBook
(the LaTeX manuscript) and ElementsOfDataScienceSolutions (retired).

## `v1` is published, and printed links point into it

The printed first edition links to Colab through `blob/v1/...`, and every
notebook downloads `utils.py` and files in `data/` from `raw/v1/...`. So:

- Never delete `v1`, rewrite its history, or force-push it. A GitHub ruleset
  blocks deletion and non-fast-forward pushes (Task 11).
- Don't move or rename `utils.py`, anything in `data/`, or the top-level
  chapter notebooks. Removing a file from `v1` breaks every copy of the book
  that points to it.
- Tags follow the print version numbers: `v1.0.1` is the state at the 1.0.1
  print release. The older `v1.0` tag is an unrelated 2021 course snapshot.

## Layout

```
soln/        the source: chapter notebooks with solutions (canonical), plus
             the data-cleaning notebooks (clean_*.ipynb) and extras
[01]*.ipynb  generated: chapter notebooks with solutions removed (by build.sh)
utils.py     canonical; soln/utils.py and jb/utils.py are symlinks to it
data/        data files the notebooks download from raw/v1/data/
examples/    supplementary notebooks. Two are generated from soln/ with the
             solutions removed: odds (from soln/odds_soln) and
             resampling_example_gun (from the same name in soln/)
jb/          Jupyter Book website (build.sh, publish.sh, _toc.yml)
figs/        static figures; the print book's pipeline copies from here
archive/     kept for the record (video scripts, quizzes, pre-v1 cleaning
             notebooks); unused
planning/    project board and write-ups
```

## Build, test, publish

The build steps only change the working tree; the publish steps push, and
pushing is what readers see.

```bash
make notebooks          # build.sh: soln/ -> [01]*.ipynb, rebuild EDS_notebooks.zip
make tests              # student notebooks + jupyter_intro
make tests-soln         # notebooks with solutions (CI skips this on Windows)
make publish MSG="..."  # publish.sh: commit and push the generated files
make site               # jb/build.sh: build the website into jb/_build/html
make publish-site       # jb/publish.sh: ghp-import, replaces the live site
```

Never run a publish target as a way to test something. Edit `soln/`, never
the generated top-level notebooks; `make notebooks` overwrites them.

`remove_soln.py` replaces every code cell that starts with `# Solution` (or
is tagged `solution`) with `# Solution goes here`, clears outputs, and keeps
only `raises-exception` tags. It processes `[01]*.ipynb` only, so
`clustering.ipynb` keeps its solutions.

## Editing notebooks: the `.ipynb` is the source

There is no jupytext pairing, and no `.md` copies are committed. For anything
beyond a trivial edit, go through markdown and back:

```bash
jupytext --to md -o /tmp/X.md soln/X.ipynb       # keep the .md out of the repo
# edit /tmp/X.md
jupytext --to ipynb --update -o soln/X.ipynb /tmp/X.md
jupyter nbconvert --to notebook --execute --inplace soln/X.ipynb
```

- `--update` keeps existing outputs and metadata; plain `jupytext --to ipynb`
  discards every output.
- After `nbconvert`, strip the per-cell `execution` timestamps it adds.
- Before committing executed outputs, check that no output recorded a local
  path. A `pip install` fallback cell does this when a package is missing.
- If an `examples/` notebook is generated from the one you edited, regenerate
  it.

A cell that is meant to raise needs the `raises-exception` tag, or nbmake
fails it. That includes cells using the `%%expect` magic from `utils.py`.

## Changes that could move data

The cleaning notebooks in `soln/` build the files in `data/`. Rebuild in a
scratch directory and compare with the committed file before replacing it:

```python
import pandas as pd
pd.testing.assert_frame_equal(pd.read_hdf("scratch/gss_eda.hdf", "gss"),
                              pd.read_hdf("data/gss_eda.hdf", "gss"))
```

Task 19 used this to verify the pandas 3 fixes: five files came out
identical.

## Traps

pandas 3 (copy-on-write) makes a chained in-place call a silent no-op:
`df['col'].replace(..., inplace=True)` and `df.col.replace(..., inplace=True)`
leave `df` unchanged. Nothing raises, so tests don't catch it. Assign
instead: `df['col'] = df['col'].replace(...)`. pandas 3 also makes the key of
`to_hdf` keyword-only (`to_hdf(path, key='gss')`).

`utils.py` calls `get_ipython()` at import, so it only imports inside
Jupyter or IPython. To test it from a script, run the script with `ipython`.

Chapters 4–6 open `2600-0.txt` without an encoding, which fails under
Windows' default cp1252. CI sets `PYTHONUTF8=1`.

Several notebooks download their data from other repos (for example, the
Political Alignment Case Study). When a download 404s, pin the URL to the
last commit that had the file rather than to a branch.

## Environment

`environment.yml` (Python 3.13, conda-forge) is for local use and ships in
`EDS_notebooks.zip`. `requirements.txt` has the same chapter dependencies for
pip, and CI installs `requirements-dev.txt`. Keep the two in step.

```bash
make create_environment   # mamba env create -f environment.yml
make update_environment
```
