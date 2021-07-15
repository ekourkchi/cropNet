from openpyxl.utils import get_column_letter
import sys
import os
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
import pylab as py
from matplotlib import gridspec
import matplotlib.dates as md

import Weather_db
import Hobo_db

import warnings
warnings.filterwarnings('ignore')

####################################################
#################################


def xcmd(cmd, verbose=True):

    if verbose:
        print('\n'+cmd)

    tmp = os.popen(cmd)
    output = ''
    for x in tmp:
        output += x
    if 'abort' in output:
        failure = True
    else:
        failure = tmp.close()
    if False:
        print('execution of %s failed' % cmd)
        print('error is as follows', output)
        sys.exit()
    else:
        return output

######################################
####################################################


engine = create_engine('mysql+mysqlconnector://' +
                       Weather_db.user +
                       ':'+Weather_db.passwd +
                       '@localhost/' +
                       Weather_db.database,
                       echo=False)

url = Hobo_db.url
user = Hobo_db.user
passwd = Hobo_db.passwd
token = Hobo_db.token

####################################################

stationInfo = {
    10906989: {"timeZone": "US/Hawaii", "name": "ALOUN_HELEMANO", "GPS": "21 32 8.9 N 158 02 05.0 W"},
    20173022: {"timeZone": "US/Hawaii", "name": "HIRAKO", "GPS": "20 00 14.6 N 155 41 29.3 W"},
    20009161: {"timeZone": "US/Hawaii", "name": "KULA_AG_PARK", "GPS": "20 47 43.2 N 156 21 35.6 W"},
    20121046: {"timeZone": "Pacific/Guam", "name": "MALOJLOJ MEDA", "GPS": "13 20 21.0 N 144 45 49.0 E"},
    20006321: {"timeZone": "US/Hawaii", "name": "MAO", "GPS": "21 27 4.9 N 158 09 25.8 W"},
    20173020: {"timeZone": "US/Hawaii", "name": "PIONEER CORN", "GPS": "21 33 41.5 N 158 07 40.3 W"},
    20173019: {"timeZone": "US/Hawaii", "name": "SEIZEN", "GPS": "20 01 26.2 N 155 39 00.5 W"},
    20824841: {"timeZone": "Pacific/Guam", "name": "WATSON", "GPS": ""},
    20824842: {"timeZone": "Pacific/Guam", "name": "WUSSTIG", "GPS": ""},
    20121045: {"timeZone": "Pacific/Guam", "name": "YIGO", "GPS": "13 33 54.3 N 144 52 38.4 E"},
    20121047: {"timeZone": "Pacific/Samoa", "name": "MALAEIMI ", "GPS": ""},
    20121048: {"timeZone": "Pacific/Samoa", "name": "TAFETA", "GPS": ""},
    20173018: {"timeZone": "US/Hawaii", "name": "TEXEIRA", "GPS": ""},
}

Sinfo_df = pd.DataFrame.from_dict(stationInfo).T.reset_index().rename(columns={"index":"serial"})
Sinfo_df.to_sql(name="stationInfo", con=engine, if_exists='replace', index=False, chunksize=1000)        
####################################################

sqlTables = pd.read_sql_query("show tables", engine)

ESNtables = sqlTables.iloc[:, 0].str.split('_').apply(lambda x: x[0]) == "HOBO"
sqlTables = sqlTables[ESNtables]

sqlTables = [x[0] for x in sqlTables.values.tolist()]

####################################################


def mapET(ET):

    if ET > 0:
        return ET
    elif ET <= 0:
        return 0
    else:
        return np.nan


