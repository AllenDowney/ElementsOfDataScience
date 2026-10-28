"""Write a Quarto book project from the staged notebooks (Task 22).

Reads the executed notebooks in book/build/stage/ (see stage.py) and writes,
for one format and edition, a complete Quarto project in
book/build/{edition}/{format}/: one Markdown file per chapter, the front
and back matter, the figures, _quarto.yml, and the style files. Every
difference between formats is decided here; Quarto only renders.

Cells are selected as in the 1e print converter: code cells whose source
starts with "# Solution" are dropped (the `solution` tag alone is not
enough), and so is setup code (see is_setup), and so are cells tagged remove-cell or hide-cell, the inputs of
remove-input / hide-input cells, and the outputs of remove-output /
hide-output cells. Cells tagged remove-print are dropped only from print
formats: they hold links, which work on a screen.

Chapters keep their numbers from the full book in every edition, so the
sample's chapters are 6 and 7, as the text's cross references expect. The
PDF sets LaTeX's chapter counter at the end of the file before each
chapter (Quarto moves a chapter's heading above anything that precedes it
in the same file); the EPUB writes the numbers into the headings.

Usage:
    python book/emit.py FORMAT [--edition NAME] [--render] [--strict]
    python book/emit.py --release      # every edition and format, rendered
                                       # and strict, into book/leanpub/
FORMAT is one of: pdf-screen, epub. Editions are in metadata.yml.
"""

import argparse
import base64
import csv
import html
import re
import shutil
import struct
import subprocess
import sys
import xml.dom.minidom
import xml.parsers.expat
import zipfile
from pathlib import Path

import nbformat
import yaml

BOOK = Path(__file__).resolve().parent
REPO = BOOK.parent
STAGE = BOOK / "build" / "stage"
RELEASE = BOOK / "leanpub"
# Images the notebooks load from GitHub (this repo or RecidivismCaseStudy,
# in either URL form) are used from this repo's figs/, which has copies.
REPO_FIG_URL = re.compile(
    r"https://(?:github\.com/AllenDowney/(?:ElementsOfDataScience|RecidivismCaseStudy)/raw"
    r"|raw\.githubusercontent\.com/AllenDowney/(?:ElementsOfDataScience|RecidivismCaseStudy))"
    r"/v1/(?:figs/)?([^)\s\"]+)")
REPO_FIG = re.compile(r"!\[([^\]]*)\]\(" + REPO_FIG_URL.pattern + r"\)")

# External links in the PDF and EPUB go through short links,
# greenteapress.com/eds/N (book/links.csv, book/shortlinks.py), so a link
# that rots can be repointed after readers have downloaded the book. The
# notebooks and the website keep the direct URLs. Links to greenteapress.com
# itself and the license stay direct.
LINKS = BOOK / "links.csv"
SHORT_BASE = "https://greenteapress.com/eds/"
DIRECT = re.compile(r"https?://(?:greenteapress\.com|creativecommons\.org|leanpub\.com)/")

# Figures are 6 x 3.5 in (utils.py); 1e printed them at two-thirds size.
FIGURE_SCALE = 2 / 3
PNG_DPI = 200  # set in stage.py
MAX_VECTOR_FIGURE = 500_000  # bytes; larger figures use the PNG

PDF_LAYOUTS = {
    # O'Reilly / No Starch trim, 7 x 9.1875 in (decided 2026-10-27).
    # Text block 5.0 in: prose about 70 characters, code about 60.
    "pdf-screen": dict(paper=(7, 9.1875), margins=(1.0, 1.0, 0.8, 0.85),
                       fontsize="11pt", codesize=(9, 11)),
}
FORMATS = list(PDF_LAYOUTS) + ["epub"]
PRINT_FORMATS = set()  # a pdf-print layout will go here

ANSI = re.compile(r"\x1b\[[0-9;]*m")
ROMAN = ["", "I", "II", "III", "IV", "V"]


def load_links():
    """Map from target URL to short-link number."""
    if not LINKS.exists():
        return {}
    with open(LINKS, newline="") as f:
        return {row["target"]: int(row["n"]) for row in csv.DictReader(f)}


def load_metadata():
    return yaml.safe_load((BOOK / "metadata.yml").read_text())


