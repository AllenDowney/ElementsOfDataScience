# PDF and EPUB from the notebooks (Task 22)

Status: phases 1–4 done 2026-10-27; automated QA done 2026-10-28 ("QA
results"). Next: Allen's proofread, then the first LeanPub upload.

## Goal

Sell *Elements of Data Science* on LeanPub as a PDF and an EPUB,
pay-what-you-want with a $0 minimum (GreenTeaPress Task 18). Readers will
read both formats on screens, so lines should be shorter than in the print
book. Build them with a pipeline that can also produce the v2 print edition,
as [v2_plan.md](v2_plan.md) proposes ("v2 could use the same MyST →
PDF/EPUB toolchain as YWCN").

## What exists now

**The 1e print pipeline** (`~/ElementsOfDataScienceBook`, see
[repos.md](repos.md)): notebooks → `pytest --nbmake --overwrite` (with a
header cell that makes DataFrames render as LaTeX) → `remove_soln.py` →
`nbconvert --to markdown` → `pandoc --listings` → `split.py` (regex fixes)
→ `latex/main.tex` with `nostarch.cls`. Facts that matter here:

- Page: Lulu crown quarto, 189 × 246 mm, text block 144 mm (5.7 in) wide.
  290 pages. The wide block keeps the page count down; at 10 pt it gives
  long prose lines.
- Code styling is in `latex/settings.tex`: `listings`, with EDS colors
  (`codeblue`, `codegreen`, `codered`, `codepurple`), source in a framed gray
  box, output in a borderless gray box. CultureWar's PDF already uses the
  same purple and blue.
- **The index exists only in the generated `.tex`.** There are 659
  `\index{}` entries in `latex/[01]*.tex` and none in the notebooks. The final
  "Indexing" commits were made by hand after conversion. Any rebuild from
  notebooks, old pipeline or new, loses the index unless the entries are
  moved into the notebook sources first. Other hand edits in the `.tex` are
  likely too; a diff of a fresh conversion against `latex/` would show them.
- `convert/build.sh` reads from local paths that no longer exist
  (`~/ElementsOfDataScience/ElementsOfDataScienceSolutions/`) and `rsync`s
  chapters 14–17 from the case-study clones' working trees.
- `latex/ElementsOfDataScience.epub` (August 2024, 18 MB) is a PDF-to-EPUB
  conversion: `index_split_NNN.html` files with rasterized images of each
  figure. It isn't worth building on. `convert/Book.txt` is LeanPub's
  placeholder sample, not a real manuscript.

**The CultureWar pipeline** (`~/CultureWar/book/BUILD.md`,
`leanpub/README.md`, `leanpub_release_plan.md`):

```text
canonical Markdown + metadata.yml + references.json
  → scripts/emit_book_sources.py   (per-format transforms; --strict)
  → book/build/{pdf,epub}/         (complete, disposable Quarto projects)
  → quarto render                  (PDF via LuaLaTeX + preamble.tex; EPUB + CSS)
  → epub_polish.py                 (EPUB post-processing)
  → build_leanpub_editions.py      (book / sample / community, PDF + EPUB)
```

Its central idea: Quarto is only the final renderer. A Python emitter owns
every difference between formats and writes a plain, self-contained Quarto
project for each one. Quarto 1.10.18, TeX Live 2025 (LuaLaTeX) and Calibre's
`ebook-convert` are installed on this machine; `epubcheck` is not.

## What to borrow, and what is new

| Piece | Borrow from CultureWar? | Notes |
|---|---|---|
| Emitter → per-format Quarto project → render | Yes, the architecture | The emitter's input changes from Markdown to executed notebooks |
| `metadata.yml` (title, version, publisher, copyright) | Yes | Version follows the print numbers (1.0.x) for 1e |
| `preamble.tex` (LuaLaTeX, Source Serif 4, ragged right, heading and note styling) | Yes, as a starting point | Add code styling; 1e's `settings.tex` colors |
| `epub-styles.css` and `epub_polish.py` | Yes | Their gotchas (no CSS variables, font paths, Thorium as the reference reader) apply as is |
| `editions.yml`, LeanPub filenames, release steps | Yes | Probably two editions (book, free sample), not three |
| Typography smoke test (`pdffonts` checks) | Yes | Add monospace to the fonts checked |
| Endnotes and the short-link registry (`references.json`) | Not now | EDS has few citations; links can stay inline. Revisit for v2 print |
| MyST multi-file HTML config | No | The website stays on Jupyter Book 1 (`jb/`) |
| Imports of CultureWar code | No | CultureWar is private. Copy and adapt into this repo, as v2_plan.md says for data |

New for EDS, because the source is notebooks with a lot of code:

1. **Execution.** Each chapter must be executed in a clean environment
   before emitting, so outputs match the code. CI already does this
   (`make tests-soln`, about 3 minutes).
2. **Cell selection.** Follow the 1e print converter
   (`ElementsOfDataScienceBook/convert/remove_soln.py`, `remove_cells.py`):
   drop code cells whose source starts with `# Solution` (the `solution` tag
   alone isn't enough: `07_dataframes` tags a non-solution cell `solution`,
   the hidden `nsfg.iloc[:, :7].head()` that supplies a narrower table for
   `nsfg.head()`); drop `remove-cell` and `hide-cell` cells, the inputs of
   `remove-input` / `hide-input`, the outputs of `remove-output` /
   `hide-output`; drop everything before the H1 (the Lulu notice). Cells
   tagged `remove-print` (the Colab link, documentation links, and exercises
   that depend on them; in 14 chapters) were cut from print because links
   don't work on paper. The screen formats keep them. Keep the error output
   of `%%expect` cells (tagged `raises-exception`), which the text discusses.
3. **Outputs.** Text output, DataFrame tables, and figures each need a
   rendering per format (below).
4. **Code layout.** Code blocks can't reflow. Their width sets the minimum
   width of the text block, and in EPUB they need a wrapping rule.
5. **Code styling.** Syntax colors and the source/output distinction, in
   both LaTeX and EPUB CSS.

## Proposed architecture

```text
book/metadata.yml   (title, version, chapter list; later pinned case-study notebooks)
        ↓
book/stage.py       copy into book/build/stage/, add the book setup cell, execute
        ↓  executed .ipynb, figures stored as PDF and PNG
book/emit.py        per format: select cells, convert outputs, write Markdown
        ↓
book/build/{pdf-screen,epub,pdf-print}/   complete Quarto projects
        ↓
quarto render (+ epub_polish.py)  →  build_editions.py  →  book/leanpub/*.{pdf,epub}
```

Style files are in `book/styles/`: `preamble.tex`, `epub.css`, `eds.theme`
(syntax colors), and `fonts/` (Source Serif 4, SIL OFL, copied from
CultureWar).

**Where it lives:** a new `book/` directory on `v1`. Adding
files doesn't break any printed link (CLAUDE.md forbids moving files, not
adding them), and the 1e ebook should be built from 1e notebooks. The same
directories carry over to `v2`. `book/build/` is gitignored and disposable,
as in CultureWar.

**Emit Markdown, not `.ipynb`.** Quarto can render notebooks directly, but
then Quarto decides how outputs look, and the output handling is exactly
where the formats differ. Emitting Markdown (fenced code, fenced output
divs, image links, pipe or raw tables) keeps every format decision in the
emitter, where CultureWar keeps them. `--strict` fails on anything the
emitter doesn't recognize (an unexpected output MIME type, an unknown tag),
like CultureWar's check for unconverted MyST directives.

**Execute once, store figures twice.** The book setup cell calls
`set_matplotlib_formats('pdf', 'png')`, so each figure output carries both a
vector PDF (for LaTeX) and a PNG (for EPUB), and the notebooks are executed
only once per build. It also sets a DataFrame formatter (below) and
`np.set_printoptions(legacy='1.25')`, which is the house rule from the
GreenTeaPress refresh checklist, so scalars print as `0.36`, not
`np.float64(0.36)`.

**Case-study chapters** come from the PoliticalAlignment and Recidivism
repos at pinned tags or commits listed in `chapters.yml`, fetched into the
stage directory, not `rsync`ed from local working trees. Task 21 refreshes
those repos and produces the tags.

## Per-format rendering

| Element | PDF (LaTeX) | EPUB (XHTML + CSS) |
|---|---|---|
| Source code | Highlighted, framed box, monospace a step smaller than body | `<pre>` with Pandoc highlighting, `white-space: pre-wrap`, light background |
| Text output | Unframed gray box, no highlighting | `<pre class="output">`, same wrap rule, gray |
| DataFrame | `df.to_latex()` → `booktabs` table; very wide frames shrink with `\small` or `\footnotesize` | HTML table at 0.85em, inside a horizontally scrollable `div` |
| Figure | Vector PDF, natural size, inline (no floats), no captions, as 1e and YWCN do | PNG at 2× display size, `max-width: 100%` |
| Error output from `%%expect` | Output box, with the traceback trimmed to the last line | Same |
| Links | Clickable, blue (EDS `codeblue`) | Clickable |
| Colab link per chapter | Keep: on a screen it opens the chapter's notebook | Keep |
| Index | Only if the 659 entries move into the sources (below) | No index; readers search |

Pandoc's highlighting (Quarto's default) can take the 1e colors through a
custom `.theme` file, which keeps PDF and EPUB consistent. That replaces
`listings`.

