# PDF and EPUB from the notebooks (Task 22)

Status: spike done, 2026-10-27 (see "Spike results"). Phase 2 next.

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
5. **Editions:** the book plus a free sample. The sample might be 1–3
   chapters that are more compelling than Chapter 1; to be proposed.

Open:

6. **Free PDF link:** GreenTeaPress Task 18's open question (keep a free
   download alongside LeanPub, or make LeanPub at $0 the download).
7. **Support ask:** add the end-of-chapter note from GreenTeaPress Task 19
   (`/support/?book=eds`) to the ebook too?

## Spike results (2026-10-27)

`07_dataframes` built to PDF (first at 6 × 9 and 7 × 10, then at the chosen
7 × 9.1875 as `pdf-screen`) and EPUB, with the files in `book/`:

```bash
conda run -n ElementsOfDataScience python book/stage.py        # about 10 s
conda run -n ElementsOfDataScience python book/emit.py pdf-screen --render
conda run -n ElementsOfDataScience python book/emit.py epub --render
```

The local `ElementsOfDataScience` env has pandas 2.2.2 and NumPy 1.26, not
CI's pandas 3. Rebuild it (`make update_environment`) before building
anything to release.

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

Still to check: Thorium; `epubcheck` (Java is installed, epubcheck isn't);
chapters with `%%expect` error output, `hide-input`, and markdown images;
chapter numbering (the spike turns it off); code-block padding in the PDF,
which is generous.

## Phases

1. **Spike, one chapter.** `07_dataframes` (code, text output, wide
   DataFrames, figures). Stage, emit, render to both screen PDF candidates
   and EPUB. Check: fonts embedded, code fits, tables legible, figures
   sharp, EPUB in Thorium. This settles decision 5 and shows whether
   Quarto's own notebook handling would have done (if it would, the emitter
   gets simpler).
2. **The 14 chapters.** Fix what `--strict` finds; hand-wrap the long code
   lines in `soln/` (with `make tests-soln`).
3. **Case-study chapters**, after Task 21 (decision 2 includes them).
4. **Book chrome.** Title page, copyright, preface (from `jb/index.md` and
   the 1e front matter), TOC, back matter with the support and LeanPub
   links; `metadata.yml`; `editions.yml`.
5. **QA and release.** Smoke tests (page size, fonts, a code block's
   presence); `epubcheck` (install it); proofread a sample on a tablet and a
   phone; LeanPub landing page; upload; tag (`v1.0.x-leanpub`, or follow the
   print version if a reprint coincides).
