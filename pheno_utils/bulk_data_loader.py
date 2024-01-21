# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/14_bulk_data_loader.ipynb.

# %% auto 0
__all__ = ['FIELD_TYPE_TO_FUNC', 'get_function_for_field_type', 'load_image', 'read_gtf', 'parse_gtf_attributes', 'show_fundus']

# %% ../nbs/14_bulk_data_loader.ipynb 3
from typing import List, Dict, Tuple, Union, Optional
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
    load_func = globals().get(function_name)
    if load_func is None:
        raise ValueError(f"Function {function_name} not found")
    return load_func


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
def read_gtf(filename: str) -> pd.DataFrame:
    """
    Read a GTF file with error handling for lines with too many fields.

    Parameters:
    filename (str): The path to the GTF file.

    Returns:
    pd.DataFrame: A DataFrame where each row corresponds to a line in the GTF file and each column corresponds to a field or attribute.
    """
    # Column names as per GTF specification
    gtf_cols = ['seqname', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame']

    data = []

    with open(filename, 'r') as f:
        for line in f:
            # Ignore comment lines
            if line.startswith('#'):
                continue

            fields = line.strip().split('\t')

            if len(fields) > 9:
                # If there are more than 9 fields, join the extra fields with the 9th field
                fields[8] = '\t'.join(fields[8:])
                fields = fields[:9]

            # Parse the 'attributes' field
            attributes_dict = parse_gtf_attributes(fields[8])

            # Create a dictionary for the row
            row_dict = {**dict(zip(gtf_cols, fields[:8])), **attributes_dict}

            # Append the row dictionary to the list
            data.append(row_dict)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data).astype({'start': 'int', 'end': 'int'})

    return df


def parse_gtf_attributes(attributes_str: str) -> Dict[str, str]:
    """
    Parse attribute column and return a dictionary.

    Parameters:
    attributes_str (str): The attributes as a semicolon-separated string.

    Returns:
    dict: A dictionary where the keys are the attribute names and the values are the attribute values.
    """
    attributes = {}

    # Split the attributes string into individual key-value pairs
    for attribute_str in attributes_str.split(';'):
        # Remove leading/trailing white space
        attribute_str = attribute_str.strip()

        if attribute_str:
            # Split the key and value
            key, value = attribute_str.split(' ')

            # Remove quotes from the value
            value = value.strip('"')

            # Add to attributes dictionary
            attributes[key] = value

    return attributes

# %% ../nbs/14_bulk_data_loader.ipynb 9
def show_fundus(fname: str) -> None:
    warnings.warn('show_fundus() is deprecated in favour of load_image() and will be removed in a future version.')
    load_image(fname)
