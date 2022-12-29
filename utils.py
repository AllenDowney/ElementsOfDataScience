import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import re
import os

class FixedWidthVariables(object):
    """Represents a set of variables in a fixed width file."""

    def __init__(self, variables, index_base=0):
        """Initializes.

        variables: DataFrame
        index_base: are the indices 0 or 1 based?

        Attributes:
        colspecs: list of (start, end) index tuples
        names: list of string variable names
        """
        self.variables = variables
        self.colspecs = variables[['start', 'end']] - index_base

        # convert colspecs to a list of pair of int
        self.colspecs = self.colspecs.astype(np.int).values.tolist()
        self.names = variables['name']

    def read_fixed_width(self, filename, **options):
        """Reads a fixed width ASCII file.

        filename: string filename

        returns: DataFrame
        """
        df = pd.read_fwf(filename,
                             colspecs=self.colspecs,
                             names=self.names,
                             **options)
        return df


def read_stata_dict(dct_file, **options):
    """Reads a Stata dictionary file.

    dct_file: string filename
    options: dict of options passed to open()

    returns: FixedWidthVariables object
    """
    type_map = dict(byte=int, int=int, long=int, float=float,
                    double=float, numeric=float)

    var_info = []
    with open(dct_file, **options) as f:
        for line in f:
            match = re.search( r'_column\(([^)]*)\)', line)
            if not match:
                continue
            start = int(match.group(1))
            t = line.split()
            vtype, name, fstring = t[1:4]
            name = name.lower()
            if vtype.startswith('str'):
                vtype = str
            else:
                vtype = type_map[vtype]
            long_desc = ' '.join(t[4:]).strip('"')
            var_info.append((start, vtype, name, fstring, long_desc))

    columns = ['start', 'type', 'name', 'fstring', 'desc']
    variables = pd.DataFrame(var_info, columns=columns)

    # fill in the end column by shifting the start column
    variables['end'] = variables.start.shift(-1)
    variables.loc[len(variables)-1, 'end'] = 0

    dct = FixedWidthVariables(variables, index_base=1)
    return dct


def read_stata(dct_name, dat_name, **options):
    """Reads Stata files from the given directory.

    dirname: string

    returns: DataFrame
    """
    dct = read_stata_dict(dct_name)
    df = dct.read_fixed_width(dat_name, **options)
    return df


def sample_rows(df, nrows, replace=False):
    """Choose a sample of rows from a DataFrame.

    df: DataFrame
    nrows: number of rows
    replace: whether to sample with replacement

    returns: DataDf
    """
    indices = np.random.choice(df.index, nrows, replace=replace)
    sample = df.loc[indices]
    return sample


def resample_rows(df):
    """Resamples rows from a DataFrame.

    df: DataFrame

    returns: DataFrame
    """
    return sample_rows(df, len(df), replace=True)


def resample_rows_weighted(df, column='finalwgt'):
    """Resamples a DataFrame using probabilities proportional to given column.

    df: DataFrame
    column: string column name to use as weights

    returns: DataFrame
    """
    weights = df[column].copy()
    weights /= sum(weights)
    indices = np.random.choice(df.index, len(df), replace=True, p=weights)
    sample = df.loc[indices]
    return sample


def resample_by_year(df, column='wtssall'):
    """Resample rows within each year.

    df: DataFrame
    column: string name of weight variable

    returns DataFrame
    """
    grouped = df.groupby('year')
    samples = [resample_rows_weighted(group, column)
               for _, group in grouped]
    sample = pd.concat(samples, ignore_index=True)
    return sample


def values(series):
    """Count the values and sort.
    
    series: pd.Series
    
    returns: series mapping from values to frequencies
    """
    return series.value_counts().sort_index()


def count_by_year(gss, varname):
    """Groups by category and year and counts.

    gss: DataFrame
    varname: string variable to group by

    returns: DataFrame with one row per year, one column per category.
    """
    grouped = gss.groupby([varname, 'year'])
    count = grouped[varname].count().unstack(level=0)

    # note: the following is not ideal, because it does not
    # distinguish 0 from NA, but in this dataset the only
    # zeros are during years when the question was not asked.
    count = count.replace(0, np.nan).dropna()
    return count

def fill_missing(df, varname, badvals=[98, 99]):
    """Fill missing data with random values.

    df: DataFrame
    varname: string column name
    badvals: list of values to be replaced
    """
    # replace badvals with NaN
    df[varname].replace(badvals, np.nan, inplace=True)

    # get the index of rows missing varname
    null = df[varname].isnull()
    n_missing = sum(null)

    # choose a random sample from the non-missing values
    fill = np.random.choice(df[varname].dropna(), n_missing, replace=True)

    # replace missing data with the samples
    df.loc[null, varname] = fill

    # return the number of missing values replaced
    return n_missing


def round_into_bins(df, var, bin_width, high=None, low=0):
    """Rounds values down to the bin they belong in.

    df: DataFrame
    var: string variable name
    bin_width: number, width of the bins

    returns: array of bin values
    """
    if high is None:
        high = df[var].max()

    bins = np.arange(low, high+bin_width, bin_width)
    indices = np.digitize(df[var], bins)
    return bins[indices-1]


def underride(d, **options):
    """Add key-value pairs to d only if key is not in d.

    d: dictionary
    options: keyword args to add to d
    """
    for key, val in options.items():
        d.setdefault(key, val)

    return d


def decorate(**options):
    """Decorate the current axes.
    Call decorate with keyword arguments like
    decorate(title='Title',
             xlabel='x',
             ylabel='y')
    The keyword arguments can be any of the axis properties
    https://matplotlib.org/api/axes_api.html
    In addition, you can use `legend=False` to suppress the legend.
    And you can use `loc` to indicate the location of the legend
    (the default value is 'best')
    """
    loc = options.pop('loc', 'best')
    if options.pop('legend', True):
        legend(loc=loc)

    plt.gca().set(**options)
    plt.tight_layout()


def legend(**options):
    """Draws a legend only if there is at least one labeled item.
    options are passed to plt.legend()
    https://matplotlib.org/api/_as_gen/matplotlib.pyplot.legend.html
    """
    underride(options, loc='best')

    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    #TODO: don't draw if there are none
    ax.legend(handles, labels, **options)

from statsmodels.nonparametric.smoothers_lowess import lowess

def make_lowess(series):
    """Use LOWESS to compute a smooth line.

    series: pd.Series

    returns: pd.Series
    """
    endog = series.values
    exog = series.index.values

    smooth = lowess(endog, exog)
    index, data = np.transpose(smooth)

    return pd.Series(data, index=index)

def plot_series_lowess(series, color):
    """Plots a series of data points and a smooth line.

    series: pd.Series
    color: string or tuple
    """
    series.plot(lw=0, marker='o', color=color, alpha=0.5)
    smooth = make_lowess(series)
    smooth.plot(label='_', color=color)

def plot_columns_lowess(df, columns, colors):
    """Plot the columns in a DataFrame.

    df: pd.DataFrame
    columns: list of column names, in the desired order
    colors: mapping from column names to colors
    """
    for col in columns:
        series = df[col]
        plot_series_lowess(series, colors[col])

def anchor_legend(x, y):
    """Put the legend at the given locationself.

    x: axis coordinate
    y: axis coordinate
    """
    plt.legend(bbox_to_anchor=(x, y), loc='upper left', ncol=1)
