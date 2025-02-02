import numpy as np
import pandas as pd
from pycaret.regression import load_model, predict_model

# import dataframe for predictions

df_ml = pd.read_csv('une_transformed_for_predictions.csv')
raw = pd.read_csv('une_to_attach_pred.csv')

# import preditive model

model = load_model('model_name_pipeline')

def transform_raw(df):

    # fix date fromat and query on specific time-frame
    df['break_date'] = pd.to_datetime(df['break_date'], format='%Y%m%d')
    # df_raw = df.query(" '2024-07-01' <= break_date <= '2024-07-31' ")

    # split 'break_hour' to later sort df by date, hour and minute
    df[['break_hour', 'break_min', 'break_sec']] = df['beginbreak_theoretical'].str.split(':', expand=True)
    df['break_hour'] = df['break_hour'].astype('int64')
    df['break_min'] = df['break_min'].astype('int64')

    # sort dataframe by date and hour
    df = df.sort_values(by=['break_date', 'break_hour', 'break_min'], ignore_index=True)

    # drop unnecesary columns
    df.drop(columns=['break_hour', 'break_min', 'break_sec'], axis=1, inplace=True)
    return df


def prediction(model, df_raw, df_pred):
    """
    This function generates the grp prediction taking transformed dataframe
    
    Args:
        model (.pkl file): transformation and model to perform predictions
        df_raw (pd.DataFrame): The input DataFrame to attached the predicitons
        df_pred (pd.DataFrame): The transformed dataframe suitable for the model

    Returns:
        pd.DataFrame: DataFrame with grp predictions
    """
    pred_df = predict_model(estimator=model, df=df_pred) # generate prediction dataframe
    df_raw['grp_prediction'] = pred_df['prediction_label'] # attach prediction to raw future data
    return df_raw

if __name__ == "__main__":
    
    # format raw data 
    df_raw = transform_raw(df=raw)
    
    # generate prediction and save it in new dataframe
    pred_df = prediction(model=model, df_raw=df_raw, df_pred=df_ml)

    # save resulting dataframe with predictions as csv NEED TO CHANGE
    pred_df.to_csv('une_grp_prediction.csv', index=False) 