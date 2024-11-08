# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/13_questionnaire_handler.ipynb.

# %% auto 0
__all__ = ['valid_codings', 'convert_to_string', 'normalize_answers', 'flatten_series', 'check_invalid_values', 'replace_values',
           'transform_answers', 'convert_codings_to_int', 'transform_dataframe']

# %% ../nbs/13_questionnaire_handler.ipynb 3
import pandas as pd
import numpy as np
import warnings

# %% ../nbs/13_questionnaire_handler.ipynb 4
valid_codings = ["hebrew", "english", "coding"]

# %% ../nbs/13_questionnaire_handler.ipynb 6
def convert_to_string(x):
    #function converts a float to a string and for floats of type 1.0 it becomes '1'
    return str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)

def normalize_answers(orig_answer: pd.Series, field_type: str) -> pd.Series:
    """
    Normalize the answers to be strings. Need to handle nulls which become strings initially and want them to still be na.

    Args:
        orig_answer (pd.Series): The original answer series.

    Returns:
        pd.Series: The normalized answer series.
    """
    if field_type == 'Categorical (multiple)':
        normalized_answer =  orig_answer.apply(lambda x: [str(i) for i in x] if isinstance(x, np.ndarray) else x)
    else:
        # Convert the entire series to strings, np.nan will become 'nan'
        normalized_answer = orig_answer.astype(str)

        # Replace float-like strings with integer-like strings, ignoring 'nan'
        normalized_answer = normalized_answer.str.replace(r"\.0$", "", regex=True)

        # Replace 'nan' with np.nan and similar when dtype is Int64
        normalized_answer = normalized_answer.replace("nan", np.nan) 
        normalized_answer = normalized_answer.replace("None", np.nan) 
        normalized_answer = normalized_answer.replace("<NA>", np.nan)

    return normalized_answer

def flatten_series(series: pd.Series) -> list:
    """
    Flatten a Pandas Series into a list, where each element of the Series can be
    an individual value or a list of values.

    Parameters:
    series (pd.Series): A Pandas Series where each element can be a single value
                        or a list of values.

    Returns:
    list: A flattened list containing all the individual elements from the Series,
          including those within lists.
    """
    flat_list = []
    for item in series:
        if isinstance(item, list) or isinstance(item, np.ndarray):
            flat_list.extend(item)
        elif not pd.isna(item):
            flat_list.append(item)
    return flat_list

def check_invalid_values(series: pd.Series, mapping_df: pd.DataFrame ):
    """
    Check if values in normalized_answer exist in code_df[code_from], excluding np.nan.
    This check is used to compare the data codings and actual values in the series to make sure there are no invalid values for categoircal single 

    Args:
        mapping_df (pd.DataFrame): A dataframe whereall the data codings are stored
                         and the values represent the values to replace with.
        series (pd.Series): The normalized answer series.

    Returns:
        None: Prints the invalid values found, if any.
    """
    # Check if series contains arrays if it does then it is categorical multiple and we need to flatten the serries first
    contains_arrays = series.dropna().apply(lambda x:  isinstance(x, list) or isinstance(x, np.ndarray))
    
    if True in contains_arrays.unique():
        answer_values = set(flatten_series(series))
    else:
        answer_values = set(series.dropna())
    
    valid_values = set()
    for coding in valid_codings:
        valid_values.update(set(mapping_df[coding].unique()))
    
    invalid_values = answer_values - valid_values
    
    if invalid_values:
        warnings.warn(f"Invalid values found: {invalid_values}")


def replace_values(row: pd.Series, mapping_dict: dict) -> [pd.Series, list, float]:
    """
    Replace values in a row with corresponding values from a mapping dictionary used for categorical multiple questions
    
    Parameters:
    row (pd.Series): A Pandas Series or a list. Each element of the Series can be
                     an individual value or a list of values.
    mapping_dict (dict): A dictionary where the keys represent original values
                         and the values represent the values to replace with.

    Returns:
    pd.Series, list, or float: Transformed row with values replaced according
                               to the mapping dictionary. If the original value
                               is a list or an ndarray, it returns a list. If the
                               original value is NaN, it returns a float (np.nan).
    """
    if isinstance(row, np.ndarray) or isinstance(row, list):
        row = list(row)  if isinstance(row, np.ndarray) else row
        return np.array([mapping_dict.get(item, item) for item in row])
    elif pd.isna(row) or pd.isnull(row):
        return None
    else:
        warnings.warn("row is not a array or list")
        return row

