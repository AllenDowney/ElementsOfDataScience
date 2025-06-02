# Build the Colab notebooks

# copy the notebooks with solutions
cp soln/[01]*.ipynb .
cp soln/utils.py .
cp soln/jupyter_intro.ipynb .
cp soln/geo_example.ipynb .
cp soln/clustering_soln.ipynb ./clustering.ipynb

# remove solutions
python remove_soln.py

# pip install pytest nbmake

# run nbmake
# pytest --nbmake [01]*.ipynb

cd ..; zip -r EDS_notebooks.zip \
    ElementsOfDataScience/[01]*.ipynb \
    ElementsOfDataScience/jupyter_intro.ipynb \
    ElementsOfDataScience/geo_example.ipynb \
    ElementsOfDataScience/utils.py \
    ElementsOfDataScience/environment.yml; \
mv EDS_notebooks.zip ElementsOfDataScience; \
cd ElementsOfDataScience

# push to GitHub
git add [0-9]*.ipynb
git add utils.py
git add clustering.ipynb
git add jupyter_intro.ipynb
git add geo_example.ipynb
git commit -m "Updating notebooks"
git push