## Line length: print versus screen

Print uses a 144 mm (5.7 in) block. For screens the targets are about 65–75
characters of prose and a code width that fits without wrapping.

Measured on `soln/[01]*.ipynb` (2026-10-27):

| | Lines | ≤ 60 chars | 61–70 | 71–80 | > 80 |
|---|---:|---:|---:|---:|---:|
| Code | 2,777 | 2,677 (96%) | 48 | 28 | 24 |
| Text output (not tables) | 1,023 | 1,006 | 12 | 4 | 1 |

The longest code lines are the `download(...)` calls with full GitHub URLs,
which the emitter drops along with the other setup cells. So a block that
fits about 64–70 monospace characters covers almost everything, and the
rest can be wrapped by hand in `soln/` (an improvement for the notebooks
too) or left to an automatic break with a continuation mark.

The spike compared 6 × 9 in (YWCN's trim; 4.6 in block, about 67
characters of prose at 10.5 pt) and 7 × 10 in (5.1 in block, about 77 at
11 pt). Allen chose the O'Reilly / No Starch trim, **7 × 9.1875 in**, with a
5.0 in block, 11 pt body and 9 pt code. Measured: prose lines of 70–75
characters; code fits about 66.

The EPUB has no fixed width: the reader sets it. Code that is wider than the
screen wraps (`pre-wrap`, with a small hanging indent) rather than
overflowing, and tables scroll. Thorium (the reference reader in CultureWar)
plus one phone-size reader is the QA set.