def transform_answers(
    tab_field_name: str,
    orig_answer: pd.Series,
    transform_from: str,
    transform_to: str,
    dict_df: pd.DataFrame,
    mapping_df: pd.DataFrame,
) -> pd.Series:
    code_from = transform_from.lower()
    code_to = transform_to.lower()
    assert code_from in valid_codings, f"transform_from must be one of {valid_codings}"
    assert code_to in valid_codings, f"transform_to must be one of {valid_codings}"

    #if dictionary index is not tabular field name
    if dict_df.index.name != 'tabular_field_name':
        dict_df = dict_df.reset_index().set_index('tabular_field_name')
    
    # converting and formatting data coding values 
    if isinstance(dict_df.loc[tab_field_name]["data_coding"], pd.Series):
        if dict_df.loc[tab_field_name]["data_coding"].nunique() == 1:
            code_string = convert_to_string(dict_df.loc[tab_field_name]["data_coding"].iloc[0])
        else:
            warnings.warn(f"data_coding has multiple values for tabular field {tab_field_name}, please check and update dictionary")
            return orig_answer
    else:
        code_string = convert_to_string(dict_df.loc[tab_field_name]["data_coding"])
    
    # Getting the data coding df from the large data coding csv
    code_df = mapping_df[mapping_df["code_number"] == code_string].copy()
    
    # Make sure no leading 0s for coding values
    code_df["coding"] =  code_df["coding"].apply(convert_to_string)
    cat_ordered = code_df\
        .astype({'coding': 'int'})\
        .sort_values('coding')[code_to]\
        .astype('str')\
        .drop_duplicates()
    
    mapping_dict = dict(zip(code_df[code_from].astype(str), code_df[code_to]))
    
  
    field_type =  dict_df.loc[tab_field_name]['field_type']
    if isinstance(field_type, pd.Series):
        if field_type.nunique() == 1:
            field_type = field_type.iloc[0]
        else:
            warnings.warn(f"tabular field {tab_field_name} is used in 2 columns and have conflicting field types,please check and update dictionary. This field has not be converted.")
            return orig_answer
    
    if field_type == 'Categorical (multiple)': 
        normalise_answer = normalize_answers(orig_answer, field_type)
        check_invalid_values(normalise_answer , code_df)
        transformed_answer = normalise_answer.apply(replace_values, mapping_dict = mapping_dict)
    else:
        normalized_answer = normalize_answers(orig_answer, field_type)
        check_invalid_values(normalized_answer, code_df)
        transformed_answer = normalized_answer.replace(mapping_dict)
        transformed_answer = pd.Categorical(transformed_answer)\
            .set_categories(cat_ordered, ordered=True)

    return transformed_answer

def convert_codings_to_int(df: pd.Series, dict_df: pd.DataFrame) -> pd.Series:
    tabular_field_name = df.name
    field_array = dict_df.loc[tabular_field_name, 'array']
    if isinstance(field_array, pd.Series):
        field_array = field_array.iloc[0]
    if field_array == 'Multiple':
        return df
    else: 
        dict_df.loc[tabular_field_name, 'pandas_dtype'] = 'Int16'
        return df.astype('Int16', errors='ignore')

def transform_dataframe(
    df: pd.DataFrame,
    transform_from: str,
    transform_to: str,
    dict_df: pd.DataFrame,
    mapping_df: pd.DataFrame,
) -> pd.DataFrame:
    # Validate input parameters
    if transform_from not in valid_codings or transform_to not in valid_codings:
        raise ValueError(f"transform_from and transform_to must be one of {valid_codings}")

    # Only fields with a code in data_coding property will be transformed
    fields_for_translation = dict_df[pd.notna(dict_df.data_coding)].index.intersection(df.columns)
    if len(fields_for_translation) == 0: # No fields with data_coding code
        return df

    transformed_df = df.copy()
    for column in fields_for_translation:
        data_coding = dict_df.loc[column, 'data_coding']
        # Handle the case where data_coding is a Series (multiple entries)
        if isinstance(data_coding, pd.Series):
            if data_coding.nunique() > 1:
                warnings.warn(f"Multiple different data_coding values found for column {column}. Using first value.")
            data_coding = data_coding.iloc[0]

        if pd.isna(data_coding):
            continue

        if transform_from != transform_to:
            transformed_df[column] = transform_answers(
                    column,
                    transformed_df[column],
                    transform_from,
                    transform_to,
                    dict_df,
                    mapping_df
                )
    
        if transform_to == 'coding':
            transformed_df[column] = convert_codings_to_int(
                transformed_df[column], 
                dict_df=dict_df
            )

    return transformed_df
