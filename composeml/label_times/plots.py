import matplotlib as mpl  # isort:skip

# Raises an import error on OSX if not included.
# https://matplotlib.org/3.1.0/faq/osx_framework.html#working-with-matplotlib-on-osx
mpl.use('agg')  # noqa

import pandas as pd
import seaborn as sns

pd.plotting.register_matplotlib_converters()
sns.set_context('notebook')
sns.set_style('darkgrid')
COLOR = sns.color_palette("Set1", n_colors=100, desat=.75)


class LabelPlots:
    """Creates plots for Label Times."""

    def __init__(self, label_times):
        """Initializes Label Plots.

        Args:
            label_times (LabelTimes) : instance of Label Times
        """
        self._label_times = label_times

    def count_by_time(self, ax=None, **kwargs):
        """Plots the label distribution across cutoff times."""
        count_by_time = self._label_times.count_by_time
        count_by_time.sort_index(inplace=True)
        target_column = self._label_times.target_columns[0]

        ax = ax or mpl.pyplot.axes()
        vmin = count_by_time.index.min()
        vmax = count_by_time.index.max()
        ax.set_xlim(vmin, vmax)

        locator = mpl.dates.AutoDateLocator()
        formatter = mpl.dates.AutoDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.figure.autofmt_xdate()

        if len(count_by_time.shape) > 1:
            ax.stackplot(
                count_by_time.index,
                count_by_time.values.T,
                labels=count_by_time.columns,
                colors=COLOR,
                alpha=.9,
                **kwargs,
            )

            ax.legend(
                loc='upper left',
                title=target_column,
                facecolor='w',
                framealpha=.9,
            )

            ax.set_title('Label Count vs. Cutoff Times')
            ax.set_ylabel('Count')
            ax.set_xlabel('Time')

        else:
            ax.fill_between(
                count_by_time.index,
                count_by_time.values.T,
                color=COLOR[1],
            )

            ax.set_title('Label vs. Cutoff Times')
            ax.set_ylabel(target_column)
            ax.set_xlabel('Time')

        return ax

    @property
    def dist(self):
        """Alias for distribution."""
        return self.distribution

    def distribution(self, **kwargs):
        """Plots the label distribution."""
        target_column = self._label_times.target_columns[0]
        dist = self._label_times[target_column]
        is_discrete = self._label_times.is_discrete[target_column]

        if is_discrete:
            ax = sns.countplot(dist, palette=COLOR, **kwargs)
        else:
            ax = sns.distplot(dist, kde=True, color=COLOR[1], **kwargs)

        ax.set_title('Label Distribution')
        ax.set_ylabel('Count')
        return ax