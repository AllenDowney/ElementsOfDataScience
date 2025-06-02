#!/usr/bin/env python
"""
Script to process Jupyter notebooks by removing solutions and preserving error-expecting cells.

This script:
1. Removes solution code and replaces it with placeholder text
2. Preserves the 'raises-exception' tag for cells that expect errors
3. Removes all other tags
4. Removes cell outputs
5. Adds reference labels for chapter/section tags

Usage: python remove_soln.py
       (Processes all notebooks matching pattern [01]*.ipynb in current directory)
"""

import nbformat as nbf
from glob import glob

# Collect a list of all notebooks in the content folder
# Pattern matches notebooks starting with 0 or 1 (e.g., 01_variables.ipynb)
filenames = glob("[01]*.ipynb")

# Text to look for and replace in solution cells
text = '# Solution'
replacement = '# Solution goes here'

# Process each notebook
for filename in sorted(filenames):
    print('Removing solutions from', filename)
    ntbk = nbf.read(filename, nbf.NO_CONVERT)

    for cell in ntbk.cells:
        # Handle cell tags:
        # - Keep 'raises-exception' tag if present (for cells that expect errors)
        # - Remove all other tags
        if 'tags' in cell['metadata']:
            tags = cell['metadata']['tags']
            # Keep only the raises-exception tag if it exists
            cell['metadata']['tags'] = ['raises-exception'] if 'raises-exception' in tags else []
        else:
            tags = []

        # Remove all cell outputs to ensure clean state
        if 'outputs' in cell:
            cell['outputs'] = []

        # Replace solution code with placeholder text
        if cell['source'].startswith(text):
            cell['source'] = replacement

        # Also check for solution tag
        if 'solution' in tags:
            cell['source'] = replacement

        # Add reference labels for chapter/section tags
        # These are used for cross-referencing in the book
        for tag in tags:
            if tag.startswith('chapter') or tag.startswith('section'):
                print(tag)
                label = f'({tag})=\n'
                cell['source'] = label + cell['source']

    # Write the modified notebook back to file
    nbf.write(ntbk, filename)
