# Elements of Data Science, 2nd edition: planning notes

Status: draft for discussion, 2026-09-23.
See [repos.md](repos.md) for how the first-edition repos fit together.

## The idea

The second edition would be a **companion to *You Would Choose Now***
(YWCN, in `~/CultureWar`). It would still be an introduction to data science
for people with no programming experience. The change is its through line: every
part builds toward doing the kind of analysis YWCN does, and the book ends with
readers carrying out a simplified version of that analysis on a survey
question they choose.

Scope:

- **In:** Python from scratch; working with survey data (GSS and possibly
  ANES); weighted estimates; time series and smoothing; uncertainty from
  resampling; subgroup comparisons; birth cohorts; regression-based estimates
  of period and cohort effects.
- **Out:** the Bayesian models in YWCN (`model10`, the RW2 time model, PyMC).
  The book can say what those models add and point readers to YWCN.
- **Dropped:** the Recidivism case study (1e chapters 16–17).
- **Expanded:** the Political Alignment Case Study (1e chapters 14–15). It
  becomes the backbone of the second half instead of an add-on.

## What YWCN does, and simpler versions a beginner can build

YWCN uses a small set of figure types over and over, and it teaches readers
to interpret them in its Introduction. Each has a counterpart built only from
tools this book already teaches.

| YWCN analysis | How YWCN does it | EDS v2 version |
|---|---|---|
| Percent giving a response, by year, with a trend line and uncertainty band | Weighted GSS estimates (`wtsmerge` = `wtssall` filled with `wtssps`); period-only RW2 "time model" | Weighted percentage per year with `groupby`; LOWESS trend; band from a weighted bootstrap |
| Cohort trajectories, one line per birth year | `model10`: cohort × period model, additive, so lines cannot cross | Pivot table of birth cohort (binned by 5 or 10 years) × survey year; then an additive logistic regression with cohort and year terms. Additive on the log-odds scale means its lines cannot cross either, which is a useful point of comparison with YWCN |
| Cohort component and period component ("standardized" figures) | Posterior predictions averaged over a reference distribution | The same standardization done by hand: predict from the regression for each cohort (or year), averaged over a fixed distribution of the other variable |
| Changing minds vs. generational replacement | Decomposition from the cohort and period components | Counterfactuals: hold cohort composition fixed and see how much change is left, and the reverse |
| Men vs. women, by race, by political alignment | Separate subgroup fits, composed on shared axes | Separate fits per subgroup, plotted together |
| Feeling thermometers | ANES 0–100 ratings | Distributions of ratings (a natural fit for the Distributions chapter) and mean over time |

PACS's `generation.ipynb` already fits a period-plus-cohort logistic
regression and compares groups, so the capstone method has a working
prototype.

## Proposed outline

About 18 chapters in four parts. The "Source" column says where each chapter
starts from.

### Part I. From Python to Pandas

The programming progression from 1e stays. Examples shift toward survey data
where that costs little.

| # | Chapter | Source | Change for v2 |
|---|---|---|---|
| 1 | Variables and values | 1e ch 1 | Minor |
| 2 | Times and places | 1e ch 2 | Add age, birth year, and cohort arithmetic (`year - age`), which sets up Part IV |
| 3 | Lists and arrays | 1e ch 3 | Minor |
| 4 | Loops and files | 1e ch 4 | Keep *War and Peace*, or switch to reading a GSS codebook file |
| 5 | Dictionaries | 1e ch 5 | Add value labels (codes → response text) as an example |
| 6 | Plotting | 1e ch 6 | Minor |

### Part II. Exploring survey data

| # | Chapter | Source | Change for v2 |
|---|---|---|---|
| 7 | DataFrames | 1e ch 7 | Switch from NSFG to GSS |
| 8 | Distributions | 1e ch 8 | PMFs of categorical responses; CDFs of ANES feeling thermometers |
| 9 | Relationships | 1e ch 9 + PACS | Cross tabulation and pivot tables become central; keep a short scatter/correlation section |
| 10 | Cleaning and validation | PACS `01_clean` | Codebooks, missing data, "don't know" responses, recoding |

### Part III. Change over time

| # | Chapter | Source | Change for v2 |
|---|---|---|---|
| 11 | Time series and smoothing | PACS `02_polviews` | Percent per year; LOWESS |
| 12 | Survey weights and resampling | 1e ch 11–12 + PACS `resampling` | Why weights matter; weighted bootstrap |
| 13 | Uncertainty | 1e ch 12–13 | Bootstrap bands on time series. 1e's hypothesis-testing chapter is condensed into a section here, since YWCN does not use p-values |
| 14 | Groups over time | PACS `03_outlook`, `04_worldview` | Men vs. women, political alignment, pivot tables by year × group |

### Part IV. Generations

| # | Chapter | Source | Change for v2 |
|---|---|---|---|
| 15 | Birth cohorts | New, drawing on `generation.ipynb` | Cohort × year tables; crude cohort trajectories |
| 16 | Logistic regression | 1e ch 10 | Logistic regression becomes the main model, with categorical and polynomial terms and predictions |
| 17 | Period and cohort effects | New, drawing on `generation.ipynb` | Additive cohort + period model; standardization; changing minds vs. generational replacement; the simplifying assumption (no separate age effect) and what it costs |
| 18 | Case study: pick a question | PACS `05_alignment` + new | The full YWCN-style analysis of one GSS question the reader chooses (the PACS tradition). Closes by comparing results with the matching YWCN figure and saying what the Bayesian model adds |

Possible additions: an ANES chapter, if ANES data can be redistributed (see
the open questions); and an outro that maps chapters to YWCN chapters.

## Data