The print edition stays at crown quarto with its wide block. For a future
print build from this pipeline (v2, or a regenerated 1e), the geometry is
one more format, `pdf-print`, with the same emitter.

## Relation to the print refresh

Two ways to do the 1e print refresh:

- **Patch the existing `.tex`** in the Book repo for errata. Cheap, and it
  keeps the index and the hand edits. It doesn't need this pipeline.
- **Regenerate from the notebooks** with this pipeline's `pdf-print` format.
  Then print, PDF, and EPUB all come from `soln/`, but first the index
  entries (and any other hand edits) must move into the notebooks, for
  example as MyST-style `{index}` roles in markdown cells that the emitter
  turns into `\index{}` for LaTeX and drops for EPUB. Moving 659 entries is
  a mechanical job a script can do with a diff of a fresh conversion against
  `latex/`, followed by a review.

Recommendation: patch the `.tex` for a 1e reprint, build the LeanPub
formats with the new pipeline, and move the index into the sources when v2
starts, since v2 needs a new index anyway.

## Decisions for Allen

Decided 2026-10-27:

1. **Rights:** Green Tea Press holds them, so EDS is eligible for LeanPub
   (fill in the GreenTeaPress Task 18 table).
2. **Chapter set:** all 18 chapters, as printed, including the four
   case-study chapters. So phase 3 depends on Task 21.
3. **Solutions:** left out, as in print.
4. **Screen PDF page:** 7 × 9.1875 in, the O'Reilly / No Starch trim
   (Allen, 2026-10-27, after the spike compared 6 × 9 and 7 × 10). Text
   block 5.0 in, 11 pt body, 9 pt code: prose lines of 70–75 characters.
5. **Editions:** the book plus a free sample: the preface and chapters 6
   (Plotting) and 7 (DataFrames and Series), chosen as more compelling than
   Chapter 1.