def stem_of(entry):
    """A chapter entry is a stem, or a mapping for a case-study chapter."""
    return entry if isinstance(entry, str) else entry["stem"]


def part_stems(part):
    return [stem_of(e) for e in part["chapters"]]


def all_chapters(meta):
    """Every chapter stem in the book, in order."""
    return [s for part in meta["parts"] for s in part_stems(part)] + meta.get("back", [])


def chapter_numbers(meta):
    """Map from stem to chapter number, for the chapters in parts."""
    stems = [s for part in meta["parts"] for s in part_stems(part)]
    return {stem: n for n, stem in enumerate(stems, 1)}


def external_chapters(meta):
    """Map from stem to its entry, for chapters from other repos."""
    return {e["stem"]: e for part in meta["parts"] for e in part["chapters"]
            if not isinstance(e, str)}


def staged_path(meta, stem):
    """Where stage.py puts the executed notebook for a chapter."""
    if stem in external_chapters(meta):
        return STAGE / "ext" / stem / f"{stem}.ipynb"
    return STAGE / f"{stem}.ipynb"


# Longer text output is abridged to its first and last lines, with an
# ellipsis between (one output in the book: years in chapter 14).
MAX_OUTPUT_LINES = 25
ABRIDGED_LINES = 5

# Text output blocks, as text_output writes them
OUTPUT_START = ("```{=latex}\n\\begin{outbox}", '```{=html}\n<pre class="output">')


