import sys
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

from forecast_ET import *

##################################################
engine = create_engine('mysql+mysqlconnector://' +
                       Weather_db.user +
                       ':' + Weather_db.passwd +
                       '@localhost/' +
                       Weather_db.database,
                       echo=False)
##################################################

intstr = sys.argv[1]
serial = sys.argv[2]

if intstr == 'integer':
    serial = int(serial)
else:
    serial = str(serial)

file = './HOBO_CAMPBELL_ET0_Rain.xlsx'

outTable = {}
outTable["serial"] = str(serial)
outTable["latest_date"] = None
outTable["day1_date"] = None
outTable["ETo_1"] = None
outTable["ETo_av3"] = None
outTable["ETo_1_MAE"] = None
outTable["ETo_1_R2"] = None
outTable["day3_date"] = None
outTable["ETo_3"] = None
outTable["ETo_3_MAE"] = None
outTable["ETo_3_R2"] = None
outTable["day5_date"] = None
outTable["ETo_5"] = None
outTable["ETo_5_MAE"] = None
outTable["ETo_5_R2"] = None
outTable["Rain_1"] = None
outTable["Rain_av3"] = None
outTable["Rain_1_MAE"] = None
outTable["Rain_1_R2"] = None

try:
    latest_date, day1_date, ETo_1, ETo_av3, ETo_1_MAE, ETo_1_R2 = forecast(
        file, serial, mode='ETo', mDelay=3, nAhead=1, n_particles=20, iters=20)
    outTable["latest_date"] = latest_date
    outTable["day1_date"] = day1_date
    outTable["ETo_1"] = ETo_1
    outTable["ETo_av3"] = ETo_av3
    outTable["ETo_1_MAE"] = ETo_1_MAE
    outTable["ETo_1_R2"] = ETo_1_R2
except BaseException:
    pass
try:
    _, day3_date, ETo_3, _, ETo_3_MAE, ETo_3_R2 = forecast(
        file, serial, mode='ETo', mDelay=5, nAhead=3, n_particles=20, iters=20)
    outTable["day3_date"] = day3_date
    outTable["ETo_3"] = ETo_3
    outTable["ETo_3_MAE"] = ETo_3_MAE
    outTable["ETo_3_R2"] = ETo_3_R2
except BaseException:
    pass
try:
    _, day5_date, ETo_5, _, ETo_5_MAE, ETo_5_R2 = forecast(
        file, serial, mode='ETo', mDelay=5, nAhead=5, n_particles=20, iters=20)
    outTable["day5_date"] = day5_date
    outTable["ETo_5"] = ETo_5
    outTable["ETo_5_MAE"] = ETo_5_MAE
    outTable["ETo_5_R2"] = ETo_5_R2
except BaseException:
    pass


try:
    _, day1_rain_date, Rain_1, Rain_av3, Rain_1_MAE, Rain_1_R2 = forecast(
        file, serial, mode='Rain', mDelay=3, nAhead=1, n_particles=20, iters=20)
    outTable["Rain_1"] = Rain_1
    outTable["Rain_av3"] = Rain_av3
    outTable["Rain_1_MAE"] = Rain_1_MAE
    outTable["Rain_1_R2"] = Rain_1_R2
    if outTable["day1_date"] is None:
        outTable["day1_date"] = day1_rain_date
except BaseException:
    pass


if outTable["latest_date"] is None:
    station = stationInfo[serial]["name"]
    data = pd.read_excel(file, sheet_name=station)
    date = 'Date(' + stationInfo[serial]["timeZone"] + ')'
    if serial == 'PH1' or serial == 'PH2':
        date = 'Date'
    # revising the column names
    for col in data.columns:
        newcol = col.split("(")[0].strip()
        data.rename(columns={col: newcol}, inplace=True)
    data.set_index("Date", inplace=True)
    latest_date = data.index[-1].strftime("%Y-%m-%d")
    outTable["latest_date"] = latest_date


now = datetime.now()
dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
outTable["last_update"] = dt_string + ' HST'

for key in outTable:
    value = outTable[key]
    outTable[key] = [value]

df = pd.DataFrame.from_dict(outTable)
df.latest_date = pd.to_datetime(df.latest_date)
df.to_sql(name='Forecasts', con=engine, if_exists='append', chunksize=1000)

engine.dispose()
