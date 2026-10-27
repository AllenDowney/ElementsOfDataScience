# Preface {.unnumbered}

## Introduction {.unnumbered}

The goal of this book is to give you the tools you need to execute a data science project from beginning to end, including these steps:

- Choosing questions, data, and methods that go together

- Finding data or collecting it yourself

- Cleaning and validating data

- Exploring datasets and visualizing distributions and relationships between variables

- Modeling data and generating predictions

- Designing data visualizations that tell a compelling story

- Communicating results effectively

We'll start with basic Python programs and work our way up.
My goal is to present a small, powerful subset of Python that allows you to do real work in data science as quickly as possible.

I won't assume you know anything about programming, statistics, or data science. When I use a term, I'll define it immediately, and when I use a programming feature, I'll explain it.

For each chapter in this book, there is a Jupyter notebook you can access from <https://allendowney.github.io/ElementsOfDataScience>.
Jupyter is a software development tool you can run in a web browser, so you don't have to install any software. A Jupyter notebook is a document that contains text, Python code, and results.
You can read it like a book, but you can also run the code, develop new programs, and test them.

The notebooks contain exercises where you can practice what you learn.
Most of the exercises are meant to be quick, but a few are more substantial.

## Book Overview {.unnumbered}

This book is organized in five parts.

Part I is an introduction to Python with emphasis on concepts and tools for working with data. It introduces Python data structures like lists and dictionaries, NumPy arrays, and Pandas DataFrames.

Part II is about exploratory data analysis, starting with the ways we represent and summarize the distribution of a variable, moving on to relationships between variables, and ending with linear and logistic regression.

Part III is about statistical inference -- that is, using a sample to infer the properties of a population. It introduces randomization methods, especially bootstrap resampling, as a tool for estimating a quantity, describing the precision of the estimate, and testing hypotheses.

Part IV is the first of two case studies, an exploration of data from the General Social Survey related to political alignment and beliefs. It introduces tools for describing changes over time and differences between groups, including cross tabulations and pivot tables.

Part V is the second case study, which introduces classification algorithms and the metrics we use to evaluate their performance. It presents a particularly challenging topic in the criminal justice system, the use of algorithms to predict who is most likely to commit future crimes.

Here are more detailed descriptions of the chapters:

Chapter 1 introduces variables, values, and numerical computation.

Chapter 2 shows how to represent times, dates, and locations in Python, and uses the GeoPandas library to plot points on a map.

Chapter 3 presents lists and NumPy arrays. It discusses absolute, relative, and percent errors, and ways to summarize them.

Chapter 4 presents the `for` loop and the `if` statement; then it uses them to speed-read *War and Peace* and count the words.

Chapter 5 presents one of the most powerful features of Python, dictionaries, and uses them to count the unique words in a text and their frequencies.

Chapter 6 introduces a plotting library, Matplotlib, and uses it to generate a few common data visualizations and one less common one, a Zipf plot.

Chapter 7 presents Pandas DataFrames, which are used to represent tables of data. As an example, it uses data from the National Survey of Family Growth to find the average weight of babies in the U.S.

Chapter 8 explains what a distribution is and presents 3 ways to represent one: a PMF, CDF, or PDF. It also shows how to compare a distribution to another distribution or a mathematical model.

Chapter 9 explores relationships between variables using scatter plots, violin plots, and box plots. It quantifies the strength of a relationship using correlation, and uses simple regression to estimate the slope of a line.

Chapter 10 presents multiple regression and uses it to explore the relationship between age, education, and income. It uses visualization to interpret multivariate models. It also presents binary variables and logistic regression.

Chapter 11 presents computational methods we can use to quantify variation due to random sampling, which is one of several sources of error in statistical estimation.

Chapter 12 introduces bootstrapping, a kind of resampling that is well suited to computational statistics.

Chapter 13 uses a computational approach to explain hypothesis testing, which is the bugbear of classical statistics.

Chapter 14 is the beginning of a case study that uses data from the General Social Survey. It uses survey responses to explore political polarization in the United States over the last 50 years.

Chapter 15 is the second part of the case study -- it explores the relationship between political alignment (conservative, moderate, or liberal) and other attitudes and beliefs.

Chapter 16 introduces the second case study, related to an algorithm used in the criminal justice system to predict crime. It replicates analysis reported in 2016 to evaluate the performance of the algorithm and its fairness between racial groups.

Chapter 17 extends the analysis in the previous chapter to address fairness between men and women, and explores different definitions of fairness and why they are hard to achieve.

## Acknowledgments {.unnumbered}

This book started as a collaboration with an interdisciplinary team at Harvard University, assembled to develop a new data science course. I am grateful to my collaborators, Liberty Vittert, Hanspeter Pfister, Joe Blitzstein, Salma Abu Ayyash, Xiao-Li Meng, Aditya Ranganathan, Robert Haussman, Nishant Sule and Salma Abdel Magid. Special thanks to Aditya Ranganathan for also serving as a technical reviewer.

Part II is based on an online course I developed for DataCamp, called "Exploratory Data Analysis in Python". The course was retired recently after five very successful years. Thanks to the people at DataCamp who worked on it, including Chester Ismay and Yashas Roy.

Part III is based on material I created for my data science course at Olin College. As always, I am grateful to my former colleagues for their support, and to my students for their suggestions and corrections.

The case studies in Part IV are based on material I developed at Olin College and as a visiting lecturer at Ashesi University in Ghana. These chapters benefited from the students' diverse perspectives and insights.

This book was in development at No Starch Press, where Alex Freed provided valuable editorial guidance. I am also grateful to Jill Franklin and Bill Pollock.
