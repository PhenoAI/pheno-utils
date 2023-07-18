# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_sleep_plots.ipynb.

# %% auto 0
__all__ = ['CHANNELS', 'DEFAULT_CHANNELS', 'COLOR_GROUPS', 'ENUMS', 'CHANNEL_LIMS', 'plot_sleep', 'plot_events', 'plot_channels',
           'format_xticks', 'get_legend_colors']

# %% ../nbs/06_sleep_plots.ipynb 3
from typing import Iterable, Optional

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# %% ../nbs/06_sleep_plots.ipynb 4
CHANNELS = {
    'actigraph': 'Actigraph',
    'body_position': 'Body Position',
    'heart_rate': 'Heart Rate',
    'heart_rate_raw': 'Heart Rate Raw',
    'pat_infra': 'PAT Infra',
    'pat_amplitude': 'PAT Amplitude',
    'pat_lpf': 'PAT LPF',
    'respiratory_movement': 'Respiratory Mov.',
    'spo2': 'SpO2',
    'snore_db': 'Snore dB',
    'pat_view': 'PAT View',
    'sleep_stage': 'Sleep Stage'
    }

DEFAULT_CHANNELS = ['actigraph', 'pat_infra', 'body_position', 'snore_db', 'heart_rate', 'spo2']

COLOR_GROUPS= {
    'actigraph': ['actigraph', 'sleep_stage'],
    'general': ['body_position'],
    'heart_rate': ['heart_rate'],
    'heart_rate_raw': ['heart_rate_raw'],
    'pat_amplitude': ['pat_amplitude'],
    'pat_infra': ['pat_infra', 'pat_view', 'pat_lpf'],
    'respiratory_movement': ['respiratory_movement', 'snore_db'],
    'spo2': ['spo2'],
    }

ENUMS = {'body_position': [[0, 1, 2, 3, 4, 5], ['N/A', 'Supine', 'Right', 'Left', 'Prone', 'Sit']],
         'sleep_stage': [[11, 12, 13, 14, 15], ['Wake', 'REM', 'Light', 'End', 'Deep']]}
CHANNEL_LIMS = {'spo2': [0, 100]}

# %% ../nbs/06_sleep_plots.ipynb 5
def plot_sleep(events: pd.DataFrame, channels: pd.DataFrame,
               array_index: Optional[int] = None,
               trim_to_events: Optional[bool] = True,
               add_events: Optional[pd.DataFrame] = None,
               event_filter: Optional[Iterable[str]] = None,
               channel_filter: Optional[Iterable[str]] = DEFAULT_CHANNELS,
               event_height: float=2, channel_height: float=0.45, width: float=10, aspect: float=0.2,
               style: str='whitegrid',
               xlim: Iterable[float]=None, **kwargs):
    """
    Plot sleep events and channels data.

    Args:

        events (pd.DataFrame): A pandas dataframe containing sleep events data.
        channels (pd.DataFrame): A pandas dataframe containing raw channels data.
        array_index (int, optional): The index of the array. Defaults to None.
        trim_to_events (bool, optional): Whether to trim the plot to the start and end of the events. Defaults to True.
        add_events (pd.DataFrame, optional): Additional events data to include in the plot. Defaults to None.
        event_filter (Iterable[str], optional): A list of events to include in the plot. Defaults to None.
        channel_filter (Iterable[str], optional): A list of channels to include in the plot. Defaults to DEFAULT_CHANNELS.
        event_height (float, optional): The height of the event plot in inches. Defaults to 2.
        channel_height (float, optional): The height of each channel plot in inches. Defaults to 0.45.
        width (float, optional): The width of the plot in inches. Defaults to 10.
        aspect (float, optional): The aspect ratio of the plot. Defaults to 0.2.
        style (str, optional): The seaborn style to use. Defaults to 'whitegrid'.
        xlim (List[float], optional): The x-axis limits of the plot. Defaults to None.
        **kwargs: Additional arguments to be passed to plot_channels().

    Returns:

        None
    """
    nC = min([len(channel_filter), channels.index.get_level_values('source').nunique()])
    if xlim is not None:
        trim_to_events = True

    fig, ax = plt.subplots(nrows=nC+1, ncols=1, sharex=True, squeeze=False,
                           height_ratios=nC*[channel_height] + [event_height],
                           figsize=(width, width*aspect*(nC*channel_height + event_height)),
                           facecolor='white')

    with sns.axes_style(style):
        try:
            plot_channels(channels, array_index=array_index, y_filter=channel_filter, ax=ax[:-1],
                     **kwargs)
            plot_events(events, array_index=array_index, y_include=event_filter, y_exclude=['Gross Trunc'],
                        ax=ax[-1,0],
                        set_xlim=trim_to_events, add_events=add_events,
                        xlim=xlim)
        except Exception as err:
            print(f'plot_channels failed due to:\n{err}')
            fig.clf()
            plot_events(events, array_index, y_include=event_filter, y_exclude=['Gross Trunc'],
                        set_xlim=trim_to_events, add_events=add_events,
                        xlim=xlim)


