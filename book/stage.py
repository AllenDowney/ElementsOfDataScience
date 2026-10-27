"""Execute chapter notebooks for the book build (Task 22).

Copies each chapter from soln/ (or, for the case-study chapters, from its
repo at the commit pinned in metadata.yml) into book/build/stage/, inserts a setup cell
after the cell that imports utils, and executes the copy there. The setup
cell makes each figure output carry both a PDF (for LaTeX) and a PNG (for
EPUB), and each DataFrame output carry LaTeX as well as HTML, so the
notebooks run once for every format.

Usage: python book/stage.py [STEM ...]   (default: the chapters in metadata.yml)
Run it in an environment with the chapter dependencies.
"""

import subprocess
import sys
import urllib.request
from pathlib import Path

import nbformat

from emit import all_chapters, external_chapters, load_metadata, staged_path

BOOK = Path(__file__).resolve().parent
REPO = BOOK.parent
STAGE = BOOK / "build" / "stage"

SETUP = """\
import matplotlib.pyplot as plt
plt.rcParams['pdf.fonttype'] = 42  # embed TrueType, not Type 3

from matplotlib_inline.backend_inline import set_matplotlib_formats
set_matplotlib_formats('pdf', 'png', bbox_inches='tight', dpi=200)

import numpy as np
if int(np.__version__.split('.')[0]) >= 2:
    np.set_printoptions(legacy='1.25')

import pandas as pd

def _dataframe_latex(df):
    return df.to_latex(escape=True, float_format='%g')

get_ipython().display_formatter.formatters['text/latex'].for_type(
    pd.DataFrame, _dataframe_latex)
"""


def stage(meta, stem):
    entry = external_chapters(meta).get(stem)
    dest = staged_path(meta, stem)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if entry:
        # A case-study chapter, from its repo at the pinned commit. It runs
        # in its own directory: PoliticalAlignment downloads its own utils.py,
        # which EDS's utils.py would otherwise shadow.
        url = (f"https://raw.githubusercontent.com/AllenDowney/{entry['repo']}/"
               f"{entry['commit']}/{entry['file']}")
        with urllib.request.urlopen(url) as response:
            nb = nbformat.reads(response.read().decode(), as_version=4)
    else:
        nb = nbformat.read(REPO / "soln" / f"{stem}.ipynb", as_version=4)

    setup = nbformat.v4.new_code_cell(SETUP)
    setup.metadata["tags"] = ["book-setup"]
    if nb.nbformat_minor < 5:
        del setup["id"]  # cell ids arrived in nbformat 4.5
    # After the cell that imports utils (which sets the figure size), or
    # first if there is none (the outro).
    index = next((i for i, cell in enumerate(nb.cells)
                  if cell.cell_type == "code" and "import utils" in cell.source), -1)
    nb.cells.insert(index + 1, setup)

    nbformat.write(nb, dest)

    # Execute where the notebook is, which is where it downloads its data.
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
         "--ExecutePreprocessor.timeout=1200", dest.name],
        cwd=dest.parent, check=True)


def main(args):
    meta = load_metadata()
    stems = args or all_chapters(meta)
    for stem in stems:
        print("staging", stem)
        stage(meta, stem)


if __name__ == "__main__":
    main(sys.argv[1:])