def getETxlsx(engine, logger_sn, fill=True):

    df = pd.read_sql_query(
        "select * from "+sqlTables[0]+' where logger_sn = '+logger_sn, engine)

    #print("select * from "+sqlTables[0]+' where logger_sn = '+logger_sn)

    for table in sqlTables[1:]:

        df_tmp = pd.read_sql_query(
            "select * from "+table+' where logger_sn = '+logger_sn, engine)
        df = pd.concat([df, df_tmp]).drop_duplicates(keep='first')

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df.timestamp.dt.tz_localize(
        'utc').dt.tz_convert(stationInfo[serial]["timeZone"])
    df = df.set_index("timestamp")

    paramNames = ["Temperature",
                  "Dew Point",
                  "Gust Speed",
                  "RH",
                  "Rain",
                  "Solar Radiation",
                  "Wind Speed"
                  ]

    df1 = df

    for i, pName in enumerate(paramNames):
        #     print(pName)
        df2 = df1[df1["quantity"] == pName]
        df2 = df2.rename(columns={"us_value": pName})
        if True:  # try:
            df2[pName] = df2[pName].astype(str)
            df2[pName] = df2[pName].apply(lambda x: x.replace(',', ''))
            df2[pName] = df2[pName].astype(np.float32)
#            df2[pName] = df2[pName].apply(lambda x: x.astype('float'))
#        except:
#            pass
        df2 = df2.rename(columns={"us_unit": pName+'_unit'})
        df2 = df2[[pName, pName+'_unit']]

        # print(pName)
        # print(df2.head())

        if i == 0:
            df_out = df2
        else:
            df_out = df_out.join(df2, lsuffix='_l', rsuffix='_r', how='outer')

    df_out["Temperature_unit"] = r'$^oF$'
    df_out["Dew Point_unit"] = r'$^oF$'
    df_out["Solar Radiation_unit"] = r'$W/m^2$'
    df_out["Rain_unit"] = r'$Inch$'
    df_out["RH_unit"] = r'$\%$'
    df_out["Gust Speed_unit"] = r'$mph$'
    df_out["Wind Speed_unit"] = r'$mph$'

    # print(df_out.head())

    df_out = df_out[~df_out.index.duplicated(keep='first')]

    # print(df_out.head())

    if fill:
        df_hourly = df_out.resample('1H').nearest(limit=3).interpolate(method='linear',
                                                                       limit=6,
                                                                       limit_direction='forward')  # .ffill()#.bfill()
        df_hourly["Rain"] = df_out.resample('1H').sum()["Rain"]
    else:
        df_hourly = df_out.resample('1H').mean()
        df_hourly["Rain"] = df_out.resample('1H').sum()["Rain"]

    df_hourly["HourOfDay"] = df_hourly.index.hour+1

    ## Temperature in Celsius
    df_hourly["Tc"] = df_hourly["Temperature"].apply(lambda F: (F-32.)/1.8)

    # Wind Speed in m/s
    df_hourly["Ws"] = df_hourly["Wind Speed"].apply(lambda Ws: Ws*0.44704)

    # Saturated Vapor Pressure
    df_hourly["es"] = df_hourly["Tc"].apply(
        lambda Tc: 0.6108*np.exp(Tc*17.27/(Tc + 237.3)))

    # Actual Vapor Pressure
    df_hourly["ea"] = df_hourly.apply(lambda row: row.es*row.RH/100., axis=1)

    # Vapor Pressure Deficit
    df_hourly["VPD"] = df_hourly.apply(lambda row: row.es-row.ea, axis=1)

    df_hourly["DELTA"] = df_hourly.apply(
        lambda row: (4099*row.es)/(row.Tc+237.3)**2, axis=1)

    df_hourly["Lambda"] = df_hourly["Tc"].apply(lambda Tc: 2.501-0.002361*Tc)

    # Presusre Kpa
    P_KPa = 101.592

    df_hourly["GAM"] = df_hourly["Tc"].apply(
        lambda Tc: 0.000646*(1+0.000946*Tc)*P_KPa)

    df_hourly["Gamma"] = df_hourly["Lambda"].apply(lambda L: 0.00163*P_KPa/L)

    df_hourly["W"] = df_hourly.apply(
        lambda row: row.DELTA/(row.DELTA + row.Gamma), axis=1)

    df_hourly["W_cimis"] = df_hourly.apply(
        lambda x: x.DELTA/(x.DELTA + x.GAM), axis=1)

    df_hourly["Air_Emiss"] = df_hourly["ea"].apply(
        lambda ea: 0.74 + 0.049 * ea)

    df_hourly["Ts"] = df_hourly.apply(
        lambda row: row.Tc-2.035+10.672*np.exp((row.HourOfDay-13.398)**2/-18.24), axis=1)

    df_hourly["Rn_Wm2"] = df_hourly.apply(lambda row: 0.77*row["Solar Radiation"] +
                                          row.Air_Emiss*5.67E-8 *
                                          (row.Tc+273.15)**4
                                          - 5.5566E-8*(row.Ts+273.15)**4, axis=1)

    df_hourly["Rn"] = df_hourly["Rn_Wm2"].apply(lambda Rn: Rn*3.6E-3)

    df_hourly["G"] = df_hourly["Rn"].apply(
        lambda Rn: 0.1*Rn if Rn > 0 else 0.5*Rn)

    df_hourly["Cd"] = df_hourly["Rn"].apply(
        lambda Rn: 0.24 if Rn > 0 else 0.96)

    df_hourly["EToHr_theory_mmhr"] = df_hourly.apply(lambda x: (x.DELTA*(x.Rn-x.G)/(x.Lambda*(x.DELTA+x.Gamma*(1+x.Cd*x.Ws))) +
                                                                x.Gamma*37*x.Ws*(x.VPD)/(x.Tc+273.16)/(x.DELTA+x.Gamma*(1+x.Cd*x.Ws))), axis=1)
    df_hourly["EToHr_theory_inhr"] = df_hourly["EToHr_theory_mmhr"].apply(
        lambda ET: 0.0393701*ET)
    df_hourly["EToHr"] = df_hourly["EToHr_theory_inhr"].apply(mapET)

    df_hourly["NR"] = df_hourly.apply(
        lambda x: x.Rn_Wm2/(694.5*(1-0.000946*x.Tc)), axis=1)
    df_hourly["FU"] = df_hourly.apply(
        lambda x: 0.03+0.0576*x.Ws if x.Rn_Wm2 > 0 else 0.125+0.0439*x.Ws, axis=1)

    df_hourly["EToHr_theory_mmhr_cimis"] = df_hourly.apply(
        lambda x: (x.W_cimis*x.NR+(1-x.W)*x.VPD*x.FU), axis=1)
    df_hourly["EToHr_theory_inhr_cimis"] = df_hourly["EToHr_theory_mmhr_cimis"].apply(
        lambda ET: 0.0393701*ET)
    df_hourly["EToHr_cimis"] = df_hourly["EToHr_theory_inhr_cimis"].apply(
        mapET)

    date_ = "Date"+'('+stationInfo[serial]["timeZone"]+')'

    ETdf = df_hourly.resample("1D").agg(["sum", "count", "mean", "min", "max"])
    ETdf = ETdf.loc["2016-03":]

    ETdf_ = ETdf["EToHr"][["sum", "count"]]
    ETdf_["sum"][ETdf_["count"] != 24] = np.nan