def plot_events(events: pd.DataFrame, array_index: Optional[int]=None,
                x_start: str='collection_timestamp', x_end: str='event_end',
                y: str='event', color: str='channel', cmap: str='muted', set_xlim: bool=True,
                xlim: Iterable[float]=None, figsize: Iterable[float]=[10, 4],
                y_include: Optional[Iterable[str]] = None,
                y_exclude: Optional[Iterable[str]] = None,
                ax: plt.Axes=None,
                add_events: Optional[pd.DataFrame] = None,
                rename_channels: dict={'PAT Amplitude': 'PAT', 'PulseRate': 'Heart Rate'},
                rename_events: dict={}):
    """ plot an events timeline for a given participant and array_index """
    # slice to night
    if (array_index is not None) and (('array_index' in events.columns) or ('array_index' in events.index.names)):
        plot_df = events.query('array_index == @array_index').copy()
    else:
        plot_df = events.copy()
    # extract start and end times
    if x_start in plot_df.index.names:
        plot_df = plot_df.reset_index(x_start)
    if x_end in plot_df.index.names:
        plot_df = plot_df.reset_index(x_end)
    # remove timezone for correct matplotlib labeling
    plot_df[x_start] = plot_df[x_start].dt.tz_localize(None)
    plot_df[x_end] = plot_df[x_end].dt.tz_localize(None)

    # filter events
    if y_include is not None:
        plot_df = plot_df.query(f'{y} in {y_include}')
    if y_exclude is not None:
        plot_df = plot_df.query(f'{y} not in {y_exclude}')
    # additional user-provided events (application logging, etc.)
    if add_events is not None:
        tlim = plot_df[x_start].min(), plot_df[x_end].max()
        add_events = add_events.loc[
            (tlim[0] < add_events[x_end]) & (add_events[x_start] < tlim[1])]
        if len(add_events):
            add_events = add_events.set_index(plot_df.index[[0]])
        plot_df = pd.concat([plot_df, add_events[
            plot_df.columns.intersection(add_events.columns)]], axis=0)

    # rename channels and events
    plot_df = plot_df.copy()
    plot_df['channel'] = plot_df['channel'].replace(rename_channels)
    plot_df['event'] = plot_df['event'].replace(rename_events)

    # set x limits
    if xlim is not None:
        if type(xlim[0]) is str:
            xlim = (pd.to_datetime(xlim[0]), xlim[1])
        if type(xlim[0]) is not pd.Timestamp:
            xlim = plot_df.loc[plot_df['start'] < xlim[0], x_start].iloc[-1], xlim[1]
        if type(xlim[1]) is str:
            xlim = (xlim[0], pd.to_datetime(xlim[1]))
        if type(xlim[1]) is not pd.Timestamp:
            xlim = xlim[0], plot_df.loc[plot_df['end'] > xlim[1], x_end].iloc[0]
    else:
        xlim = plot_df[x_start].min(), plot_df[x_end].max()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    # set colors
    colors = sorted(plot_df[color].unique())
    colors = pd.DataFrame({color: colors, 'color': sns.color_palette(cmap, len(colors))})\
        .set_index(color)['color']

    # plot events
    plot_df = plot_df.assign(diff=lambda x: x[x_end] - x[x_start]).sort_values([color, y])
    labels = []
    legend = []
    for i, (y_label, y) in enumerate(plot_df.groupby(y, sort=False)):
        if len(y) == 0:
            continue
        labels.append(y_label)
        for c, r in y.groupby(color):
            data = r[[x_start, 'diff']]
            if not len(data):
                continue
            h = ax.broken_barh(data.values, (i-0.4,0.8), color=colors[c], alpha=0.7)
            legend.append({'label': c, 'handle': h})

    # format plot
    legend = pd.DataFrame.from_dict(legend).drop_duplicates(subset='label')
    ax.legend(legend['handle'], legend['label'],
              bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    str_title = ''
    if 'participant_id' in events.index.names:
        str_title += events.index.get_level_values('participant_id')[0].astype(str)
    if array_index is not None:
        str_title += f' / {array_index}'
    plt.suptitle(str_title, fontsize=14, weight='bold')
    ax.set_yticks(np.arange(len(labels)), labels)
    plt.tight_layout()
    ax.set_xlabel('Time')
    if set_xlim:
        ax.set_xlim(*xlim)
    format_xticks(ax)

    return ax


def plot_channels(channels: pd.DataFrame, array_index: Optional[int]=None,
             y_filter: Optional[Iterable[str]]=None, ax: plt.Axes=None,
             discrete_events: Optional[Iterable[str]]=['sleep_stage', 'body_position'],
             time_col='collection_timestamp', height=1.5, resample='1s', cmap='muted',
             rename_channels=CHANNELS, **kwargs):
    """ plot channels data for a given participant and array_index """
    # set colors
    colors = get_legend_colors(cmap).explode('source')
    colors['source'] = pd.Categorical(colors['source'])
    colors = colors.set_index('source')

    # filter data
    if (array_index is not None) and (('array_index' in channels.columns) or ('array_index' in channels.index.names)):
        data = channels.query('array_index == @array_index').copy()
    else:
        data = channels.copy()
    # extract time and channel name
    if time_col in channels.index.names:
        data = data.reset_index(time_col)
    if 'source' not in data.index.names:
        data = data.set_index('source')
    data[time_col] = data[time_col].dt.tz_localize(None)

    # grouping and coloring sources by event "channels"
    data = data.join(colors[['channel']])\
        .sort_values(['channel', time_col], ascending=[False, True])

    if ax is None:
        n = data.index.unique().size
        fig, ax = plt.subplots(nrows=n, figsize=(10, n*height), sharex=True, squeeze=False)

    # plot data
    ax_shift = 0
    for i, (source, d) in enumerate(data.groupby('source', sort=False)):
        if (source not in CHANNELS) or (y_filter is not None and source not in y_filter):
            print(f'plot_channels: skipping {source}')
            ax_shift += 1
            continue
        iax = i - ax_shift
        if resample is not None:
            d = d.resample(resample, on=time_col).mean(numeric_only=True).reset_index()
        if source in colors.index:
            c = colors.loc[source, 'color']
        else:
            c = 'grey'
        if source in CHANNEL_LIMS:
            d = d.loc[(CHANNEL_LIMS[source][0] <= d['values']) & (d['values'] <= CHANNEL_LIMS[source][1])]
        ax[iax, 0].scatter(d[time_col].dt.tz_localize(None).values, d['values'].values, s=0.1, color=c)
        if source not in CHANNEL_LIMS:
            ylim = d['values'].quantile([0.001, 0.999]).tolist()
            ylim[0] = 0.95*ylim[0] if ylim[0] >= 0 else 1.1*ylim[0]
            ylim[1] = 1.1*ylim[1] if ylim[1] >= 0 else 0.95*ylim[1]
            ax[iax,0].set_ylim(*ylim)
        if source in rename_channels:
            ax[iax, 0].set_ylabel(rename_channels[source], rotation=0, horizontalalignment='right')
        else:
            ax[iax,0].set_ylabel(source, rotation=0, horizontalalignment='right')

        if source in discrete_events:
            if source in ENUMS:
                ax[iax, 0].set_yticks(ENUMS[source][0],labels=ENUMS[source][1])
            else:
                ax[iax, 0].set_yticks(d['values'].drop_duplicates().sort_values().values)
                ylabels = ax[iax, 0].get_yticklabels()
                for label in ylabels[1:-1]:
                    label.set_text('')
                ax[iax, 0].set_yticklabels(ylabels)

    # format plot
    for i in range(len(ax)):
        ax[i,0].set_xlabel('')
        ax[i,0].set_xticklabels([])
    if ax is None:
        print('entered')
        ax[-1,0].set_xlabel('Time')
        ax[-1,0].set_xlim(data[time_col].min(), data[time_col].max())
        format_xticks(ax[-1,0])


    return ax


def format_xticks(ax, format='%m/%d %H:%M'):
    """ format datestrings on x axis """
    xticks = ax.get_xticks()
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, rotation=25, ha='right')
    xfmt = mdates.DateFormatter(format)
    ax.xaxis.set_major_formatter(xfmt)


def get_legend_colors(cmap='muted'):
    # the following dict keys should correspond to sleep event channels
    colors = pd.Series(COLOR_GROUPS, name='source').to_frame().reset_index()\
        .rename(columns={'index': 'channel'}).sort_values('channel')
    colors['color'] = sns.color_palette(cmap, len(colors))

    return colors