class Emitter:
    def __init__(self, fmt, outdir, meta):
        self.fmt = fmt
        self.meta = meta
        self.links = load_links()
        self.seen = []  # (url, stem) for every external link, in book order
        self.is_pdf = fmt.startswith("pdf")
        self.outdir = outdir
        self.issues = []

    def issue(self, stem, i, message):
        self.issues.append(f"{stem} cell {i}: {message}")

    # --- cells ---

    def chapter(self, stem, number=None):
        """Markdown for one chapter; number is None for an unnumbered one."""
        nb = nbformat.read(staged_path(self.meta, stem), as_version=4)
        blocks = []
        started = False
        self.nfig = 0
        self.number, self.nsection = number, 0
        for i, cell in enumerate(nb.cells):
            tags = set(cell.metadata.get("tags", []))
            source = cell.source.strip()

            # Removed cells go first: chapter 1 has a removed "# Welcome"
            # cell before its title.
            if tags & {"remove-cell", "hide-cell", "book-setup"}:
                continue
            if "remove-print" in tags and self.fmt in PRINT_FORMATS:
                continue

            # Everything before the chapter title (the Lulu notice) is dropped.
            if not started:
                if cell.cell_type == "markdown" and source.startswith("# "):
                    started = True
                    title, _, rest = source.partition("\n")
                    if number is None:
                        title += " {.unnumbered}"
                    elif not self.is_pdf:
                        title = f"# {number} {title[2:]}"
                    source = f"{title}\n{rest}"
                else:
                    continue

            if cell.cell_type == "markdown":
                blocks.append(self.markdown(stem, i, source))
            elif cell.cell_type == "code":
                if source.startswith("# Solution") or is_setup(source):
                    continue
                shown = source and not tags & {"remove-input", "hide-input"}
                if shown:
                    blocks.append(f"```python\n{source}\n```")
                if not tags & {"remove-output", "hide-output"}:
                    # Text output right under its code (or under more text
                    # output from the same cell) is joined to the box above.
                    joined = shown
                    for block in self.outputs(stem, i, cell.get("outputs", [])):
                        if block.startswith(OUTPUT_START):
                            if joined:
                                block = self.join_output(block)
                            joined = True
                        else:
                            joined = False
                        blocks.append(block)
        return "\n\n".join(b for b in blocks if b) + "\n"

    def markdown(self, stem, i, source):
        # Images from GitHub with a copy in figs/ use the copy; others stay
        # remote, and are reported below.
        scales = self.meta.get("figure_scale", {})

        def local_fig(m):
            alt, name = m.groups()
            if not self.copy_fig(name):
                return m.group(0)
            return f"![{alt}](figs/{name}){{width={100 * scales.get(name, 1):.0f}%}}"
        source = REPO_FIG.sub(local_fig, source)

        # Raw <img> tags: Pandoc drops them from LaTeX, and leaves them
        # unclosed (invalid XHTML) in EPUB. Width is in pixels, as in HTML.
        def html_fig(m):
            tag = m.group(0)
            name = REPO_FIG_URL.search(tag).group(1)
            width = re.search(r'width="(\d+)"', tag)
            if not self.copy_fig(name):
                return tag
            scale = scales.get(name, 1)
            if width:
                attr = f"{{width={round(int(width.group(1)) * scale)}}}"
            else:
                attr = f"{{width={100 * scale:.0f}%}}" if scale != 1 else ""
            return f"![](figs/{name}){attr}"
        source = re.sub(r"<img[^>]*" + REPO_FIG_URL.pattern + r"[^>]*>", html_fig, source)

        for url in re.findall(r"!\[[^\]]*\]\((https?://[^)]+)\)", source):
            self.issue(stem, i, f"remote image {url}")
        if "<img" in source:
            self.issue(stem, i, "raw <img> tag")

        # A fence with no language in the text is code the reader isn't
        # meant to run; set it like a code cell.
        lines = source.split("\n")
        inside = False
        for j, line in enumerate(lines):
            if line.startswith("```"):
                if not inside and line.strip() == "```":
                    lines[j] = "```python"
                inside = not inside
        source = "\n".join(lines)

        source = self.short_links(stem, i, source)
        if self.number is not None and not self.is_pdf:
            source = self.number_sections(source)
        return source

    def short_links(self, stem, i, source):
        """Point the external links in markdown at their short links."""
        def short(url):
            if DIRECT.match(url):
                return None
            self.seen.append((url, stem))
            n = self.links.get(url)
            if n is None:
                self.issue(stem, i, f"link not in links.csv: {url} "
                                    "(python book/shortlinks.py update)")
                return None
            return f"{SHORT_BASE}{n}"

        def autolink(m):
            url = short(m.group(1))
            return m.group(0) if url is None else f"[{url[8:]}]({url})"

        def link(m):
            text, target = m.groups()
            url = short(target)
            if url is None:
                return m.group(0)
            if text in (target, target.removeprefix("https://")):
                text = url[8:]
            return f"[{text}]({url})"

        source = re.sub(r"<(https?://[^>\s]+)>", autolink, source)
        source = re.sub(r"(?<!!)\[([^\]]*)\]\((https?://[^)\s]+)\)", link, source)
        for url in re.findall(r"https?://[^\s)>\]`'\"]+", source):
            if not (url.startswith(SHORT_BASE) or DIRECT.match(url)
                    or url.startswith("https://github.com/AllenDowney/")
                    and "/figs/" in url):
                self.issue(stem, i, f"URL not converted to a short link: {url}")
        return source

    def copy_fig(self, name):
        """Copy figs/{name} into the project; False if there is no copy."""
        if not (REPO / "figs" / name).exists():
            return False
        (self.outdir / "figs").mkdir(exist_ok=True)
        shutil.copy2(REPO / "figs" / name, self.outdir / "figs" / name)
        return True

    def number_sections(self, source):
        """Write section numbers into ## headings (EPUB)."""
        lines, fenced = [], False
        for line in source.split("\n"):
            if line.startswith("```"):
                fenced = not fenced
            if not fenced and line.startswith("## "):
                self.nsection += 1
                line = f"## {self.number}.{self.nsection} {line[3:]}"
            lines.append(line)
        return "\n".join(lines)

    # --- outputs ---

    def outputs(self, stem, i, outputs):
        blocks = []
        for out in outputs:
            kind = out.output_type
            if kind == "stream":
                if out.name == "stderr":
                    # Warnings are dropped quietly (Python 3.13 adds a
                    # SyntaxWarning to the %%expect example in chapter 1).
                    if "Warning:" not in out.text:
                        self.issue(stem, i, f"stderr output dropped: {out.text[:60]!r}")
                    continue
                blocks.append(self.text_output(out.text))
            elif kind == "error":
                blocks.append(self.text_output(f"{out.ename}: {out.evalue}"))
            elif kind in ("execute_result", "display_data"):
                blocks.append(self.rich_output(stem, i, out.data))
            else:
                self.issue(stem, i, f"unknown output type {kind}")
        return blocks

    def rich_output(self, stem, i, data):
        if "image/png" in data:
            return self.figure(stem, data)
        if self.is_pdf and "text/latex" in data:
            return self.latex_table(data["text/latex"])
        if not self.is_pdf and "text/html" in data:
            return self.html_table(data["text/html"])
        if "text/plain" in data:
            return self.text_output(data["text/plain"])
        self.issue(stem, i, f"no usable MIME type in {sorted(data)}")
        return ""

    def text_output(self, text):
        text = ANSI.sub("", text).rstrip("\n")
        lines = text.split("\n")
        if len(lines) > MAX_OUTPUT_LINES:
            keep = ABRIDGED_LINES
            text = "\n".join(lines[:keep] + ["..."] + lines[-keep:])
        if self.is_pdf:
            return ("```{=latex}\n\\begin{outbox}\n\\begin{bookoutput}\n"
                    f"{text}\n\\end{{bookoutput}}\n\\end{{outbox}}\n```")
        return f'```{{=html}}\n<pre class="output">{html.escape(text)}</pre>\n```'

    def join_output(self, block):
        if self.is_pdf:
            return block.replace("\\begin{outbox}", "\\begin{outbox}[joined]", 1)
        return block.replace('<pre class="output">', '<pre class="output joined">', 1)

    def latex_table(self, latex):
        return ("```{=latex}\n\\begin{booktable}\n"
                f"{latex.strip()}\n\\end{{booktable}}\n```")

    def html_table(self, table):
        table = re.sub(r"<style.*?</style>", "", table, flags=re.S)
        table = re.sub(r' border="1"', "", table)
        return f'```{{=html}}\n<div class="table-wrap">{table.strip()}</div>\n```'

    def figure(self, stem, data):
        self.nfig += 1
        figdir = self.outdir / "figs"
        figdir.mkdir(exist_ok=True)
        name = f"{stem}_{self.nfig:02d}"
        png = base64.b64decode(data["image/png"])
        (figdir / f"{name}.png").write_bytes(png)
        width_px, _ = png_size(png)
        width_in = width_px / PNG_DPI * FIGURE_SCALE
        if self.is_pdf:
            # Wide figures (side-by-side panels) shrink to the text block.
            lay = PDF_LAYOUTS[self.fmt]
            text_width = lay["paper"][0] - lay["margins"][0] - lay["margins"][1]
            width_in = min(width_in, text_width)
            # Vector PDF, except for figures with so many marks (the
            # scatter plots in chapter 9) that the PDF runs to megabytes;
            # their PNG at two-thirds size is effectively 300 dpi.
            pdf = base64.b64decode(data.get("application/pdf", ""))
            if 0 < len(pdf) <= MAX_VECTOR_FIGURE:
                (figdir / f"{name}.pdf").write_bytes(pdf)
                return f"![](figs/{name}.pdf){{width={width_in:.2f}in}}"
            return f"![](figs/{name}.png){{width={width_in:.2f}in}}"
        return f"![](figs/{name}.png)"


