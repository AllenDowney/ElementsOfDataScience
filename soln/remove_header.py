import nbformat as nbf
from glob import glob

# Collect a list of all notebooks in the content folder
filenames = glob("[0-1]*.ipynb")

for filename in sorted(filenames):
    print(filename)
    notebook = nbf.read(filename, nbf.NO_CONVERT)

    notebook.cells = notebook.cells[1:]

    nbf.write(notebook, filename)
