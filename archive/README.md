# Archive

Material kept for the record. Nothing here is used to build the notebooks,
the website, or the book.

- `video_scripts/`: narration scripts for the online class videos (2019)
  that were the basis of Part II of the book, *Exploratory Data Analysis*
  (chapters 7–10: DataFrames, distributions, relationships, regression).
  `scripts.zip` holds the March 2019 versions of the four files;
  `chapter_3_scripts.txt` was edited once more after that.
- `quizzes/`: seven quizzes (`quiz01`–`quiz07`), copied from
  `ElementsOfDataScienceSolutions/quizzes` at commit `887e660` (2024-04-01).
  Only the notebooks are archived; the data files beside them were never
  committed there.
- `pre_v1_cleaning/`: `brfss_clean.ipynb` (2017 BRFSS) and `nsfg_clean.ipynb`
  (2013–2015 NSFG), the predecessors of `soln/clean_brfss.ipynb` and
  `soln/clean_nsfg.ipynb`. They wrote the top-level `brfss.hdf5` and
  `nsfg.hdf5`, which were removed from `v1` on 2026-09-24 and are still in
  the history (`examples/correlation2.ipynb` downloads `brfss.hdf5` from
  commit `852dd2e`).
