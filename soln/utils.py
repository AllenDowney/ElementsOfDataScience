"""Supporting code for Elements of Data Science

by Allen Downey

MIT License
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import contextlib
import gzip
import io
import re
import textwrap
import os

from IPython.core.magic import register_cell_magic
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

from os.path import basename, exists
from statsmodels.nonparametric.smoothers_lowess import lowess


# Make the figures smaller to save some screen real estate.
# The figures generated for the book have DPI 400, so scaling
# them by a factor of 4 restores them to the size in the notebooks.
plt.rcParams["figure.dpi"] = 75
plt.rcParams["figure.figsize"] = [6, 3.5]


def wrap(obj):
    for line in textwrap.wrap(str(obj), subsequent_indent="    "):
        print(line)


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
        self.colspecs = variables[["start", "end"]] - index_base

        # convert colspecs to a list of pair of int
        self.colspecs = self.colspecs.astype(np.int).values.tolist()
        self.names = variables["name"]

    def read_fixed_width(self, filename, **options):
        """Reads a fixed width ASCII file.

        filename: string filename

        returns: DataFrame
        """
        df = pd.read_fwf(filename, colspecs=self.colspecs, names=self.names, **options)
        return df


def read_stata_dict(dct_file, **options):
    """Reads a Stata dictionary file.

    dct_file: string filename
    options: dict of options passed to open()

    returns: FixedWidthVariables object
    """
    type_map = dict(
        byte=int, int=int, long=int, float=float, double=float, numeric=float
    )

    var_info = []
    with open(dct_file, **options) as f:
        for line in f:
            match = re.search(r"_column\(([^)]*)\)", line)
            if not match:
                continue
            start = int(match.group(1))
            t = line.split()
            vtype, name, fstring = t[1:4]
            name = name.lower()
            if vtype.startswith("str"):
                vtype = str
            else:
                vtype = type_map[vtype]
            long_desc = " ".join(t[4:]).strip('"')
            var_info.append((start, vtype, name, fstring, long_desc))

    columns = ["start", "type", "name", "fstring", "desc"]
    variables = pd.DataFrame(var_info, columns=columns)

    # fill in the end column by shifting the start column
    variables["end"] = variables.start.shift(-1)
    variables.loc[len(variables) - 1, "end"] = 0

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


def resample_rows_weighted(df, column="finalwgt"):
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


def resample_by_year(df, column="wtssall"):
    """Resample rows within each year.

    df: DataFrame
    column: string name of weight variable

    returns DataFrame
    """
    grouped = df.groupby("year")
    samples = [resample_rows_weighted(group, column) for _, group in grouped]
    sample = pd.concat(samples, ignore_index=True)
    return sample


def values(series):
    """Count the values and sort.

    series: pd.Series

    returns: series mapping from values to frequencies
    """
    return series.value_counts(dropna=False).sort_index()


def count_by_year(gss, varname):
    """Groups by category and year and counts.

    gss: DataFrame
    varname: string variable to group by

    returns: DataFrame with one row per year, one column per category.
    """
    grouped = gss.groupby([varname, "year"])
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

    bins = np.arange(low, high + bin_width, bin_width)
    indices = np.digitize(df[var], bins)
    return bins[indices - 1]


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
    loc = options.pop("loc", "best")
    if options.pop("legend", True):
        legend(loc=loc)

    plt.gca().set(**options)
    plt.tight_layout()


def legend(**options):
    """Draws a legend only if there is at least one labeled item.
    options are passed to plt.legend()
    https://matplotlib.org/api/_as_gen/matplotlib.pyplot.legend.html
    """
    underride(options, loc="best")

    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, **options)


def make_lowess(series, frac=2 / 3):
    """Use LOWESS to compute a smooth line.

    series: pd.Series

    returns: pd.Series
    """
    y = series.values
    x = series.index.values

    smooth = lowess(y, x, frac=frac)
    index, data = np.transpose(smooth)
    return pd.Series(data, index=index)


def plot_lowess(series, color, frac=0.7, **options):
    """Plot a smooth line.

    series: pd.Series
    color: string or tuple
    """
    if "label" not in options:
        options["label"] = series.name

    smooth = make_lowess(series, frac=frac)
    smooth.plot(color=color, **options)


def plot_series_lowess(series, color, frac=0.7, **options):
    """Plots a series of data points and a smooth line.

    series: pd.Series
    color: string or tuple
    """
    if "label" not in options:
        options["label"] = series.name

    x = series.index
    y = series.values

    if len(series) == 1:
        # just plot the point
        plt.plot(x, y, "o", color=color, alpha=0.5, label=options["label"])
    else:
        # plot the points and line
        plt.plot(x, y, "o", color=color, alpha=0.5, label="_")
        plot_lowess(series, color, frac, **options)


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
    plt.legend(bbox_to_anchor=(x, y), loc="upper left", ncol=1)


def download(url):
    filename = basename(url)
    if not exists(filename):
        from urllib.request import urlretrieve

        local, _ = urlretrieve(url, filename)
        print("Downloaded " + local)


def read_gss(dict_file="GSS.dct", data_file="GSS.dat.gz"):
    from statadict import parse_stata_dict

    download(
        "https://github.com/AllenDowney/"
        + "ElementsOfDataScience/raw/master/data/"
        + dict_file
    )

    download(
        "https://github.com/AllenDowney/"
        + "ElementsOfDataScience/raw/master/data/"
        + data_file
    )

    stata_dict = parse_stata_dict(dict_file)
    fp = gzip.open(data_file)
    gss = pd.read_fwf(fp, names=stata_dict.names, colspecs=stata_dict.colspecs)
    return gss


def traceback(mode):
    """Set the traceback mode.

    mode: string
    """
    # this context suppresses the output
    with contextlib.redirect_stdout(io.StringIO()):
        get_ipython().run_cell(f"%xmode {mode}")


traceback("Minimal")


def extract_function_name(text):
    """Find a function definition and return its name.

    text: String

    returns: String or None
    """
    pattern = r"def\s+(\w+)\s*\("
    match = re.search(pattern, text)
    if match:
        func_name = match.group(1)
        return func_name
    else:
        return None


@register_cell_magic
def expect_error(line, cell):
    try:
        get_ipython().run_cell(cell)
    except Exception as e:
        get_ipython().run_cell("%tb")


@magic_arguments()
@argument("exception", help="Type of exception to catch")
@register_cell_magic
def expect(line, cell):
    args = parse_argstring(expect, line)
    exception = eval(args.exception)
    try:
        get_ipython().run_cell(cell)
    except exception as e:
        get_ipython().run_cell("%tb")
