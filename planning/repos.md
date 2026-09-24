# How the Elements of Data Science repositories fit together

*Elements of Data Science* comes from three repositories, plus two case-study
repositories that supply the last four chapters of the printed book.

| Local path | GitHub | Visibility | Default branch | Role |
|---|---|---|---|---|
| `~/ElementsOfDataScience` (this repo) | [AllenDowney/ElementsOfDataScience](https://github.com/AllenDowney/ElementsOfDataScience) | public | `v1` | Student notebooks, Colab links, data, figures, Jupyter Book website |
| `~/ElementsOfDataScienceSolutions` | AllenDowney/ElementsOfDataScienceSolutions | **private** | `master` | Older copy of the solution notebooks; data-cleaning notebooks and quizzes |
| `~/ElementsOfDataScienceBook` | [AllenDowney/ElementsOfDataScienceBook](https://github.com/AllenDowney/ElementsOfDataScienceBook) | public | `main` | LaTeX manuscript of the printed book and the notebook→LaTeX pipeline |
| `~/PoliticalAlignmentCaseStudy` | AllenDowney/PoliticalAlignmentCaseStudy | public | — | Book chapters 14–15 |
| `~/RecidivismCaseStudy` | AllenDowney/RecidivismCaseStudy | public | — | Book chapters 16–17 |

## Data flow

```
                ElementsOfDataScience/soln/  (notebooks with solutions; canonical)
                  │       older copy in ElementsOfDataScienceSolutions
                  │
      ┌───────────┼──────────────────────────────┐
      │           │                              │
      ▼           ▼                              ▼
 build.sh     jb/build.sh                  Book/convert/build.sh
 (remove_soln) (prep_notebooks:            (+ case-study notebooks,
      │         tag solutions               + figs/ from this repo)
      │         remove-cell)                     │
      ▼           ▼                              ▼
 top-level     gh-pages branch             latex/*.tex → latex/main.tex
 01..14_*.ipynb allendowney.github.io/      → print book (No Starch
 + EDS_notebooks.zip  ElementsOfDataScience   class, Lulu paperback)
 (Colab / download)   (online book)
```

All three outputs start from the same notebooks. Solution cells begin with
`# Solution` (or carry a `solution` tag), and each pipeline handles them in its
own way:

- **Student notebooks** (this repo, top level): `remove_soln.py` replaces each
  solution with `# Solution goes here`, clears outputs, and removes every tag
  except `raises-exception`.
- **Website** (`jb/`): `prep_notebooks.py` tags solution cells `remove-cell`,
  so Jupyter Book hides them.
- **Print book** (`ElementsOfDataScienceBook/convert/`): runs each notebook with
  `pytest --nbmake --overwrite`, removes solutions, clears cells tagged
  `remove-*`/`hide-*`, then converts with `nbconvert` → Markdown → `pandoc` →
  LaTeX, and post-processes with `split.py`.

## 1. ElementsOfDataScience (this repo)

This is the public home of the book: readers use it, it holds the Colab links,
and the website is built from it.

- `01_variables.ipynb` … `14_outro.ipynb`: the chapter notebooks with solutions
  removed. The README and the notebook headers link to these on Colab. They
  are generated files; edit the solution notebooks, not these.
- `soln/`: the notebooks with solutions, and the canonical copy of them
  (added May 2025). `build.sh` reads from here.
- `build.sh`: copies `soln/` to the top level, runs `remove_soln.py`, rebuilds
  `EDS_notebooks.zip`, then commits and pushes.
- `jb/`: the Jupyter Book site. `jb/build.sh` copies `soln/` plus
  `examples/resample_logit.ipynb` and `examples/anderson.ipynb`, hides the
  solutions, runs `jb build`, and uses `ghp-import` to publish to `gh-pages`
  (https://allendowney.github.io/ElementsOfDataScience/).
- `utils.py`: helper module that each notebook downloads from
  `raw.githubusercontent.com/.../v1/utils.py`, so it must stay on `v1`.
- `figs/`: static figures. The Book pipeline copies these with `rsync`.
- `examples/`, `unfilled/`: extra exercises and teaching notebooks that are
  not in the printed book.
- Data files (`*.hdf5`, `data/`) and `*_clean.ipynb` notebooks that prepare
  them.
- `.github/workflows/tests.yml`: runs `make tests` (`pytest --nbmake [01]*.ipynb`)
  on each push to `v1` and once a month.

Branches: `v1` is the current branch (the default branch, and the one the
notebooks link to). `master` holds the pre-publication version, last updated
March 2024, with chapter names such as `11_inference`. `spring2021` is an old
course snapshot. `gh-pages` holds the built website.

## 2. ElementsOfDataScienceSolutions (private)

This repo holds an older copy of the chapter notebooks with solutions. It was
the source for the other two repos from 2020 to 2024; `soln/` in this repo has
replaced it as the canonical copy.

- `01_variables.ipynb` … `14_outro.ipynb` hold the same content as
  `soln/` here. As of this writing, 13 of the 14 are identical.
  `07_dataframes.ipynb` differs in one line, and `soln/` has the newer version.
- `clean_*.ipynb` notebooks build the NSFG, GSS, and BRFSS data extracts that
  the chapters download.
- `header.ipynb` and `add_header.py` prepend the standard "Run on Colab /
  download utils" cells to each notebook.
- `scrub_code.py` and `scrub.sh` are older versions of `remove_soln.py`. They
  still use the old `*_soln.ipynb` names and wrote into a parent directory.
- `quizzes/` holds `quiz01`–`quiz07` with their data files. These appear only
  here.
- `manuscript/` is tracked in git but deleted in the working tree. It holds
  Markdown chapters left from an earlier build.

This repo used to be cloned **inside** this one, at
`~/ElementsOfDataScience/ElementsOfDataScienceSolutions/`. The Book's
`convert/build.sh` still reads from that path. Commit `5aecb48` ("Removing
solutions that weren't supposed to be here") deleted two notebooks from that
nested path after they were committed to this repo by mistake. Since May 2025
the solutions have lived in `soln/` instead, and the most recent notebook
changes were made there rather than in the Solutions repo.

## 3. ElementsOfDataScienceBook

This repo holds the LaTeX manuscript of the printed book. It is frozen at
**Version 1.0.1** (August 2024) and has tag-like commits `Version 1.0.0` and
`Version 1.0.1`.

- `latex/main.tex` is the current master file. It uses `nostarch.cls`, and
  its settings, fonts, and index are in `latex/`. It `\input`s 18 chapters in
  five parts:
  1. *From Python to Pandas*: 01–06
  2. *Exploratory Data Analysis*: 07–10
  3. *Statistical Inference*: 11–13
  4. *Case Study: Political Alignment*: 14 `polviews`, 15 `outlook`
  5. *Case Study: Recidivism*: 16 `classification`, 17 `calibration`

  plus 18 `outro`.
- `convert/` holds the notebook→LaTeX pipeline (`build.sh`, `add_header.py`
  with `header_latex.ipynb`, `remove_soln.py`, `remove_cells.py`, `split.py`).
  `build.sh` gathers its inputs from:
  - `~/ElementsOfDataScience/ElementsOfDataScienceSolutions/[01]*.ipynb`
    (chapters 1–13; `14_outro` is renamed to `18_outro`)
  - `~/PoliticalAlignmentCaseStudy/02_polviews_soln.ipynb` → `14_polviews`,
    `03_outlook.ipynb` → `15_outlook`
  - `~/RecidivismCaseStudy/01_classification.ipynb` → `16_classification`,
    `02_calibration.ipynb` → `17_calibration`
  - `~/ElementsOfDataScience/figs` and `utils.py`
- `chapters/` holds generated `.tex` files from an earlier layout, including
  the old names `11_inference`, `02_polviews`, and `01_classification`.
  `main.tex`, `preamble.tex`, and `old/` at the top level are also earlier
  versions. Use `latex/`.
- `cover/`, `fonts/`, `images/`: cover files (ISBN 978-0-9716775-1-7, Lulu
  template) and the typefaces.
- Branches: `nostarch` and several `overleaf-*` branches remain from editing
  in Overleaf.

The printed book is therefore a superset of the notebooks: it adds four
case-study chapters that come from other repos. In the notebook repos, the
last chapter is `14_outro`; in the printed book it is chapter 18.

## Keeping them in sync

Typical edit → publish sequence:

1. Edit the solution notebook in `soln/`.
2. In this repo, run `./build.sh` to regenerate the student notebooks and the
   zip, then commit and push to `v1`. CI tests the result.
3. Run `cd jb && ./build.sh` to rebuild and publish the website.
4. For a new print edition, run `convert/build.sh <notebooks>` in the Book
   repo, then `make` in `latex/`.

Things to watch for:

- **`soln/` in this repo is the canonical copy of the solutions.** The
  Solutions repo is an older copy that may lag behind; for example, it has an
  older version of `07_dataframes.ipynb`. Make edits in `soln/`.
- **The solutions are public, on purpose.** `soln/` is pushed to the public
  `v1` branch even though the Solutions repo is private.
- **The Book's `convert/build.sh` path is out of date.** It reads from
  `~/ElementsOfDataScience/ElementsOfDataScienceSolutions/`, which no longer
  exists. The print build will be revised anyway.
- **Links are pinned to the `v1` branch.** Notebook headers, `utils.py`
  downloads, and the README's Colab and download links all use `v1`.
