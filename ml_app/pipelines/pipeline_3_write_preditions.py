import numpy as np
import pandas as pd
import sqlite3

# set up sql connection
database_name = 'database.db'
conn = sqlite3.connect(database_name)

# import dataframe with predictions
df_pred = pd.read_csv('une_grp_prediction.csv')

# generate function 

def write_predictions(conn, df)
    df.to_sql("grp_prediction_period", conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    return print("The table ", df, " has been succesfully written to the database.")

def check_table_exists(database, table_name):
    try:
        conn = conn
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except sqlite3.Error as e:
        print(f"Error checking table existence: {e}")
        return False

if __name__ == "__main__":
    
    # generate prediction and save it in new dataframe
    write_predictions(conn=conn, df=df_pred)

    # save resulting dataframe with predictions as csv NEED TO CHANGE
    pred_df.to_csv('une_grp_prediction.csv', index=False) 

    # check if table was successfuly written
    if check_table_exists(database=database_name, table_name="grp_prediction_period"): 
        print(f"The table '{table_name}' exists in the database.")
    else: 
        print(f"The table '{table_name}' does not exist in the database.")