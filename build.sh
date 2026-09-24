#!/bin/bash
# Build the Colab notebooks: copy the notebooks from soln/, remove the
# solutions, and rebuild EDS_notebooks.zip.
#
# This only changes files in the working tree. Review the result with
# `git diff --stat`, run `make tests`, then publish with
# `./publish.sh "commit message"` (or `make publish MSG="..."`).

set -e
cd "$(dirname "$0")"

# copy the notebooks with solutions
cp soln/[01]*.ipynb .
cp soln/jupyter_intro.ipynb .
cp soln/geo_example.ipynb .
cp soln/clustering_soln.ipynb ./clustering.ipynb

# remove solutions (from the [01]*.ipynb chapter notebooks only)
python remove_soln.py

# rebuild the zip from scratch; `zip` adds to an existing archive, so files
# dropped from this list would otherwise stay in it
REPO=$(basename "$PWD")
rm -f EDS_notebooks.zip
(cd .. && zip -q -r "$REPO/EDS_notebooks.zip" \
    "$REPO"/[01]*.ipynb \
    "$REPO"/jupyter_intro.ipynb \
    "$REPO"/geo_example.ipynb \
    "$REPO"/utils.py \
    "$REPO"/environment.yml)

echo
echo "Built. Changed files:"
git status --short -- '[01]*.ipynb' jupyter_intro.ipynb geo_example.ipynb clustering.ipynb EDS_notebooks.zip
echo
echo "Next: review, run 'make tests', then ./publish.sh \"commit message\""
