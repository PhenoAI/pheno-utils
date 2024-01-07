# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_config.ipynb.

# %% auto 0
__all__ = ['REF_COLOR', 'FEMALE_COLOR', 'MALE_COLOR', 'ALL_COLOR', 'GLUC_COLOR', 'FOOD_COLOR', 'DATASETS_PATH', 'COHORT',
           'EVENTS_DATASET', 'ERROR_ACTION', 'CONFIG_FILES', 'BULK_DATA_PATH', 'PREFERRED_LANGUAGE', 'config_found',
           'DICT_PROPERTY_PATH', 'DATA_CODING_PATH', 'copy_tre_config', 'get_dictionary_properties_file_path',
           'get_data_coding_file_path', 'generate_synthetic_data', 'generate_synthetic_data_like',
           'generate_categorical_synthetic_data']

# %% ../nbs/00_config.ipynb 3
import os
import json
import numpy as np
import pandas as pd
import shutil
from glob import glob

# %% ../nbs/00_config.ipynb 4
REF_COLOR = "k"
FEMALE_COLOR = "C1"
MALE_COLOR = "C0"
ALL_COLOR = "C5"

GLUC_COLOR = "C0"
FOOD_COLOR = "C1"

DATASETS_PATH = '/home/ec2-user/studies/hpp_datasets/'
COHORT = None
EVENTS_DATASET = 'events'
ERROR_ACTION = 'raise'
CONFIG_FILES = ['.pheno/config.json', '~/.pheno/config.json', '/efs/.pheno/config.json']
BULK_DATA_PATH = {}
PREFERRED_LANGUAGE = 'english'

config_found = False



# %% ../nbs/00_config.ipynb 5
def copy_tre_config():
    default_config_found = False
    script_path = os.path.dirname(os.path.abspath(__file__))
    
    env_config = os.path.join(script_path, 'config_setup', 'env_config.json')
    with open(env_config, 'r') as openfile:
        env_json = json.load(openfile)
    
    # where am I? 
    config_name = ''
    env = None
    for k, v in env_json.items():
        if os.path.exists(v['ident_path']):
            env = k
            config_name = v['config_name']
            break
        
    absolute_config_path = os.path.join(script_path, 'config_setup', config_name)
    
    if (env is not None) and (os.path.exists(absolute_config_path)):
        default_config_found = True
        if not os.path.exists(os.path.expanduser('~/.pheno')):
            os.makedirs(os.path.expanduser('~/.pheno'))
        
        shutil.copy2(absolute_config_path, os.path.expanduser('~/.pheno/config.json'))
    
    return default_config_found


# %% ../nbs/00_config.ipynb 6
for cf in CONFIG_FILES:
    cf = os.path.expanduser(cf)
    if not os.path.isfile(cf):
        continue
    
    config_found=True
    break


if not config_found: 
    if not copy_tre_config():
        raise ValueError(f'Missing Config file, please read the README file and run config_setup/create_default_config.py')
        
    
for cf in CONFIG_FILES:
    cf = os.path.expanduser(cf)
    if not os.path.isfile(cf):
        continue
    
    f = open(cf)
    config = json.load(f)
    
    if 'DATASETS_PATH' in config:
        DATASETS_PATH = config['DATASETS_PATH']
    if 'BULK_DATA_PATH' in config:
        BULK_DATA_PATH = config['BULK_DATA_PATH']
    if 'EVENTS_DATASET' in config:
        EVENTS_DATASET = config['EVENTS_DATASET']
    if 'PREFERRED_LANGUAGE' in config:
        PREFERRED_LANGUAGE = config['PREFERRED_LANGUAGE']
    if 'COHORT' in config:
        if config['COHORT'] == 0 or config['COHORT']=='None' or config['COHORT']==None :
            COHORT = None
    if 'ERROR_ACTION' in config:
        ERROR_ACTION = config['ERROR_ACTION']
    break


# %% ../nbs/00_config.ipynb 7
def get_dictionary_properties_file_path() -> str:
    """
    Get the file path for dictionary properties - TODO: move to config file or DB.
    At this point only includes field_type properties.

    Args:

    Returns:
        str: the path to the file
    """
    path = os.path.join(DATASETS_PATH, 'metadata', '2 - Dictionary properties - field_type.csv')
    if path.startswith('s3://'):
        return path
    return glob(path)[0]

