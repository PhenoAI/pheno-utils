# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/12_cohort_selector.ipynb.

# %% auto 0
__all__ = ['CohortSelector']

# %% ../nbs/12_cohort_selector.ipynb 3
import re
from typing import List, Any, Dict, Union
import warnings

import numpy as np
import pandas as pd

# %% ../nbs/12_cohort_selector.ipynb 4
from pheno_utils.config import (
    DATASETS_PATH, 
    COHORT, 
    ERROR_ACTION
)
from .meta_loader import MetaLoader

# %% ../nbs/12_cohort_selector.ipynb 5
class CohortSelector:
    """
    Class for selecting a subset of a cohort's data based on a query.

    Args:

        base_path (str, optional): Base path of the datasets. Defaults to DATASETS_PATH.
        cohort (str, optional): Name of the cohort. Defaults to COHORT.
        errors (str, optional): Error action. Defaults to ERROR_ACTION.
        **kwargs: Additional keyword arguments.

    Attributes:

        cohort (str): Name of the cohort.
        base_path (str): Base path of the datasets.
        errors (str): Error action.
        kwargs: Additional keyword arguments.
        ml (MetaLoader): MetaLoader object for loading metadata and data.

    """

    def __init__(
        self,
        base_path: str = DATASETS_PATH,
        cohort: str = COHORT,
        errors: str = ERROR_ACTION,
        **kwargs,
    ) -> None:
        """
        Initialize CohortSelector object.

        Args:

            base_path (str, optional): Base path of the datasets. Defaults to DATASETS_PATH.
            cohort (str, optional): Name of the cohort. Defaults to COHORT.
            errors (str, optional): Error action. Defaults to ERROR_ACTION.
            **kwargs: Additional keyword arguments.

        """
        self.cohort = cohort
        self.base_path = base_path
        self.errors = errors
        self.kwargs = kwargs

        self.ml = MetaLoader(
            base_path=self.base_path, cohort=self.cohort,
            flexible_field_search=False, errors=self.errors,
            **self.kwargs)

    def select(self, query: str) -> pd.DataFrame:
        """
        Select a subset of the cohort's data based on the given query.

        Args:

            query (str): Query string to filter the data.

        Returns:

            pd.DataFrame: Filtered DataFrame based on the query.

        Raises:

            ValueError: If no column names are found in the query.
            ValueError: If column names in the query do not match the column names in the metadata.

        """
        column_names = re.findall(r'([a-zA-Z][a-zA-Z0-9_]*)\b', query)
        if not column_names:
            raise ValueError('No column names found in query')

        test_cols = self.ml.get(column_names)    
        missing_cols = [col for col in column_names
                        if col not in test_cols.columns.str.split('/').str[1]]
        if len(missing_cols):
            raise ValueError(f'Column names {missing_cols} in query do not match column names in metadata')

        df = self.ml.load(column_names)

        return df.query(query)