def is_setup(source):
    """True for a notebook's setup code, which the book leaves out: the
    download function, cells that only call it, and pip-install fallbacks.
    The EDS chapters tag these remove-cell; the case studies tag them
    remove-print, which the screen formats otherwise keep."""
    return ("def download(" in source
            or re.fullmatch(r"(download\([^()]*\)\s*)+", source) is not None
            or ("except ImportError" in source and "pip install" in source))


def png_size(png):
    return struct.unpack(">II", png[16:24])


# --- front matter ---

def latex_text(text):
    """Metadata text to LaTeX: <URL> becomes \\url{URL}."""
    return re.sub(r"<(https?://[^>]+)>", r"\\url{\1}", text)


def frontmatter_tex(meta, badge):
    """KOMA title page additions: publisher and edition badge (PDF)."""
    lines = [r"\publishers{" + meta["publisher"] + "}", r"\date{}"]
    if badge:
        lines.append(r"\subject{" + r"\\".join(badge) + "}")
    return "\n".join(lines) + "\n"


def copyright_tex(meta):
    """The copyright page, after the title page (PDF). KOMA prints the back
    of the title page only in two-sided layouts."""
    lines = [
        r"\thispagestyle{empty}",
        r"{\small\RaggedRight",
        rf"\textbf{{{meta['title']}}}\\",
        rf"{meta['subtitle']}\\",
        rf"by {meta['author']}\par",
        rf"Version {meta['version']}\par",
        rf"{meta['publisher']}, {meta['publisher_place']}\par",
        rf"Copyright \textcopyright\ {meta['copyright_year']} {meta['author']}.\par",
        latex_text(meta["license"]) + r"\par",
        latex_text(meta["commercial"]) + r"\par",
        meta["cover_credit"] + r"\par}",
        r"\clearpage",
    ]
    return "\n".join(lines) + "\n"


