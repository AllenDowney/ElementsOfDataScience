#!/bin/bash
# pip install jupyter-book

# Build the Jupyter book version into _build/html. This does not publish;
# check the result in a browser, then run ./publish.sh.

set -e
cd "$(dirname "$0")"

# copy the chapter notebooks
cp ../soln/[01][0-9]*.ipynb .
cp ../examples/resample_logit.ipynb .
cp ../examples/anderson.ipynb .

# add tags to hide the solutions
python prep_notebooks.py

# build the HTML version
jb build .

echo
echo "Built jb/_build/html. Next: check it, then jb/publish.sh"
