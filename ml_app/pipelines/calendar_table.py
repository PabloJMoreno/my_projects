# calendar table

# import libraries
import numpy as np
import pandas as pd
from datetime import datetime

# create function to generate calendar table

def create_calendar_table():
    # set variables for date range
    today = datetime.now()
    start_date = pd.Timestamp(today.year - 10, 1, 1)
    date_series = pd.date_range(start_date, today)
    
    # yty table
    df_yty = pd.DataFrame({'dates': date_series})
    df_yty['dateType'] = "YTY"
    df_yty['yearType'] = df_yty['dates'].dt.year - today.year
    df_yty['uploadType'] = "Monthly"
    df_yty['DimDateId'] = df_yty['dates'].dt.strftime('%Y%m%d')
    df_yty['Use Case'] = "Pige"
    df_yty['Year'] = df_yty['dates'].dt.year
    df_yty['Sort'] = df_yty['dates'].dt.month
    df_yty['month id'] = df_yty['dates'].dt.month
    df_yty['month name'] = df_yty['dates'].dt.strftime('%B')
    df_yty['IsoWeek'] = 'W' + df_yty['dates'].dt.isocalendar().week.astype(str).str.zfill(2)
    
    # ytd_w table
    df_ytd_w = pd.DataFrame({'dates': date_series})
    df_ytd_w['dateType'] = "YTD"
    df_ytd_w['yearType'] = df_ytd_w['dates'].dt.year - today.year
    df_ytd_w['uploadType'] = "Weekly"
    df_ytd_w['DimDateId'] = df_ytd_w['dates'].dt.strftime('%Y%m%d')
    df_ytd_w['Use Case'] = "Pige"
    df_ytd_w['Year'] = df_ytd_w['dates'].dt.year
    df_ytd_w['Sort'] = df_ytd_w['dates'].dt.month
    df_ytd_w['month id'] = df_ytd_w['dates'].dt.month
    df_ytd_w['month name'] = df_ytd_w['dates'].dt.strftime('%B')
    df_ytd_w['IsoWeek'] = 'W' + df_ytd_w['dates'].dt.isocalendar().week.astype(str).str.zfill(2)
    
    # ytd_m table
    df_ytd_m = pd.DataFrame({'dates': date_series})
    df_ytd_m['dateType'] = "YTD"
    df_ytd_m['yearType'] = df_ytd_m['dates'].dt.year - today.year
    df_ytd_m['uploadType'] = "Monthly"
    df_ytd_m['DimDateId'] = df_ytd_m['dates'].dt.strftime('%Y%m%d')
    df_ytd_m['Use Case'] = "Pige"
    df_ytd_m['Year'] = df_ytd_m['dates'].dt.year
    df_ytd_m['Sort'] = df_ytd_m['dates'].dt.month
    df_ytd_m['month id'] = df_ytd_m['dates'].dt.month
    df_ytd_m['month name'] = df_ytd_m['dates'].dt.strftime('%B')
    df_ytd_m['IsoWeek'] = 'W' + df_ytd_m['dates'].dt.isocalendar().week.astype(str).str.zfill(2)
    
    # my table
    df_my = pd.DataFrame({'dates': date_series})
    df_my['dateType'] = "YTD"
    df_my['yearType'] = df_my['dates'].dt.year - today.year
    df_my['uploadType'] = "Monthly"
    df_my['DimDateId'] = df_my['dates'].dt.strftime('%Y%m%d')
    df_my['Use Case'] = "Pige"
    df_my['Year'] = (df_my['dates'].dt.year % 100 - 1).astype(str) + '-' +  (df_my['dates'].dt.year % 100).astype(str)
    df_my['Sort'] = df_my['dates'].dt.month
    df_my['month id'] = df_my['dates'].dt.month
    df_my['month name'] = df_my['dates'].dt.strftime('%B')
    df_my['IsoWeek'] = 'W' + df_my['dates'].dt.isocalendar().week.astype(str).str.zfill(2)
    
    # concatenation of tables
    df = pd.concat([df_yty, df_ytd_w, df_ytd_m], ignore_index=True)
    
    return df

if __name__ == "__main__":
    
    # create table
    calendar_table = create_calendar_table()

    # save table as csv
    calendar_table.to_csv('calendar_table.csv', index=False)