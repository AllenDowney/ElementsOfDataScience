#!/bin/bash
# pip install ghp-import

# Publish jb/_build/html to the gh-pages branch, which replaces the website
# at https://allendowney.github.io/ElementsOfDataScience/. Run build.sh first.

set -e
cd "$(dirname "$0")"

if [ ! -f _build/html/index.html ]; then
    echo "No build found; run jb/build.sh first" >&2
    exit 1
fi

ghp-import -n -p -f _build/html