# %% ../nbs/00_config.ipynb 8
def get_data_coding_file_path() -> str:
    """
    Get the file path for dictionary properties - TODO: move to config file or DB.
    At this point only includes field_type properties.

    Args:

    Returns:
        str: the path to the file
    """
    path = os.path.join(DATASETS_PATH, 'metadata', 'coding_mapping.parquet') 
    if path.startswith('s3://'):
        return path
    return glob(path)[0]

# %% ../nbs/00_config.ipynb 9
DICT_PROPERTY_PATH = get_dictionary_properties_file_path()
DATA_CODING_PATH = get_data_coding_file_path()

# %% ../nbs/00_config.ipynb 10
def generate_synthetic_data(n: int = 1000) -> pd.DataFrame:
    """
    Generates a sample DataFrame containing age, gender, and value data.

    Args:
        n: The number of rows in the generated DataFrame.

    Returns:
        A pandas DataFrame with columns 'age', 'gender', and 'val'.
    """
    pids = np.arange(n)
    # Set start and end dates
    start_date = pd.Timestamp('2020-01-01')
    end_date = pd.Timestamp('now')
    dates = pd.to_datetime(pd.to_datetime(np.random.uniform(start_date.value, end_date.value, n).astype(np.int64)).date)  
    ages = np.random.uniform(35, 73, size=n)
    genders = np.random.choice([0, 1], size=n)
    vals = np.random.normal(30 + 1 * ages + 40 * genders, 20, size=n)
    
    data = pd.DataFrame(data={"participant_id":pids,"date_of_research_stage": dates,"age_at_research_stage": ages, "sex": genders, "val1": vals}).set_index("participant_id")
    data["val2"] = data["val1"]*0.3 + 0.5*np.random.normal(0,50) + 0.2*10*data["sex"]
    return data

# %% ../nbs/00_config.ipynb 11
def generate_synthetic_data_like(df: pd.DataFrame, n: int = 1000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generate a sample DataFrame containing the same columns as `df`, but with random data.

    Args:
    
        df: The DataFrame whose columns should be used.
        n: The number of rows in the generated DataFrame.

    Returns:
        A pandas DataFrame with the same columns as `df`.
    """
    np.random.seed(random_seed)
    pids = np.arange(n)
    if n > len(df):
        replace = True
    else:
        replace = False

    null = df.reset_index().apply(lambda x: x.sample(frac=1).values)\
        .sample(n=n, replace=replace).assign(participant_id=pids)\
        .set_index(df.index.names)

    def is_path_string(x):
        return isinstance(x, str) and (x.count('/') > 1)

    # handle specific columns
    null.loc[:, null.map(is_path_string).mean() > 0.5] = '/path/to/file'
    if ('collection_timestamp' in null.columns) and ('collection_date' in null.columns):
        null['collection_date'] = null['collection_timestamp'].dt.date

    return null

# %% ../nbs/00_config.ipynb 12
def generate_categorical_synthetic_data(n: int = 1000) -> pd.DataFrame:
    """
    Generates a sample DataFrame containing age, gender, and categorical value data.

    Args:
        n: The number of rows in the generated DataFrame.

    Returns:
        A pandas DataFrame with columns 'age', 'gender', and 'val1'.
    """
    pids = np.arange(n)
    # Set start and end dates
    start_date = pd.Timestamp('2020-01-01')
    end_date = pd.Timestamp('now')
    dates = pd.to_datetime(pd.to_datetime(np.random.uniform(start_date.value, end_date.value, n).astype(np.int64)).date)
    ages = np.random.uniform(35, 73, size=n)
    genders = np.random.choice([0, 1], size=n)
    
    # Generate categorical values for 'val1'
    categories = ['A', 'B', 'C', 'D', 'E']
    val1 = np.random.choice(['A', 'B', 'C', 'D', 'E'], size=n)
    val2 = np.random.choice(['A', 'B', 'C'], size=n)
    
    data = pd.DataFrame(data={"participant_id":pids, "date_of_research_stage": dates, "age_at_research_stage": ages, "sex": genders, "val1": val1, "val2": val2}).set_index("participant_id")
    return data