def title_page_md(meta, badge):
    """Title and copyright, one spine item with a page break (EPUB)."""
    blocks = [f"# {meta['title']} {{.unnumbered}}", "",
              '<div class="epub-titlepage">', ""]
    if badge:
        blocks += [f'<p class="epub-badge">{"<br/>".join(badge)}</p>', ""]
    blocks += [f'<p class="epub-subtitle">{meta["subtitle"]}</p>', "",
               f'<p class="epub-author">{meta["author"]}</p>', "",
               f'<p class="epub-publisher">{meta["publisher"]}</p>', "",
               "</div>", "", '<div class="epub-copyright">', "",
               f"Version {meta['version']}", "",
               f"{meta['publisher']}, {meta['publisher_place']}", "",
               f"Copyright © {meta['copyright_year']} {meta['author']}.", "",
               meta["license"], "", meta["commercial"], "", meta["cover_credit"], "",
               "</div>", ""]
    return "\n".join(blocks)


# --- project ---

def quarto_yml(fmt, meta, chapters):
    head = f"""\
project:
  type: book

book:
  title: "{meta['title']}"
  subtitle: "{meta['subtitle']}"
  author: "{meta['author']}"
  chapters:
{chapters}

highlight-style: eds.theme
toc-title: Contents
"""
    if fmt == "epub":
        return head + """
format:
  epub:
    toc: true
    toc-depth: 1
    number-sections: false
    epub-title-page: false
    fig-cap: false
    css: epub.css
    epub-fonts:
      - fonts/SourceSerif4-Regular.otf
      - fonts/SourceSerif4-It.otf
      - fonts/SourceSerif4-Bold.otf
      - fonts/SourceSerif4-BoldIt.otf
"""
    lay = PDF_LAYOUTS[fmt]
    (pw, ph), (left, right, top, bottom) = lay["paper"], lay["margins"]
    size, skip = lay["codesize"]
    return head + f"""
format:
  pdf:
    documentclass: scrbook
    pdf-engine: lualatex
    classoption: [oneside, openany, numbers=noendperiod, fontsize={lay['fontsize']}]
    toc: true
    toc-depth: 1
    number-sections: true
    colorlinks: true
    fig-pos: 'H'
    keep-tex: true
    code-block-bg: "#F2F2F2"
    code-block-border-left: false
    geometry:
      - paperwidth={pw}in
      - paperheight={ph}in
      - left={left}in
      - right={right}in
      - top={top}in
      - bottom={bottom}in
    include-in-header:
      - text: \\newcommand{{\\codesize}}{{\\fontsize{{{size}}}{{{skip}}}\\selectfont}}
      - file: preamble.tex
      - file: frontmatter.tex
    include-before-body:
      - file: copyright.tex
"""


