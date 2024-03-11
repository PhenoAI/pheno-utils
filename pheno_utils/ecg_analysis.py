# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_ecg_analysis.ipynb.

# %% auto 0
__all__ = ['vis_ecg']

# %% ../nbs/09_ecg_analysis.ipynb 3
from typing import Tuple

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# %% ../nbs/09_ecg_analysis.ipynb 4
def vis_ecg(values_df: pd.DataFrame) -> None:
    """
    Visualize ECG data for 12 leads.

    Args:
        values_df (pd.DataFrame): A DataFrame containing ECG data with 12 columns, one for each lead.

    Returns:
        None: Displays a 3x4 grid of ECG plots for the 12 leads.
    """
    count = 0
    frequency = 1000
    time_data = np.arange(values_df.shape[0]) / frequency
    sns.set(rc={'figure.figsize':(40.7,18.27)})
    fig, axs = plt.subplots(3, 4)
    
    for y in range(0,4):    
        for x in range(0,3):
            col = values_df.columns[count]
            axs[x, y].plot(time_data, values_df[col].values)
            axs[x, y].set_title(col)
            count += 1
            plt.xlabel("time in seconds")
            plt.ylabel("ECG in uV")