6. **Code style:** format all the chapter notebooks with Ruff at 60
   columns (`ruff.toml`, `make format`), for one standard style, rather
   than hand-wrapping the long lines. Done; see "Code formatting".

7. **Version:** 1.1.0, © 2024–2026: 1e revised for the ebook (the code
   has been reformatted). LeanPub versions continue from there.
8. **Support ask:** yes, on a back page of the full book
   (`book/front/book_back.md`), with links to the site and notebooks.

Open:

9. **Free PDF link:** GreenTeaPress Task 18's open question (keep a free
   download alongside LeanPub, or make LeanPub at $0 the download).

## Spike results (2026-10-27)

`07_dataframes` built to PDF (first at 6 × 9 and 7 × 10, then at the chosen
7 × 9.1875 as `pdf-screen`) and EPUB, with the files in `book/`:

```bash
conda run -n ElementsOfDataScience python book/stage.py        # about 10 s
conda run -n ElementsOfDataScience python book/emit.py pdf-screen --render
conda run -n ElementsOfDataScience python book/emit.py epub --render
```

The spike ran in an old `ElementsOfDataScience` env (pandas 2.2.2). Phase 2
recreated it from `environment.yml` (Python 3.13.18, pandas 3.1.0, NumPy
2.5.4).

What worked:

