# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/13_questionnaire_handler.ipynb.

# %% auto 0
__all__ = ['convert_to_string', 'normalize_answers', 'check_invalid_values', 'flatten_series', 'check_values', 'replace_values',
           'transform_answers', 'transform_dataframe']

# %% ../nbs/13_questionnaire_handler.ipynb 3
import pandas as pd
import numpy as np
import warnings

# %% ../nbs/13_questionnaire_handler.ipynb 5
def convert_to_string(x):
    return str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)

def normalize_answers(orig_answer: pd.Series) -> pd.Series:
    """
    Normalize the answers from string.

    Args:
        orig_answer (pd.Series): The original answer series.

    Returns:
        pd.Series: The normalized answer series.
    """
    # Convert the entire series to strings, np.nan will become 'nan'
    normalized_answer = orig_answer.astype(str)

    # Replace float-like strings with integer-like strings, ignoring 'nan'
    normalized_answer = normalized_answer.str.replace(r"\.0$", "", regex=True)
    normalized_answer = normalized_answer.replace("nan", np.nan)
    normalized_answer = normalized_answer.replace("<NA>", np.nan)
    #check

    return normalized_answer

def check_invalid_values(code_df, code_from, normalized_answer):
    """
    Check if values in normalized_answer exist in code_df[code_from], excluding np.nan.

    Args:
        code_df (pd.DataFrame): The DataFrame containing the code mappings.
        code_from (str): The column name to check in code_df.
        normalized_answer (pd.Series): The normalized answer series.

    Returns:
        None: Prints the invalid values found, if any.
    """
    # Check if values in normalized_answer exist in code_df[code_from], excluding np.nan
    valid_values = set(code_df[code_from].astype(str))
    answer_values = set(normalized_answer.dropna())
    invalid_values = answer_values - valid_values

    if invalid_values:
        warnings.warn(f"Invalid values found: {invalid_values}")

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

def check_values(series: pd.Series, mapping_dict: dict) -> None:
    """
    Check if all values in a Series have corresponding mappings in a dictionary.
    Raise a warning if any value in the Series doesn't have a mapping.

    Parameters:
    series (pd.Series): A Pandas Series to check.
    mapping_dict (dict): A dictionary where the keys represent the values to be
                         checked against the Series.

    Returns:
    None: This function does not return anything. It raises warnings if any
          mismatch is found between the Series values and dictionary keys.
    """
    unique_values = set(flatten_series(series))
    missing_values = unique_values - set(mapping_dict.keys())
    if missing_values:
        warnings.warn(f"Warning: Missing mappings for values {missing_values} for tabular field {series.name}")


def replace_values(row: pd.Series, mapping_dict: dict) -> [pd.Series, list, float]:
    """
    Replace values in a row with corresponding values from a mapping dictionary used for categpoical multiple questions
    
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
    if isinstance(row, list) or isinstance(row, np.ndarray):
        row = list(row) if isinstance(row, np.ndarray) else row
        return [mapping_dict.get(item, item) for item in row]
    elif pd.isna(row):
        return np.nan
    else:
        return mapping_dict.get(row, row)

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
    assert code_from in ["hebrew", "english", "coding"], "transform_from must be one of 'hebrew', 'english', 'coding'"
    assert code_to in ["hebrew", "english", "coding"], "transform_to must be one of 'hebrew', 'english', 'coding'"

    #if dictionary index is not tabular field name
    if dict_df.index.name != 'tabular_field_name':
        dict_df = dict_df.reset_index().set_index('tabular_field_name')
    
    # converting and formatting data coding values 
    if isinstance(dict_df.loc[tab_field_name]["data_coding"], pd.Series):
        code_string = convert_to_string(dict_df.loc[tab_field_name]["data_coding"].iloc[0])
    else:
        code_string = convert_to_string(dict_df.loc[tab_field_name]["data_coding"])
    
    #getting the data coding df from the large data coding csv
    code_df = mapping_df[mapping_df["code_number"] == code_string].copy()
    #Make sure no leading 0s for coding values
    code_df["coding"] = code_df["coding"].astype(int).astype(str)
    coding = dict(zip(code_df[code_from].astype(str), code_df[code_to]))
    
    
    field_type =  dict_df.loc[tab_field_name]['field_type']
    #if tab field is in 2 features sets it will be a series so just check the first case
    if isinstance(field_type, pd.Series) and field_type.iloc[0].strip() == 'Categorical (multiple)' or isinstance(field_type, str) and field_type.strip() == 'Categorical (multiple)':
          # Convert dictionary keys to integers
        mapping_dict = {int(k): v for k, v in coding.items()}
        check_values( orig_answer , mapping_dict)
        transformed_answer = orig_answer.apply(replace_values, mapping_dict = mapping_dict)
    else:
        #if categorical single
        normalized_answer = normalize_answers(orig_answer)
        check_invalid_values(code_df, code_from, normalized_answer)
        transformed_answer = normalized_answer.replace(coding)
        transformed_answer = transformed_answer.astype("category")

    return transformed_answer

   



def transform_dataframe(
    df: pd.DataFrame,
    transform_from: str,
    transform_to: str,
    dict_df: pd.DataFrame,
    mapping_df: pd.DataFrame,
) -> pd.DataFrame:
    if 'data_coding' not in dict_df.columns or transform_from == transform_to:
        return df
    
    fields_for_translation = dict_df[pd.notna(dict_df.data_coding)].index.intersection(df.columns)
    if len(fields_for_translation) == 0:
        return df
    transformed_df = df.copy()
    for column in fields_for_translation:
        print(column)
        try: 
            data_coding = dict_df.loc[column, 'data_coding']
        except Exception as e:
            warnings.warn(f'Could not find data_coding for column {column}')
            continue
        # Handle the case where data_coding is a Series (multiple entries)
        if isinstance(data_coding, pd.Series):
            # Proceed only if all data_codings are consistent
            if data_coding.nunique() == 1 and pd.notna(data_coding.iloc[0]):
                transformed_df[column] = transform_answers(
                    column,
                    transformed_df[column],
                    transform_from,
                    transform_to,
                    dict_df,
                    mapping_df
                )
        else:  # Single value for data_coding
            if pd.notna(data_coding):
                transformed_df[column] = transform_answers(
                    column,
                    transformed_df[column],
                    transform_from,
                    transform_to,
                    dict_df,
                    mapping_df
                )
    return transformed_df
