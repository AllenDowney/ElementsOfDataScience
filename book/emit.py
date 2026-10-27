"""Write a Quarto book project from the staged notebooks (Task 22).

Reads the executed notebooks in book/build/stage/ (see stage.py) and writes,
for one format, a complete Quarto project in book/build/{format}/: one
Markdown file per chapter, the figures, _quarto.yml, and the style files.
Every difference between formats is decided here; Quarto only renders.

Cells are selected as in the 1e print converter: code cells whose source
starts with "# Solution" are dropped (the `solution` tag alone is not
enough), and so are cells tagged remove-cell or hide-cell, the inputs of
remove-input / hide-input cells, and the outputs of remove-output /
hide-output cells. Cells tagged remove-print are dropped only from print
formats: they hold links, which work on a screen.

Usage: python book/emit.py FORMAT [--render] [--strict]
FORMAT is one of: pdf-screen, epub
"""

import argparse
import base64
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
REPO_FIG_URL = re.compile(
    r"https://github\.com/AllenDowney/ElementsOfDataScience/raw/v1/figs/([^)\s\"]+)")
REPO_FIG = re.compile(r"!\[([^\]]*)\]\(" + REPO_FIG_URL.pattern + r"\)")

# Figures are 6 x 3.5 in (utils.py); 1e printed them at two-thirds size.
FIGURE_SCALE = 2 / 3
PNG_DPI = 200  # set in stage.py

PDF_LAYOUTS = {
    # O'Reilly / No Starch trim, 7 x 9.1875 in (decided 2026-10-27).
    # Text block 5.0 in: prose about 70 characters, code about 66.
    "pdf-screen": dict(paper=(7, 9.1875), margins=(1.0, 1.0, 0.8, 0.85),
                       fontsize="11pt", codesize=(9, 11)),
}
FORMATS = list(PDF_LAYOUTS) + ["epub"]
PRINT_FORMATS = set()  # a pdf-print layout will go here

ANSI = re.compile(r"\x1b\[[0-9;]*m")


class Emitter:
    def __init__(self, fmt, outdir):
        self.fmt = fmt
        self.is_pdf = fmt.startswith("pdf")
        self.outdir = outdir
        self.issues = []

    def issue(self, stem, i, message):
        self.issues.append(f"{stem} cell {i}: {message}")

    # --- cells ---

    def chapter(self, stem, numbered=True):
        nb = nbformat.read(STAGE / f"{stem}.ipynb", as_version=4)
        blocks = []
        started = False
        self.nfig = 0
        for i, cell in enumerate(nb.cells):
            tags = set(cell.metadata.get("tags", []))
            source = cell.source.strip()

            # Everything before the chapter title (the Lulu notice) is dropped.
            if not started:
                if cell.cell_type == "markdown" and source.startswith("# "):
                    started = True
                    if not numbered:
                        title, _, rest = source.partition("\n")
                        source = f"{title} {{.unnumbered}}\n{rest}"
                else:
                    continue

            if tags & {"remove-cell", "hide-cell", "book-setup"}:
                continue
            if "remove-print" in tags and self.fmt in PRINT_FORMATS:
                continue

            if cell.cell_type == "markdown":
                blocks.append(self.markdown(stem, i, source))
            elif cell.cell_type == "code":
                if source.startswith("# Solution"):
                    continue
                if source and not tags & {"remove-input", "hide-input"}:
                    blocks.append(f"```python\n{source}\n```")
                if not tags & {"remove-output", "hide-output"}:
                    blocks.extend(self.outputs(stem, i, cell.get("outputs", [])))
        return "\n\n".join(b for b in blocks if b) + "\n"

    def markdown(self, stem, i, source):
        # Images from this repo's figs/ are used from the local copy.
        def local_fig(m):
            alt, name = m.groups()
            (self.outdir / "figs").mkdir(exist_ok=True)
            shutil.copy2(REPO / "figs" / name, self.outdir / "figs" / name)
            return f"![{alt}](figs/{name}){{width=100%}}"
        source = REPO_FIG.sub(local_fig, source)

        # Raw <img> tags: Pandoc drops them from LaTeX, and leaves them
        # unclosed (invalid XHTML) in EPUB. Width is in pixels, as in HTML.
        def html_fig(m):
            tag = m.group(0)
            name = REPO_FIG_URL.search(tag).group(1)
            width = re.search(r'width="(\d+)"', tag)
            (self.outdir / "figs").mkdir(exist_ok=True)
            shutil.copy2(REPO / "figs" / name, self.outdir / "figs" / name)
            attr = f"{{width={width.group(1)}}}" if width else ""
            return f"![](figs/{name}){attr}"
        source = re.sub(r"<img[^>]*" + REPO_FIG_URL.pattern + r"[^>]*>", html_fig, source)

        for url in re.findall(r"!\[[^\]]*\]\((https?://[^)]+)\)", source):
            self.issue(stem, i, f"remote image {url}")
        if "<img" in source:
            self.issue(stem, i, "raw <img> tag")
        return source

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
        if self.is_pdf:
            return ("```{=latex}\n\\begin{bookoutput}\n"
                    f"{text}\n\\end{{bookoutput}}\n```")
        return f'```{{=html}}\n<pre class="output">{html.escape(text)}</pre>\n```'

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
        if self.is_pdf and "application/pdf" in data:
            # Wide figures (side-by-side panels) shrink to the text block.
            lay = PDF_LAYOUTS[self.fmt]
            text_width = lay["paper"][0] - lay["margins"][0] - lay["margins"][1]
            width_in = min(width_in, text_width)
            (figdir / f"{name}.pdf").write_bytes(base64.b64decode(data["application/pdf"]))
            return f"![](figs/{name}.pdf){{width={width_in:.2f}in}}"
        return f"![](figs/{name}.png)"


def png_size(png):
    return struct.unpack(">II", png[16:24])


# --- project ---

def quarto_yml(fmt, meta, chapters):
    chapter_lines = "\n".join(f"    - {c}.md" for c in ["index"] + chapters)
    head = f"""\
project:
  type: book

book:
  title: "{meta['title']}"
  subtitle: "{meta['subtitle']}"
  author: "{meta['author']}"
  chapters:
{chapter_lines}

highlight-style: eds.theme
"""
    if fmt == "epub":
        return head + """
format:
  epub:
    toc: true
    toc-depth: 1
    number-sections: true
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
    classoption: [oneside, openany, fontsize={lay['fontsize']}]
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
"""


INDEX_MD = """\
# Preface {.unnumbered}

Spike build of *Elements of Data Science* (Task 22): one chapter, to compare
page layouts and check how code, output, tables, and figures render.
"""


def emit(fmt, strict=False, render=False):
    meta = yaml.safe_load((BOOK / "metadata.yml").read_text())
    outdir = BOOK / "build" / fmt
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)

    emitter = Emitter(fmt, outdir)
    for stem in meta["chapters"]:
        numbered = stem not in meta.get("unnumbered", [])
        (outdir / f"{stem}.md").write_text(emitter.chapter(stem, numbered))
    (outdir / "index.md").write_text(INDEX_MD)
    (outdir / "_quarto.yml").write_text(quarto_yml(fmt, meta, meta["chapters"]))

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
        if fmt == "epub":
            check_epub(next((outdir / "_book").glob("*.epub")))


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


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("format", choices=FORMATS)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    emit(args.format, strict=args.strict, render=args.render)


if __name__ == "__main__":
    main()
