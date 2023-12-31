# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/14_bulk_data_loader.ipynb.

# %% auto 0
__all__ = ['FIELD_TYPE_TO_FUNC', 'get_function_for_field_type', 'load_image', 'show_fundus']

# %% ../nbs/14_bulk_data_loader.ipynb 3
import matplotlib.pyplot as plt
from PIL import Image
import warnings
from smart_open import open
import pandas as pd
from pandas import read_parquet

# %% ../nbs/14_bulk_data_loader.ipynb 4
from pheno_utils.config import (
    DICT_PROPERTY_PATH
    )

# %% ../nbs/14_bulk_data_loader.ipynb 5
FIELD_TYPE_TO_FUNC = pd.read_csv(DICT_PROPERTY_PATH, index_col='field_type')['load_func'].dropna().to_dict()

# %% ../nbs/14_bulk_data_loader.ipynb 6
def get_function_for_field_type(field_type):
    function_name = FIELD_TYPE_TO_FUNC.get(field_type, "read_parquet")
    try:
        return globals().get(function_name)
    except:
        raise ValueError(f"Function {function_name} not found")


# %% ../nbs/14_bulk_data_loader.ipynb 7
def load_image(fname: str) -> None:
    """
    Display a fundus image from an input file path.
    Args:
        fname (str): The file path to the fundus image.
    """
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    img = Image.open(open(fname, 'rb'))
    ax.imshow(img, cmap="gray")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')

# %% ../nbs/14_bulk_data_loader.ipynb 8
def show_fundus(fname: str) -> None:
    warnings.warn('show_fundus() is deprecated in favour of load_image() and will be removed in a future version.')
    load_image(fname)
