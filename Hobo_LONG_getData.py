import matplotlib.pyplot as plt
import requests
import json
import pandas as pd
from pandas.io import sql
from pandas.io.json import json_normalize
import numpy as np
from sqlalchemy import types, create_engine
from datetime import date, timedelta
from datetime import datetime
import time
import re
import Weather_db
import Hobo_db

####################################################################

engine = create_engine('mysql+mysqlconnector://'+
                       Weather_db.user+
                       ':'+Weather_db.passwd+
                       '@localhost/'+
                       Weather_db.database, 
                       echo=False)

url    = Hobo_db.url
user   = Hobo_db.user
passwd = Hobo_db.passwd
token  = Hobo_db.token

####################################################################

def getData(HOBOquery):
    
    query  = {
              "authentication":
                  {
                      "password": passwd,
                      "token":token,
                      "user":user
                  },
              "query": HOBOquery
             }

    headers = {'Content-type': 'application/json'}

    url = "https://webservice.hobolink.com/restv2/data/custom/file"

    t1 =  datetime.now()
    
    print("Downloading data from HOBOlink Query: "+HOBOquery)
    print(f"Start time: {t1}")
    ###########################################
    results = requests.post(url, data=json.dumps(query), headers=headers)
    ###########################################
    t2 =  datetime.now()
    print(f'Execution time ({HOBOquery}): {t2-t1}')
    
    fileName = HOBOquery.replace('-', '_')+".xlsx"
    
    R = results.text
    if not "Time-out" in R:
        output = open(fileName, 'wb')
        output.write(results.content)
        output.close()   
    else:
        print("Query Time-out, trying again ...")
        getData(HOBOquery)
            
    return fileName
####################################################################

def meta_data(x):
    
    comment = x.colname
    return parser(comment)

def parser(comment):

    S1 = comment.split(',')
    S2 = S1[0].split('(')
    quantity = S2[0].strip()
    S21 = S2[1].split(' ')
    code = S21[0].strip()
    
    content_size_pattern = r'\(.*\)'
    item = re.search(content_size_pattern, comment).group(0)
    content_size_pattern = r'\(.*\s'
    code = re.search(content_size_pattern, item).group(0).strip('(').strip()
    
    content_size_pattern = r'\s\S*:.*\)'
    item = re.search(content_size_pattern, comment).group(0).strip(')')
    S3 = item.split(":")

    logger_sn = S3[0].strip()
    sensor_sn = S3[1].strip()
    us_unit = S1[1].strip()
    comment = S1[2].strip()

    return pd.Series([
        quantity,
        code,
        logger_sn,
        sensor_sn,
        us_unit,
        comment
        ])

####################################################################

def frame2column(df):
    
    df1 = df.drop(columns="Line#")
    df1 = df1.rename(columns={"Date":"timestamp"})
#     df1['timestamp'] = pd.to_datetime(df1.timestamp)
    df1 = df1.set_index('timestamp')

    n_col = len(df1.columns)

    df_list = []
    for m in range(n_col):

        df2 = df1[df1.columns[m:m+1]].dropna()
        df2['us_value'] = df2.loc[:,:]
        df2['colname'] = df2.columns[0]

        if len(df2)>0:

            df2[['quantity','code','logger_sn','sensor_sn','us_unit','comment']] = df2.apply(meta_data, axis=1)
            df2 = df2.drop(columns="colname")
            df2 = df2.iloc[:,1:]
            df_list.append(df2)


    dfALL = pd.concat(df_list)

    return dfALL

####################################################################


# HOBOlist = ["ESN-2018B2-CSV"]
# HOBOlist = ["ESN-10906989"]

#HOBOlist = []
#HOBOlist += ["ESN-2020A-CSV", "ESN-2020B-CSV", "ESN-2020C-CSV"]
#HOBOlist += ["ESN-2019A-CSV", "ESN-2019B-CSV"]
#HOBOlist += ["ESN-2018A-CSV"]
#HOBOlist += ["ESN-2018B1-CSV", "ESN-2018B2-CSV"]
#HOBOlist += ["ESN-2017A-CSV", "ESN-2017B-CSV"]
#HOBOlist += ["ESN-2016A-CSV", "ESN-2016B-CSV"]

#HOBOlist = ["ESN-2020C-CSV"]
#HOBOlist = ["ESN-2021A-XLS", "ESN-2021B-XLS"]

# HOBOlist = ["ESN-2021B-XLS"]

HOBOlist = ["ESN-2021C-XLS", "ESN-2021D-XLS"]


for HOBOquery in HOBOlist:
  try:
    fileName = getData(HOBOquery)
    print("Data stored locally in: "+fileName)
    
    fileName = HOBOquery.replace('-', '_')+".xlsx"
    df = pd.read_excel(fileName)
    
    print("Transforming data to load into the MySQL databse ...")
    
    dfALL = frame2column(df)
    tableName = fileName.split('.')[0].replace('ESN', 'HOBO')
    
    print("Inserting data into the SQL table: "+tableName+" ...")

    dfALL.index = pd.to_datetime(dfALL.index)
    df2SQL = dfALL
    df2SQL.to_sql(name=tableName, con=engine, if_exists='replace', index=True, chunksize=1000)        
  except:
    pass

####################################################################

engine.dispose()