#     ETdf_["sum"][ETdf_["sum"]==0] = np.nan
    ETdf0 = ETdf_[["sum"]]
    ETdf0["ETo_PM(inch/day)"] = ETdf_["sum"]
    ETdf0[date_] = ETdf_.index.date

    ETdf_ = ETdf["EToHr_cimis"][["sum", "count"]]
    ETdf_["sum"][ETdf_["count"] != 24] = np.nan
#     ETdf_["sum"][ETdf_["sum"]==0] = np.nan
    ETdf0["ETo_CIMIS(inch/day)"] = ETdf_["sum"]

    ETdf_ = ETdf["Rain"][["sum", "count"]]
    ETdf_["sum"][ETdf_["count"] != 24] = np.nan
    ETdf_["sum"][ETdf_["sum"] < 0] = np.nan
    ETdf0["Rain(inch)"] = ETdf_["sum"]

    ETdf_ = ETdf["Tc"][["mean", "count"]]
#     ETdf_["mean"][ETdf_["count"]!=24] = np.nan
    ETdf0["Tc"] = ETdf_["mean"]

    ETdf_ = ETdf["Tc"][["min", "count"]]
#     ETdf_["min"][ETdf_["count"]!=24] = np.nan
    ETdf0["Tmin"] = ETdf_["min"]

    ETdf_ = ETdf["Tc"][["max", "count"]]
