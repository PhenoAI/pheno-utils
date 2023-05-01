# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_subset_loader.ipynb.

# %% auto 0
__all__ = ['subset_path', 'load_subset']

# %% ../nbs/10_subset_loader.ipynb 3
import numpy as np
import pandas as pd

# %% ../nbs/10_subset_loader.ipynb 4
from .config import *
from . import PhenoLoader, MetaLoader

subset_path = {'train': '/home/ec2-user/studies/train_datasets',
               'test_01': '/efs/.pheno/test_datasets_01',
               'test_02': '/efs/.pheno/test_datasets_02',
               'test_final': '/efs/.pheno/test_datasets_final',
               'test_backup': '/efs/.pheno/test_datasets_backup'}

# %% ../nbs/10_subset_loader.ipynb 5
def load_subset(subset: str, dataset: str=None, loader: str='data', age_sex_dataset=None, **kwargs):
    """
    Wrapper for loading a train/test subset of a dataset.
    Args:

        subset (str): Can be one of 'train', 'test_01', 'test_02', 'test_final'.
        dataset (str): Name of the dataset to load. Not needed when requesting a MetaLoader.
        loader (str): Can be one of 'meta', 'data'.

        **kwargs: Additional keyword arguments to be passed to PhenoLoader / MetaLoader.
    Returns:

        DataLoader MetaLoader object: An object for the specified subset of the dataset.
    """
    if subset not in subset_path.keys():
        ValueError(f"Subset {subset} not found. Must be one of {subset_path.keys()}")
    if loader == 'meta':
        return MetaLoader(base_path=subset_path[subset], **kwargs)

    return PhenoLoader(dataset, base_path=subset_path[subset], age_sex_dataset=age_sex_dataset, **kwargs)
