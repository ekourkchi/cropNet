import requests
import json
import pandas as pd
from pandas.io import sql
from pandas.io.json import json_normalize
import numpy as np
from sqlalchemy import types, create_engine
from datetime import date, timedelta
import Weather_db
import Hobo_db

####################################################################
engine = create_engine('mysql+mysqlconnector://'+
                       Weather_db.user+
                       ':'+Weather_db.passwd+
                       '@localhost/'+
                       Weather_db.database, 
                       echo=False)

####################################################################


from openpyxl.utils import get_column_letter

def autosize_excel_columns(worksheet, df):
    autosize_excel_columns_df(worksheet, df.index.to_frame())
    autosize_excel_columns_df(worksheet, df, offset=df.index.nlevels)

def autosize_excel_columns_df(worksheet, df, offset=0):
    for idx, col in enumerate(df):
        series = df[col]
        max_len = max((
          series.astype(str).map(len).max(),
          len(str(series.name))
        )) + 1

        colName = get_column_letter(idx+offset+1)  
        worksheet.column_dimensions[colName].width = max_len

####################################################################

today = date.today()
tomorrow = today + timedelta(days=1)

# string
today = today.isoformat()
tomorrow = tomorrow.isoformat()

####################################################################

def getData(station="PH1"):
    
    headers = {'Content-type': 'application/json',
               'Authorization': Hobo_db.campbell_token
              }


    url = Hobo_db.campbell_url+station+'/2016-01-01T00:00:00Z/'+tomorrow+'T00:00:00Z?fields=ETo%2C%20PrecipDay%2C%20SolarRadDay%2C%20RH%2C%20Temp'
    #latest?stations=PH1&timezone=US%2FHawaii'

    r = requests.get(url, headers=headers)  # data=json.dumps(query)
    data = json.loads(r.text)
    df = pd.json_normalize(data)

    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index("timestamp")

    df = df.drop(columns=["interval"])
    df = df.resample('1D').mean()

    df1 = df.interpolate(method='linear', limit=3, limit_direction='forward')
    df = df.rename(columns={"values.ETo": "ETo.raw", "values.PrecipDay": "Rainfall.raw"})
    df = df.rename(columns={"values.RH": "RH.raw", "values.SolarRadDay": "SolarRad.raw"})
    df = df.rename(columns={"values.Temp": "Temp.raw"})
    df["ETo.filled"] = df1["values.ETo"]
    df["Rainfall.filled"] = df1["values.PrecipDay"]
    df["RH.filled"] = df1["values.RH"]
    df["SolarRadDay.filled"] = df1["values.SolarRadDay"]
    df["Temp.filled"] = df1["values.Temp"]

    df = df.reset_index()   
    df["timestamp"] = df["timestamp"].dt.tz_convert("US/Hawaii").dt.date
    df = df.rename(columns={"timestamp":"Date"})
    
    return df

####################################################################
outFILE = 'HOBO_CAMPBELL_ET0_Rain.xlsx'
####################################################################

station = "PH1"
with pd.ExcelWriter(outFILE, engine='openpyxl', mode='a') as writer:
    
    df = getData(station=station)
    df.to_sql(name=station+"_ETdata", con=engine, if_exists='replace', index=True, chunksize=1000)
    
    sheet_name = 'PIONEER Gay'
    
    df.to_excel(writer, sheet_name = sheet_name)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    autosize_excel_columns(worksheet, df)
    writer.save()


station = "PH2"
with pd.ExcelWriter(outFILE, engine='openpyxl', mode='a') as writer:
    
    df = getData(station=station)
    df.to_sql(name=station+"_ETdata", con=engine, if_exists='replace', index=True, chunksize=1000)
    
    sheet_name = 'PIONEER Helemano'

    df.to_excel(writer, sheet_name = sheet_name)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    autosize_excel_columns(worksheet, df)
    writer.save()