#     ETdf_["max"][ETdf_["count"]!=24] = np.nan
    ETdf0["Tmax"] = ETdf_["max"]

    ETdf_ = ETdf["VPD"][["mean", "count"]]
#     ETdf_["mean"][ETdf_["count"]!=24] = np.nan
    ETdf0["VPD"] = ETdf_["mean"]

    ETdf_ = ETdf["Rn"][["mean", "count"]]
#     ETdf_["mean"][ETdf_["count"]!=24] = np.nan
    ETdf0["Rn"] = ETdf_["mean"]

    if fill:
        ETdf0 = ETdf0[[date_, "ETo_PM(inch/day)", "ETo_CIMIS(inch/day)", "Rain(inch)", "Tc", "Tmin", "Tmax", "VPD", "Rn"]].interpolate(method='linear',
                                                                                                                                       limit=3,
                                                                                                                                       limit_direction='forward')
    else:
        ETdf0 = ETdf0[[date_, "ETo_PM(inch/day)", "ETo_CIMIS(inch/day)",
                       "Rain(inch)", "Tc", "Tmin", "Tmax", "VPD", "Rn"]]

    ETdf0.reset_index(drop=True, inplace=True)

    return ETdf0

 ####################################################


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


def formatGPS(gps):

    lat = ""
    lon = ""

    try:
        gps = [str(x) for x in gps.split(" ")]
        lat = "%2d°:%02d\':%2.2f\" " % (
            float(gps[0]), float(gps[1]), float(gps[2]))+gps[3]
        lon = "%2d°:%02d\':%2.2f\" " % (
            float(gps[4]), float(gps[5]), float(gps[6]))+gps[7]
    except:
        pass

    return lat, lon
####################################################


outFILE = 'HOBO_CAMPBELL_ET0_Rain.xlsx'

xcmd("rm "+outFILE)
xcmd("cp template.xlsx "+outFILE)

####################################################

with pd.ExcelWriter(outFILE, engine='openpyxl', mode='a') as writer:

    for serial in stationInfo:
        sheet_name = stationInfo[serial]["name"]
        print(serial, sheet_name)

        xl_sheet_df = getETxlsx(engine, str(serial), fill=True)
        xl_sheet_df_ = getETxlsx(engine, str(serial), fill=False)

        xl_sheet_df["ETo_PM (raw)"] = xl_sheet_df_["ETo_PM(inch/day)"]
        xl_sheet_df["ETo_CIMIS (raw)"] = xl_sheet_df_["ETo_CIMIS(inch/day)"]
        xl_sheet_df["Rain (raw)"] = xl_sheet_df_["Rain(inch)"]
        
        
        
        sql_df = xl_sheet_df.rename(columns={xl_sheet_df.columns[0]:'Date'})
        sql_df.columns=["Date","ETo_PM_inch_day","ETo_CIMIS_inch_day","Rain_inch","Tc","Tmin","Tmax","VPD","Rn","ETo_PM_raw","ETo_CIMIS_raw","Rain_raw"]
        sql_df.index = pd.to_datetime(sql_df.index)
        sql_df.to_sql(name=str(serial)+'_ETdata', con=engine, if_exists='replace', index=False, chunksize=1000)  

        xl_sheet_df.to_excel(writer, sheet_name=sheet_name)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        autosize_excel_columns(worksheet, xl_sheet_df)
        writer.save()

####################################################