- **GSS:** build a public extract for EDS v2 from the same cumulative release
  YWCN uses (currently `gss7224_r3a`), with the same weight construction
  (`wtsmerge`). Then numbers in v2 can match YWCN's weighted estimates. The
  extract script should live in the EDS repo, not in `CultureWar`, which is
  private.
- **ANES:** YWCN's feeling thermometers come from the ANES cumulative data
  file. Check the ANES terms before putting an extract in a public repo.
- **Keep v2 independent of `CultureWar` code.** That repo is private and
  heavy (PyMC, a SLURM cluster pipeline). Share variable choices and figure
  conventions, not imports.
- **Retire 1e datasets** that no longer carry a chapter (NSFG, BRFSS) unless a
  Part I or II example still needs them.

## Repository organization

### Requirements, whatever the choice

1. **The `v1` branch of this repo must stay unchanged for good.** The printed
   first edition and every 1e notebook link to
   `colab.research.google.com/github/AllenDowney/ElementsOfDataScience/blob/v1/...`,
   and every notebook downloads `utils.py` from `.../v1/utils.py`. Deleting or
   rewriting `v1` breaks the printed book.
2. **Use one repo for v2, not three.** In 1e, content moves between this repo,
   the Solutions repo, and the Book repo by `rsync` to hard-coded local
   paths. For v2, keep the solution notebooks (`soln/`, canonical), the
   generated student notebooks, the website, and the book build in one place.
   Since the print build is being revised anyway, v2 could use the same MyST
   → PDF/EPUB toolchain as YWCN (`book/`, Leanpub editions) instead of the
   LaTeX pipeline.

### Options

**A. A `v2` branch in this repo, made the default branch.** This is the
pattern `ThinkStats` (default branch `v3`) and `ThinkPython` (default branch
`v3`) already use.

- *For:* the repo URL, stars, watchers, and issue history carry over. The
  website URL `allendowney.github.io/ElementsOfDataScience` stays the same.
  You already use this pattern.
- *Against:* GitHub Pages serves one site per repo. If v2 takes over the
  site, 1e website readers lose it unless the deploy publishes 1e under a
  subpath such as `/v1/`. That means changing the deploy script, because
  `ghp-import` as used now replaces the whole site. Issues from both editions
  share one tracker (labels can separate them). The v2 tree will differ a lot
  from v1, so the branches share history but little content.

**B. A new repo** (for example `ElementsOfDataScience2`, the `ThinkStats2`
pattern, or a name tied to YWCN).

- *For:* a clean start, built for the new toolchain and one-repo layout from
  day one. Each edition gets its own website with no deploy changes. 1e
  stays exactly as it is. No branch is involved for anyone.
- *Against:* a new URL, and stars and issues start from zero. This repo's
  README and website need a clear "second edition is here" banner, or
  readers who find the 1e repo through search won't know v2 exists. That
  makes one more repo, though if you take requirement 2, it replaces two
  (Book and Solutions) for v2 purposes.

Two options not recommended: a `v2/` directory on this repo's current branch
(long, confusing paths, and the 1e files stay in the main view), and a branch
of the Book repo (that repo is only the LaTeX build).

### On readers having to navigate branches

In practice, casual readers rarely see a branch:

- They arrive through the website, a Colab link, the Green Tea Press page, or
  the README. None of these asks them to pick a branch.
- GitHub shows the **default branch** to anyone who opens the repo. Under
  option A, v2 readers see v2 without doing anything.
- 1e readers following links in the printed book land on `v1` because the
  link names it.

The people who would have to use the branch dropdown are 1e readers who
browse the repo or website **without** a link from the book. A README line
("Looking for the first edition? It's on the `v1` branch, and the 1e website
is at `/v1/`") and a matching banner on the website cover them.

So the worry is manageable under option A, provided the default branch is v2
and the 1e website stays up. The real cost of A is the versioned website
deploy, not reader navigation.

### Decision (2026-09-23): option A

The second edition keeps the title *Elements of Data Science*, which already
has some brand recognition. So v2 is a **`v2` branch in this repo, made the
default branch** once it is ready to be seen, following ThinkStats and
ThinkPython. It needs a README note and a website that keeps 1e at `/v1/`.

Following requirement 2, the `v2` branch holds everything for v2. The Book and
Solutions repos stay 1e-only.

The cleanup to do on `v1` before creating the branch is tracked in
[PROJECT_BOARD.md](PROJECT_BOARD.md).

## Open questions

1. ~~Title~~: decided, it stays *Elements of Data Science*, so v2 is a
   `v2` branch (option A). A subtitle naming the YWCN connection is still
   possible.
2. Timing relative to YWCN: does v2 wait for YWCN's variable list and figure
   style to settle, or grow alongside it and adjust later?
3. How closely should the case study match YWCN? For example, the capstone
   could reproduce the "people would try to be fair" example from YWCN's
   Introduction as closely as the simpler methods allow.
4. ANES: can an extract go in a public repo? If not, is ANES optional in v2
   or left out?
5. Part I: keep *War and Peace* and the other non-survey examples as a
   change of pace, or move everything to survey data?
6. Hypothesis testing: condense it (as proposed), keep a full chapter, or
   drop it?
7. Publishing: Leanpub and a print edition like YWCN, the Lulu/Green Tea Press
   route of 1e, or both?

## Suggested next steps

1. Finish the `v1` cleanup on the [project board](PROJECT_BOARD.md), then
   create the `v2` branch with a `soln/` + generated notebooks + `book/`
   layout.
2. Build the v2 GSS extract script and check that its weighted yearly
   percentages match YWCN's for one or two variables.
3. Prototype chapter 17 first by cleaning up `generation.ipynb`. It is the
   hardest new material, and if it works, the rest of the outline is mostly
   adapting existing chapters.
4. Write a one-page map of each v2 chapter to the YWCN chapters and figures
   it prepares readers for.
