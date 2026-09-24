import nbformat as nbf
from glob import glob

# Collect a list of all notebooks in the content folder
filenames = glob("[0-1]*.ipynb")

# read the header file
header = nbf.read('header.ipynb', nbf.NO_CONVERT)

for filename in sorted(filenames):
    print(filename)
    notebook = nbf.read(filename, nbf.NO_CONVERT)

    notebook.cells = header.cells + notebook.cells

    nbf.write(notebook, filename)
