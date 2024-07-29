### tranformation code

import numpy as np
import pandas as pd

cols = ['break_date', 'grp_LIVE7', 'type_break', 'break_hour', 'break_min',
       'year', 'month', 'day', 'dow', 'woy', 'code_break_freq_encode',
       'class_break_bb', 'class_break_inner', 'class_break_normal',
       'class_break_trailer', 'name_target_12-34', 'name_target_15+',
       'name_target_15+ GS 1-4', 'name_target_15-24', 'name_target_15-34',
       'name_target_15-44', 'name_target_15-54', 'name_target_18-24',
       'name_target_18-34', 'name_target_18-44', 'name_target_18-54',
       'name_target_18-54 GS 1-4', 'name_target_18-64', 'name_target_25-44',
       'name_target_25-54', 'name_target_25-54 GS 1-6',
       'name_target_25-54 GS1-4', 'name_target_35+', 'name_target_35-54',
       'name_target_35-54 GS 1-4', 'name_target_4+', 'name_target_4-14',
       'name_target_55+', 'name_target_FEM 15+', 'name_target_FEM 18-34',
       'name_target_FEM 18-44', 'name_target_FEM 18-54',
       'name_target_FEM 18-54 GS 1-4', 'name_target_FEM 25-44',
       'name_target_FEM 25-54', 'name_target_HOM 15+', 'name_target_HOM 18-34',
       'name_target_HOM 18-44', 'name_target_HOM 18-54',
       'name_target_HOM 18-54 GS 1-4', 'name_target_PRA 18-34',
       'name_target_PRA 18-44', 'name_target_PRA 18-54',
       'name_target_PRA 18-54 GS 1-4', 'name_target_PRA 18-64',
       'name_target_PRA 25-54', 'name_target_PRA 25-64',
       'name_target_PRA AVEC ENFANT']

# check missing columns from new raw-data compared with baseline dataframe
def add_missing_columns(df, columns_list, default_value=0):
    """
    Adds missing columns in latest data with default value of 0 compared when the model was initially trained.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns_list (list): List of column names to compare with DataFrame columns.
        default_value (int or float, optional): Default value for the missing columns. Defaults to 0.

    Returns:
        pd.DataFrame: DataFrame with missing columns added.
    """
    missing_columns = set(columns_list) - set(df.columns)
    for col in missing_columns:
        df[col] = default_value
    return df

# transformation process of the raw-data
def transform_dataframe(df):
    # adjust format 
    df['break_date'] = pd.to_datetime(df['break_date'], format='%Y%m%d')
    df['class_break'] = df['class_break'].astype('category')
    df['name_target'] = df['name_target'].astype('category')
    df['type_break'] = df['type_break'].astype('category')
    df['program_after_type1'] = df['program_after_type1'].astype('category')
    df['program_before_type1'] = df['program_before_type1'].astype('category')

    # extract date features
    df['year'] = df['break_date'].dt.year
    df['month'] = df['break_date'].dt.month
    df['day'] = df['break_date'].dt.day
    df['dow'] = df['break_date'].dt.dayofweek
    df['woy'] = df['break_date'].dt.isocalendar().week
    df['woy'] = df['woy'].astype('int32')

    # extract hour, minute and second
    df[['break_hour', 'break_min', 'break_sec']] = df['beginbreak_theoretical'].str.split(':', expand=True)
    df['break_hour'] = df['break_hour'].astype('int64')
    df['break_min'] = df['break_min'].astype('int64')
    df['break_sec'] = df['break_sec'].astype('int64')
    df.drop(['beginbreak_theoretical', 'break_sec'], axis=1, inplace=True)

    # fill grp = 0 with random values from 0.01 to 0.02 
    # use only to re-train model
    # df['grp_LIVE7'] = df['grp_LIVE7'].replace(0, np.random.uniform(0.01, 0.02))

    # sort values by date, hour, minute
    df = df.sort_values(by=['break_date', 'break_hour', 'break_min'], ignore_index=True)

    # encode 'type_break' by one-hot
    df['type_break'] = [1 if x == 'Prime' else 0 for x in df['type_break']]

    # encode 'code_break' by frequency
    fqcb = df.groupby('code_break').size() / len(df)
    df['code_break_freq_encode'] = df['code_break'].map(fqcb)
    df['code_break_freq_encode'] = df['code_break_freq_encode'].astype('float64')
    df.drop(['code_break'], axis=1, inplace=True)  # drop original column

    # encode 'class_break' and 'name_target'
    df_ml = pd.get_dummies(df, columns=['class_break', 'name_target'], dtype=bool)
    df_ml.drop(columns=['program_before_type1', 'program_after_type1'], axis=1, inplace=True)

    # adding missing columns
    df_ml = add_missing_columns(df=df_ml, columns_list=cols)

    return df_ml

if __name__ == "__main__":

    # import raw data REPLACE WITH CORRECT SOURCE
    data = spark.read.format('csv').option('delimiter', ';').option('header', True).load('/mnt/prd/governed/Forecasting/SynapseExtract/predict').filter(data.name_medium == 'UNE').filter("grp_LIVE7 is null")
    cols = ['break_date', 'beginbreak_theoretical', 'code_break', 'type_break', 'class_break', 'name_target', 'program_before_type1', 'program_after_type1']
    df = data.select(*cols).toPandas()
    df['break_date'] = pd.to_datetime(df['break_date'], format='%Y%m%d')
    df = df.query(" '2024-08-01' <= break_date <= '2024-08-31' ") ### REPLACE DATE INTERVAL WITH ENVIRONMENT VARIABLES

    # transform raw-data into dataframe
    df_ml = transform_dataframe(df)

    # add missing columns if needed
    df_ml = add_missing_columns(df=df_ml, columns_list=cols, default_value=0)

    # save the file as csv NEED TO CHANGE
    df_ml.to_csv('une_df_ml.csv')

    # save the raw file to attach preditions
    df.to_csv('une_to_attach_pred.csv')