def emit(fmt, edition="book", strict=False, render=False):
    """Write (and optionally render) one format of one edition; return the output path."""
    meta = load_metadata()
    ed = meta["editions"][edition]
    badge = ed.get("badge")
    numbers = chapter_numbers(meta)
    outdir = BOOK / "build" / edition / fmt
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    emitter = Emitter(fmt, outdir, meta)

    # Front matter. Quarto always starts with index.md: in the PDF that is
    # the preface (the title page comes from KOMA); in the EPUB it is the
    # title and copyright, and the preface follows.
    preface = emitter.short_links("preface", 0, (BOOK / "front" / "preface.md").read_text())
    if fmt == "epub":
        (outdir / "index.md").write_text(title_page_md(meta, badge))
        (outdir / "preface.md").write_text(preface)
        entries = ["    - index.md", "    - preface.md"]
    else:
        (outdir / "index.md").write_text(preface)
        (outdir / "frontmatter.tex").write_text(frontmatter_tex(meta, badge))
        (outdir / "copyright.tex").write_text(copyright_tex(meta))
        entries = ["    - index.md"]

    files = ["index.md"] if fmt != "epub" else ["index.md", "preface.md"]

    def write_chapter(stem):
        if stem.startswith("front/"):
            name = Path(stem).name
            text = (BOOK / f"{stem}.md").read_text()
            text = text.replace("{{leanpub_url}}", meta["leanpub_url"])
            (outdir / f"{name}.md").write_text(emitter.short_links(name, 0, text))
            files.append(f"{name}.md")
            return f"{name}.md"
        number = numbers.get(stem)
        if number and fmt != "epub":
            with open(outdir / files[-1], "a") as f:
                f.write(f"\n```{{=latex}}\n\\setcounter{{chapter}}{{{number - 1}}}\n```\n")
        (outdir / f"{stem}.md").write_text(emitter.chapter(stem, number))
        files.append(f"{stem}.md")
        return f"{stem}.md"

    if "chapters" in ed:  # a selection, without parts
        entries += [f"    - {write_chapter(s)}" for s in ed["chapters"]]
        back = [ed["back"]] if "back" in ed else []
    else:
        for n, part in enumerate(meta["parts"], 1):
            if fmt == "epub":
                # Quarto leaves parts out of the EPUB, so each part gets a page.
                name = f"part{n}.md"
                (outdir / name).write_text(
                    f"# Part {ROMAN[n]}: {part['title']} {{.unnumbered}}\n")
                files.append(name)
                entries.append(f"    - {name}")
                entries += [f"    - {write_chapter(s)}" for s in part_stems(part)]
            else:
                entries.append(f'    - part: "{part["title"]}"\n      chapters:')
                entries += [f"        - {write_chapter(s)}" for s in part_stems(part)]
        back = meta.get("back", []) + ([ed["back"]] if "back" in ed else [])
    entries += [f"    - {write_chapter(s)}" for s in back]
    (outdir / "_quarto.yml").write_text(quarto_yml(fmt, meta, "\n".join(entries)))

    shutil.copy2(BOOK / "styles" / "eds.theme", outdir)
    if fmt == "epub":
        shutil.copy2(BOOK / "styles" / "epub.css", outdir)
        shutil.copytree(BOOK / "styles" / "fonts", outdir / "fonts")
    else:
        shutil.copy2(BOOK / "styles" / "preamble.tex", outdir)

    for line in emitter.issues:
        print("issue:", line, file=sys.stderr)
    if strict and emitter.issues:
        sys.exit(f"{len(emitter.issues)} issue(s); stopping (--strict)")

    if render:
        subprocess.run(["quarto", "render", "--to", "epub" if fmt == "epub" else "pdf"],
                       cwd=outdir, check=True)
        output = next((outdir / "_book").glob("*.epub" if fmt == "epub" else "*.pdf"))
        if fmt == "epub":
            check_epub(output)
        return output


def check_epub(path):
    """Fail if any XHTML file in the EPUB is not well-formed XML."""
    bad = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith(".xhtml"):
                try:
                    xml.dom.minidom.parseString(z.read(name))
                except xml.parsers.expat.ExpatError as e:
                    bad.append(f"{name}: {e}")
    if bad:
        sys.exit("malformed XHTML in the EPUB:\n" + "\n".join(bad))


def release():
    """Every edition in every format, into book/leanpub/ with LeanPub names."""
    meta = load_metadata()
    RELEASE.mkdir(exist_ok=True)
    for edition in meta["editions"]:
        suffix = "" if edition == "book" else f"-{edition}"
        for fmt in FORMATS:
            output = emit(fmt, edition, strict=True, render=True)
            name = f"downey-elements-of-data-science-{meta['version']}{suffix}{output.suffix}"
            shutil.copy2(output, RELEASE / name)
            print("wrote", RELEASE / name)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("format", nargs="?", choices=FORMATS)
    parser.add_argument("--edition", default="book")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    if args.release:
        release()
    elif args.format:
        emit(args.format, args.edition, strict=args.strict, render=args.render)
    else:
        parser.error("give a FORMAT or --release")


if __name__ == "__main__":
    main()