- The emitter design holds. About 250 lines handled every cell and output in
  the chapter, with no Lua filters and no Quarto notebook features. The
  `--strict` check reported nothing. (Quarto's own `.ipynb` rendering
  wasn't tried; nothing in this chapter called for it.)
- PDF: Source Serif 4 and Source Code Pro embedded; source code highlighted
  in the 1e colors on a gray box; text output gray, with a rule at the left;
  the 7-column DataFrame shrinks a little to the text width and stays
  legible; figures are vector PDFs at two-thirds size, as in 1e.
- Matplotlib embeds its fonts as Type 3 by default. `pdf.fonttype = 42` in
  the setup cell makes them TrueType.
- EPUB: well-formed XHTML; code wraps with a hanging indent on each line;
  the wide DataFrame scrolls sideways. Checked with a phone-size Calibre
  rendering, not yet in Thorium. Pandoc puts its own `<style>` block in each
  chapter (`white-space: pre`, `overflow: auto` on source code), so
  `epub.css` overrides it with more specific selectors. The first try,
  without those, clipped the first character of each block and scrolled.
- Length: about 18 pages for the chapter in each screen layout tried, against
  16 in print (which also left out the `remove-print` cells). Roughly
  320–330 pages for the whole book.

## Phase 2 results (2026-10-27)

All 14 chapters (1–13 and "Further Reading") stage in about 5 minutes and
build to both formats with `--strict` and no issues.

- PDF: 232 pages, 7 × 9.1875 in, all fonts embedded, no missing glyphs.
  Chapters 1–13 take about 224 pages against about 208 in print (8% more),
  so the 18-chapter book should come to about 315 pages.
- EPUB: 9.3 MB. `emit.py --render` now fails if any XHTML file is not
  well-formed.
- Chapters and sections are numbered as in print (1, 1.1, ...); chapters
  listed under `unnumbered` in `metadata.yml` aren't (the outro).

Fixed on the way:

- Three markdown images pointed at `raw/v1/figs/...` on GitHub, two of them
  as raw HTML `<img width=...>`. Pandoc drops raw HTML from LaTeX, so those
  figures were silently missing from the PDF, and in the EPUB the tag was
  unclosed (invalid XHTML). The emitter now uses the local `figs/` copies
  and keeps the pixel width; `--strict` flags any other raw `<img>`. (The
  xkcd comic in chapter 10 is `remove-cell`, so it never reaches the book,
  which matters because xkcd is CC BY-NC.)
- Side-by-side figures (chapter 9) came out 5.79 in wide; figure width is
  now capped at the text block.
- Python 3.13 adds a `SyntaxWarning` on stderr to the `%%expect` example in
  chapter 1. stderr warnings are dropped quietly; any other stderr is an
  issue.

`%%expect` cells print as in 1e: the magic line, the code, then
`TypeError: ...`.

Lines that wrap (with a ↪ mark in the PDF, a hanging indent in the EPUB):
the 66-character estimate was wrong. `Scale=MatchLowercase` enlarges
Source Code Pro by about 6% and the code box has padding, so code fits
about 60 characters at 9 pt, and 26 printed code lines wrapped.

## Code formatting (2026-10-27)

Allen chose Ruff's formatter, which imposes one standard style, over
hand-wrapping (Black and nbblack are no longer used). `ruff.toml`:
`line-length = 60`, `quote-style = "preserve"`, and `include` limited to
`soln/[01]*.ipynb`, so `utils.py` and the rest of `v1` are never touched.
`make format` formats, then lists lines still too long.

- Ruff changed only cell sources (checked: metadata, outputs and JSON
  layout unchanged), in 13 notebooks. Besides wrapping it made style
  changes, such as `2 ** 3` → `2**3` and `np.sin(theta/2)**2` →
  `np.sin(theta / 2) ** 2`, so the `v1` notebooks no longer match the
  printed code character for character. One markdown cell quoted changed
  code (`np.sin(theta / 2) ** 2` in chapter 2) and was updated; a script
  found no others.
- Hand fixes: Ruff split the haversine line in chapter 2 inside a call
  (`np.cos(` / `phi2` / `) * ...`). Parentheses don't help, since Ruff
  removes them, so the function now uses an intermediate `cos_product`.
  An 82-character comment in chapter 8 was split in two.
- Left alone: two string literals over 60 (chapter 4's Gutenberg marker,
  chapter 5's quotation), which would need implicit concatenation.
- `make tests-soln` 14 passed; `make notebooks` regenerated the student
  notebooks and the zip; `make tests` 15 passed.
- Book: 235 pages (Ruff's taller code adds 3). Seven wrapped lines remain:
  the two strings and a few outputs (list and `Index` reprs, an error
  message).

Environment notes: `environment.yml` now lists pytest, nbmake and ruff
(it had no test tools). nbmake 1.5.5 pins `nbclient` below 0.7, so
installing it downgraded `nbclient` 0.11.0 → 0.6.8; nbconvert under that
version prints a Python 3.13 `DeprecationWarning` (cpython #70647) when it
runs, which is harmless. Run the build with the env activated, not with
`conda run`: under `conda run`, `PROJ_DATA` went missing and GDAL printed a
PROJ error into chapter 2's output, which `--strict` caught.

Still to check: Thorium; `epubcheck` (Java is installed, epubcheck isn't);
code-block padding in the PDF, which is generous.

## Phase 3 results (2026-10-27)

Parts IV and V are in: chapters 14–17 from PoliticalAlignmentCaseStudy
(`02_polviews_soln`, `03_outlook`) and RecidivismCaseStudy
(`01_classification`, `02_calibration`), after Task 21 formatted both repos
with the same `ruff.toml`. The book PDF is 316 pages and 7.0 MB; the EPUB
is 11 MB.

- In `metadata.yml`, a case-study chapter is a mapping (stem, repo, full
  commit, file). `stage.py` downloads the notebook at that commit from
  GitHub, so the build doesn't depend on local clones. To take later fixes,
  move the commit after the repo's CI passes.
- Each external chapter runs in its own directory (`stage/ext/{stem}/`):
  PoliticalAlignment downloads its own `utils.py`, which EDS's `utils.py`
  would otherwise shadow.
- Three images came from GitHub (`machine_bias_table.png`,
  `calibration1.png`). The emitter now uses any GitHub image from this repo
  or Recidivism that has a copy in `figs/` (checked identical).
- The case studies tag their setup cells (the `download` function and
  calls, pip fallbacks) `remove-print`, not `remove-cell`, and their long
  URLs overflowed the page by up to 184 pt. The screen formats keep
  `remove-print` cells, many of which are content cut from print for
  space, so the emitter now drops setup code by what it is (`is_setup`).
  1e print left these cells out too. No overfull boxes over 0.2 pt remain;
  no missing glyphs.

## Phase 4 results (2026-10-27)

`python book/emit.py --release` builds both editions in both formats,
strict, into `book/leanpub/` (gitignored), named as for YWCN:

| File | Size | Pages |
|---|---:|---:|
| `downey-elements-of-data-science-1.0.1.pdf` | 6.7 MB | 243 |
| `downey-elements-of-data-science-1.0.1.epub` | 9.3 MB | |
| `downey-elements-of-data-science-1.0.1-sample.pdf` | 1.2 MB | 47 |
| `downey-elements-of-data-science-1.0.1-sample.epub` | 2.3 MB | |

- `metadata.yml` holds the parts, the back matter, the editions, and the
  copyright text. Working projects are in `book/build/{edition}/{format}/`.
- Front matter follows CultureWar: in the PDF, a KOMA title page (with the
  edition badge as `\subject`), then the copyright page (through
  `include-before-body`, because KOMA prints the back of the title page
  only in two-sided layouts), then Contents; `index.md` is the preface. In
  the EPUB, `index.md` is the title and copyright page and `preface.md`
  follows.
- The preface is 1e's (`intro.tex`, converted with Pandoc into
  `book/front/preface.md`), with one typo fixed ("In introduces"). It still
  describes all five parts and 17 chapters, which is right once the case
  studies are in. `latex/preface.md` in the Book repo is an older draft.
- Chapter numbers come from the chapter's position in the full book, so
  the sample's chapters are 6 and 7. The PDF sets LaTeX's counter at the
  end of the previous file; setting it before the heading in the same file
  didn't work, because Quarto moves the heading above it. The EPUB writes
  the numbers into the headings and gets a page per part, since Quarto
  leaves parts out of EPUBs.
- Figures with large vector PDFs (12, mostly the chapter 9 scatter plots,
  6–8 MB each) use their PNG instead: the book PDF went from 62 MB to
  6.7 MB.
- Fixed: chapter 1's removed `# Welcome` cell was taken as the chapter
  title.

The copyright page uses 1e's text without the print ISBN (it identifies
the paperback), with version 1.1.0 and © 2024–2026 (decision 7). The full
book ends with a "Thank You" page: the notebooks, and the support ask
(decision 8). Files are now `downey-elements-of-data-science-1.1.0*`; the
book PDF is 244 pages.

## QA results (2026-10-28)

- **epubcheck 5.4.0** (W3C): both EPUBs, no errors, warnings or infos.
- **`make tests-book`** (`book/test_book.py`, 15 checks on the release
  files): page size, embedded fonts and no Type 3, size under 15 MB, the
  copyright page, parts I–V and chapters 1–17 in order in the book,
  chapters 6 and 7 numbered as such in the sample, a code block and its
  output, the EPUB navigation, and epubcheck when `EPUBCHECK` points to the
  jar. Checked that the tests fail on a wrong page size or chapter count.
- **Links:** 60 external links in the EPUB; 52 return 200. Six return 403
  to a script (cdc.gov ×3, economist.com, nejm.org, pewresearch.org), which
  these sites do to non-browser clients; check them in a browser. The two
  GSS Data Explorer links (chapter 8) fail here because the server sends an
  incomplete certificate chain; browsers usually cope, so check them too.

For Allen's proofread (what the automated checks can't judge):

- The EPUBs in Thorium (publisher styles on), and on a phone: code
  wrapping, wide DataFrames scrolling, the title and copyright page.
- The PDF on a tablet: figure sizes, the 12 scatter plots now as PNG
  (chapter 9), page breaks around code and output.
- The `remove-print` cells the screen editions add back (Colab links,
  documentation links, content cut from print for space, such as the
  confusion matrices in chapter 16): does the text around them still read
  well?
- The two string literals that wrap (chapters 4 and 5).

## Phases

1. **Spike, one chapter.** `07_dataframes` (code, text output, wide
   DataFrames, figures). Stage, emit, render to both screen PDF candidates
   and EPUB. Check: fonts embedded, code fits, tables legible, figures
   sharp, EPUB in Thorium. This settles decision 5 and shows whether
   Quarto's own notebook handling would have done (if it would, the emitter
   gets simpler).
2. **The 14 chapters.** Done 2026-10-27. Fix what `--strict` finds;
   long code lines handled by formatting with Ruff (decision 6).
3. **Case-study chapters.** Done 2026-10-27.
4. **Book chrome.** Done 2026-10-27.
   Title page, copyright, preface, Contents, parts, the sample edition.
5. **QA and release.** Automated part done 2026-10-28; landing page drafted
   (`book/leanpub/landing-page.txt`). Smoke tests (page size, fonts, a code block's
   presence); `epubcheck` (install it); proofread a sample on a tablet and a
   phone; LeanPub landing page; upload; tag (`v1.0.x-leanpub`, or follow the
   print version if a reprint coincides).
