import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-darkgrid')
plt.switch_backend('agg')
palette = plt.get_cmap('Set2')

from typing import List, Optional, Tuple, Union
from typing import Literal

StrOrStrList = Union[str, List[str]]


class GraphVisualizer:
    '''
      Common data visaulize helper for group project of team #8.
    '''

    def __init__(self, alpha=1.0, colors=sns.color_palette('pastel')):
        '''
        Initialize the visualizer.

        Prameters:
          alpha: float, default 1.0
            Custom plots alpha value, alpha must be within the 0-1 range, inclusive.
          colors: TODO, default sns.color_palette('pastel')
            List of colors or continuous colormap defining a palette.
        '''

        self.alpha = alpha
        self.colors = colors

    def make_bar_plot(self,
                      data: pd.DataFrame = None, figsize=(20, 10), ax: plt.Axes = None, **kwargs) -> Optional[
        plt.Figure]:
        '''
        Shows bar plot with sns.barplot.

        Prameters:
          data: Optional[pd.DataFrame], default None
            Dataset for plotting with x/y columns.
          figsize: Tuple[int, int], default (20, 10)
            Plot figsize.
          title: Optional[str], default None
            Plot title text.
          xlabel, ylabel: Optional[str], default None
            Plot axis labels text.
          title_size: int, default 16
            Plot title font size.
          label_size: int, default 14
            Plot axis labels font size.
          ax: Optional[plt.Axes], default None
            Axes object to draw the plot onto, otherwise generates own Axes.
          x_logscale, y_logscale: bool, default False
            If True axis scale type equals 'log'.
          xticks, yticks: Optional[List[str]], default None
            Plot ticks list.
          xticks_by, yticks_by: int, default -1
            Plot ticks stepw, -1 means auto sns ticks generating.
          xticks_rotation, yticks_rotation: int, default 0
            Plot axis ticks roatation angle.

        Returns:
          fig: Optional[plt.Figure]
            Returns pyplot figure if axes was not passed, otherwise None.
        '''

        fig: plt.Figure = None
        ax: plt.Axes = ax

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            ax = ax

        sns.barplot(data=data, x=data.get('x', None), y=data.get('y', None), ax=ax, alpha=self.alpha)

        self._configure_axes(
            ax,
            data.get('x', None),
            data.get('y', None),
            **kwargs
        )

        return fig

    def make_bar_multiplot(self,
                           data: List[pd.DataFrame], title: StrOrStrList = None,
                           xlabel: StrOrStrList = None, ylabel: StrOrStrList = None,
                           direction: Literal['row', 'col'] = 'row', sharex=False, sharey=False,
                           figsize=(20, 10), **kwargs) -> plt.Figure:
        '''
        Shows multiple bar plot with sns.barplot within single figure.

        Prameters:
          data: BarMultichartData
            List of dataframes with x/y columns.
          direction: Literal['row', 'col'], default 'row'
            Direction for placing plots.
          sharex, sharey: bool, default False
            If true x/y axis labels will be shared between plots.
          figsize: Tuple[int, int], default (20, 10)
            Plot figsize.
          title: Optional[StrOrStrList], default None
            Plot title text or list of titles for each plot.
          xlabel, ylabel: Optional[StrOrStrList], default None
            Plot axis labels text or list of labels for each plot.
          title_size: int, default 16
            Plot title font size.
          label_size: int, default 14
            Plot axis labels font size.
          x_logscale, y_logscale: bool, default False
            If True axis scale type equals 'log'.
          xticks, yticks: Optional[List[str]], default None
            Plot ticks list.
          xticks_by, yticks_by: int, default -1
            Plot ticks stepw, -1 means auto sns ticks generating.
          xticks_rotation, yticks_rotation: int, default 0
            Plot axis ticks roatation angle.

        Returns:
          fig: plt.Figure
            Returns pyplot figure.
        '''

        nrows = 1 if direction == 'row' else len(data)
        ncols = 1 if direction == 'col' else len(data)

        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, sharex=sharex, sharey=sharey)

        for (i, graph_data) in enumerate(data):
            item_title = title[i] if type(title) is list else title
            item_xlabel = xlabel[i] if type(xlabel) is list else xlabel
            item_ylabel = ylabel[i] if type(ylabel) is list else ylabel

            item_xlabel = '' if sharex and i < len(data) - 1 else item_xlabel
            item_ylabel = '' if sharey and i > 0 else item_ylabel

            self.make_bar_plot(
                data=graph_data,
                title=item_title,
                xlabel=item_xlabel,
                ylabel=item_ylabel,
                figsize=figsize,
                ax=axs[i],
                **kwargs
            )

        return fig

    def make_pie_chart(self,
                       data: pd.DataFrame, title: str = None, labels: List[str] = None,
                       title_size=16, label_size=14, figsize=(10, 10),
                       autopct='%1.0f%%', **kwargs) -> plt.Figure:
        '''
        Shows pie chart plot with plt.pie.

        Prameters:
          data: pd.DataFrame
            Dataset for drawing chart.
          title: Optional[str], default None
            Chart title text.
          labels: Optional[List[str]], default None
            Chart slice labels&.
          title_size: int, default 16
            Chart title font size.
          label_size: int, default 14
            Chart labels font size.
          figsize: Tuple[int, int], default (10, 10)
            Plot figsize.
          autopct: Optional[str or callable], default: '%1.0f%%'
            If not None, is a string or function used to label the wedges with their numeric value.
            The label will be placed inside the wedge. If it is a format string, the label will be fmt % pct.
            If it is a function, it will be called.

        Returns:
          fig: plt.Figure
            Returns pyplot figure.
        '''

        fig, ax = plt.subplots(figsize=figsize)

        ax.pie(data, labels=labels, autopct=autopct, colors=self.colors, textprops={'fontsize': label_size})

        ax.set_alpha(self.alpha)

        if title is not None:
            ax.set_title(title, fontsize=title_size)

        return fig

    def make_scatter_plot(self,
                          data: pd.DataFrame = None, figsize=(20, 10),
                          alpha: float = None, **kwargs) -> plt.Figure:
        '''
        Shows scatter plot with sns.scatterplot.

        Prameters:
          data: Optional[pd.DataFrame], default None
            Dataset for plotting with x/y columns.
          figsize: Tuple[int, int], default (20, 10)
            Plot figsize.
          title: Optional[str], default None
            Plot title text.
          xlabel, ylabel: Optional[str], default None
            Plot axis labels text.
          title_size: int, default 16
            Plot title font size.
          label_size: int, default 14
            Plot axis labels font size.
          alpha: float, default GraphVisualizer instance alpha property
            Custom plot dots alpha value.
          x_logscale, y_logscale: bool
            If True axis scale type equals 'log', default False.
          xticks, yticks: Optional[List[str]], default None
            Plot ticks list.
          xticks_by, yticks_by: int, default -1
            Plot ticks step, -1 means auto sns ticks generating.
          xticks_rotation, yticks_rotation: int, default 0
            Plot axis ticks roatation angle.

        Returns:
          fig: plt.Figure
            Returns pyplot figure.
        '''

        fig, ax = plt.subplots(figsize=figsize)

        if alpha is None:
            alpha = self.alpha

        sns.scatterplot(data=data, x=data.get('x', None), y=data.get('y', None), ax=ax, alpha=alpha)

        self._configure_axes(
            ax,
            data.get('x', None),
            data.get('y', None),
            **kwargs
        )

        return fig

    def make_hist_plot(self,
                       data: pd.DataFrame = None, figsize=(20, 10),
                       bins=10, discrete=False, **kwargs) -> plt.Figure:
        '''
        Shows histogram plot with sns.histplot.

        Prameters:
          data: Optional[pd.DataFrame], default None
            Dataset for plotting with x/y columns.
          figsize: Tuple[int, int], default (20, 10)
            Plot figsize.
          title: Optional[str], default None
            Plot title text.
          xlabel, ylabel: Optional[str], default None
            Plot axis labels text.
          title_size: int, default 16
            Plot title font size.
          label_size: int, default 14
            Plot axis labels font size.
          alpha: float, default GraphVisualizer instance alpha property
            Custom plot dots alpha value.
          x_logscale, y_logscale: bool, default False
            If True axis scale type equals 'log'.
          xticks, yticks: Optional[List[str]], default None
            Plot ticks list.
          xticks_by, yticks_by: int, default -1
            Plot ticks step, -1 means auto sns ticks generating.
          xticks_rotation, yticks_rotation: int, default 0
            Plot axis ticks roatation angle.

        Returns:
          fig: plt.Figure
            Returns pyplot figure.
        '''

        fig, ax = plt.subplots(figsize=figsize)

        sns.histplot(data=data, x=data.get('x', None), y=data.get('y', None), ax=ax, bins=bins, discrete=discrete,
                     alpha=self.alpha)

        self._configure_axes(
            ax,
            data.get('x', None),
            data.get('y', None),
            **kwargs
        )

        return fig

    def _configure_axes(self,
                        ax: plt.Axes, data_x: pd.Series = None, data_y: pd.Series = None,
                        title: str = None, xlabel: str = None, ylabel: str = None, title_size=16, label_size=14,
                        xticks: List[str] = None, yticks: List[str] = None, xticks_by=-1, yticks_by=-1,
                        x_logscale=False, y_logscale=False, xticks_rotation=0, yticks_rotation=0, **kwargs):
        '''
        Configures plot axis display.

        Prameters:
          ax: plt.Axes
            Axes object to configure.
          data_x, data_y: Optional[pd.Series], default None
            Series to generate ticks.
          title: Optional[str], default None
            Plot title text.
          xlabel, ylabel: Optional[str], default None
            Plot axis labels text.
          title_size: int, default 16
            Plot title font size.
          label_size: int, default 14
            Plot axis labels font size.
          xticks, yticks: Optional[List[str]], default None
            Plot ticks list.
          x_logscale, y_logscale: bool, default False
            If True axis scale type equals 'log'.
          xticks_by, yticks_by: int, default -1
            Plot ticks step, -1 means auto sns ticks generating.
          xticks_rotation, yticks_rotation: int, default 0
            Plot axis ticks roatation angle.

        Returns: None.
        '''

        if title is not None:
            ax.set_title(title, fontsize=title_size)

        if xlabel is not None:
            ax.set_xlabel(xlabel, fontsize=label_size)

        if ylabel is not None:
            ax.set_ylabel(ylabel, fontsize=label_size)

        if x_logscale:
            ax.set_xscale('log')

        if y_logscale:
            ax.set_yscale('log')

        if xticks is not None:
            ax.xaxis.set_ticks(xticks)
        elif xticks_by != -1:
            ax.xaxis.set_ticks(np.arange(min(0, min(data_x)), max(data_x) + xticks_by, xticks_by))

        if yticks is not None:
            ax.yaxis.set_ticks(yticks)
        elif yticks_by != -1:
            ax.yaxis.set_ticks(np.arange(min(0, min(data_y)), max(data_y) + yticks_by, yticks_by))

        if xticks_rotation != 0:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=xticks_rotation)

        if yticks_rotation != 0:
            ax.set_yticklabels(ax.get_yticklabels(), rotation=yticks_rotation)
