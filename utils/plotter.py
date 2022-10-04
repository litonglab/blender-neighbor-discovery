from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np



linestyles = OrderedDict(
    [
     # ('loosely dotted',      (0, (1, 10))),
     #('dotted', (0, (1, 4))),
     ('densely dotted', (0, (1, 1))),

     # ('loosely dashed',      (0, (5, 10))),
     #('dashed', (0, (5, 4))),
     ('densely dashed', (0, (5, 1))),

     # ('loosely dashdotted',  (0, (3, 10, 1, 10))),
     #   ('dashdotted',          (0, (3, 5, 1, 5))),
     ('temp', (0, (3, 4, 1, 3))),
#('solid', (0, ())),
     # ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
     # ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1))),
        ('densely dashdotted', (0, (3, 1, 1, 1)))])

def plot_cdf(x, cdf_values, ax=None, ls='--', lw=3, lc='r', label=''):
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(x, cdf_values, ls=ls, lw=lw, c=lc, label=label)
    return ax

def plot_values_as_cdf(values, ax=None, ls='--', lw=3, lc='r', label=''):
    x, counts = np.unique(values, return_counts=True)
    cusum = np.cumsum(counts)
    y = cusum / cusum[-1]
    _ax = plot_cdf(x, y, ax, ls=ls, lw=lw, lc=lc, label=label)
    return _ax

