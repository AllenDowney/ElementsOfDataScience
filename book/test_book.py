"""Smoke tests for the LeanPub files (Task 22): `make tests-book`.

Checks the files `book/emit.py --release` wrote into book/leanpub/, so run
the release first. Needs pdfinfo, pdffonts and pdftotext (poppler). If
EPUBCHECK is set to the path of epubcheck.jar, the EPUBs are validated too.
"""

import os
import re
import subprocess
import zipfile
from pathlib import Path

import pytest

from emit import RELEASE, chapter_numbers, load_metadata

META = load_metadata()
STEM = f"downey-elements-of-data-science-{META['version']}"
BOOK_PDF = RELEASE / f"{STEM}.pdf"
SAMPLE_PDF = RELEASE / f"{STEM}-sample.pdf"
BOOK_EPUB = RELEASE / f"{STEM}.epub"
SAMPLE_EPUB = RELEASE / f"{STEM}-sample.epub"
ROMAN = ["I", "II", "III", "IV", "V"]


def run(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def front_text(pdf, last_page=8):
    """Text of the title, copyright and contents pages."""
    return run("pdftotext", "-f", "1", "-l", str(last_page), str(pdf), "-")


@pytest.fixture(params=[BOOK_PDF, SAMPLE_PDF], ids=["book", "sample"])
def pdf(request):
    if not request.param.exists():
        pytest.fail(f"{request.param.name} is missing; run book/emit.py --release")
    return request.param


def test_page_size(pdf):
    # 7 x 9.1875 in, the O'Reilly / No Starch trim
    assert "Page size:       504 x 661.5 pts" in run("pdfinfo", str(pdf))


def test_fonts_embedded(pdf):
    rows = run("pdffonts", str(pdf)).splitlines()[2:]
    names = " ".join(rows)
    for font in ["SourceSerif4-Regular", "SourceSerif4-It", "SourceSerif4-Bold",
                 "SourceCodePro-Regular"]:
        assert font in names
    for row in rows:
        assert "Type 3" not in row, row  # matplotlib's default; stage.py sets fonttype 42
        assert " yes " in row, f"not embedded: {row}"


def test_size(pdf):
    # Dense scatter plots as vector PDFs once made the book 62 MB.
    assert pdf.stat().st_size < 15_000_000


def test_copyright_page(pdf):
    text = front_text(pdf)
    assert f"Version {META['version']}" in text
    assert f"Copyright © {META['copyright_year']} {META['author']}" in text


def test_book_contents():
    """Parts I-V, chapters 1-17 in order, then the unnumbered back matter."""
    text = front_text(BOOK_PDF)
    for numeral in ROMAN[:len(META["parts"])]:
        assert re.search(rf"^{numeral}\b", text, re.M), f"part {numeral}"
    numbers = [int(m) for m in re.findall(r"^(\d+) [A-Z]", text, re.M)]
    total = len(chapter_numbers(META))
    assert numbers[:total] == list(range(1, total + 1))
    assert "Further Reading" in text and "Thank You" in text


def test_sample_contents():
    """The sample's chapters keep their numbers from the full book."""
    text = front_text(SAMPLE_PDF, last_page=4)
    assert "Free sample" in text
    numbers = chapter_numbers(META)
    for stem in META["editions"]["sample"]["chapters"]:
        assert re.search(rf"^{numbers[stem]} [A-Z]", text, re.M), stem


def test_code_and_output():
    """A code block and its output from chapter 7 made it through."""
    text = run("pdftotext", str(BOOK_PDF), "-")
    assert "nsfg.head()" in text
    assert "CASEID" in text


@pytest.mark.parametrize("epub", [BOOK_EPUB, SAMPLE_EPUB], ids=["book", "sample"])
def test_epub_nav(epub):
    with zipfile.ZipFile(epub) as z:
        nav = z.read("EPUB/nav.xhtml").decode()
    titles = re.findall(r'<a href="[^"]*">([^<]*)', nav)
    numbers = chapter_numbers(META)
    if epub == BOOK_EPUB:
        expected = [str(n) for n in range(1, len(numbers) + 1)]
        assert sum(t.startswith("Part ") for t in titles) == len(META["parts"])
    else:
        expected = [str(numbers[s]) for s in META["editions"]["sample"]["chapters"]]
    found = [t.split()[0] for t in titles if t[:1].isdigit()]
    assert found == expected


@pytest.mark.skipif(not os.environ.get("EPUBCHECK"), reason="EPUBCHECK not set")
@pytest.mark.parametrize("epub", [BOOK_EPUB, SAMPLE_EPUB], ids=["book", "sample"])
def test_epubcheck(epub):
    result = subprocess.run(["java", "-jar", os.environ["EPUBCHECK"], str(epub)],
                            capture_output=True, text=True)
    assert "No errors or warnings detected" in result.stdout, result.stdout[-2000:]
