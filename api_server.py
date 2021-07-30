from flask import render_template
from flask import Flask, jsonify
import connexion
from sqlalchemy import types, create_engine
from datetime import date, timedelta
import Weather_db
import sqlalchemy


engine = create_engine('mysql+mysqlconnector://' +
                       Weather_db.user +
                       ':' + Weather_db.passwd +
                       '@localhost/' +
                       Weather_db.database,
                       echo=False)


stationInfo = {
    '10906989': {"timeZone": "US/Hawaii", "Name": "ALOUN HELEMANO HOBO", "GPS": "21.5356N  -158.0343W"},
    '20173022': {"timeZone": "US/Hawaii", "Name": "HIRAKO HOBO", "GPS": "20.0036N  -155.6864W"},
    '20009161': {"timeZone": "US/Hawaii", "Name": "KULA AG PARK HOBO", "GPS": "20.7972N  -156.3599W"},
    '20121046': {"timeZone": "Pacific/Guam", "Name": "MALOJLOJ MEDA HOBO", "GPS": "13.31893N  144.76374E"},
    '20006321': {"timeZone": "US/Hawaii", "Name": "MA'O HOBO", "GPS": "21.4505N  -1581582W"},
    '20173020': {"timeZone": "US/Hawaii", "Name": "PIONEER CORN HOBO", "GPS": "21.5695N  -158.1561W"},
    '20173019': {"timeZone": "US/Hawaii", "Name": "SEIZEN HOBO", "GPS": "20.0264N  -155.6535W"},
    '20824841': {"timeZone": "Pacific/Guam", "Name": "WATSON HOBO", "GPS": "?"},
    '20824842': {"timeZone": "Pacific/Guam", "Name": "WUSSTIG HOBO", "GPS": "?"},
    '20121045': {"timeZone": "Pacific/Guam", "Name": "YIGO WATSO HOBO", "GPS": "13.5650N  144.8774E"},
    '20121047': {"timeZone": "Pacific/Samoa", "Name": "MALAEIMI HOBO", "GPS": "-14.1914S  -170.4425W"},
    '20121048': {"timeZone": "Pacific/Samoa", "Name": "TAFETA HOBO", "GPS": "-14.32095S  -170.754286W"},
    '20173018': {"timeZone": "US/Hawaii", "Name": "TEXEIRA HOBO", "GPS": "20.7952N  -156.3489W"},
    'PH1': {"timeZone": "US/Hawaii", "Name": "PIONEER GAY CAMPBELL", "GPS": "21.568543N  -158.155975W"},
    'PH2': {"timeZone": "US/Hawaii", "Name": "PIONEER HELENANO CAMPBELL", "GPS": "21.565335N  -158.097097W"},
}


# Create the application instance
app = connexion.App(__name__, specification_dir='./')


# Read the swagger.yml file to configure the endpoints
# app.add_api('swagger.yml')

# Create a URL route in our application for "/"


@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'api.html'
    """

    webDict = {}
    for serial in stationInfo:
        try:
            date  = dailyData(serial)['Date']
            webDict[serial] = date
        except:
            webDict[serial] = ''

    return render_template('api.html', webDict=webDict)

##########################################################################


@app.route('/<serial>/<date>', methods=['GET'])
def chosenDate(serial, date):
    return jsonify(dailyData(serial, date=None))

@app.route('/<serial>', methods=['GET'])
def lastDate(serial):
    return jsonify(dailyData(serial))
    

def queryMaker(serial, date=None):

    db_table = serial + "_ETdata"

    queryTail = " order by Date desc limit 1;"

    if date is not None:
        date = str(date)  # date is originally in the form of an YYYY-MM-dd
        date_str = date[:4] + '-' + date[5:7] + '-' + date[8:10]
        queryTail = " where Date='" + date_str + "';"
        queryMid = ""

    if serial == 'PH1' or serial == 'PH2':
        query = "select `Temp.raw`, `ETo.raw`, `Rainfall.raw`, Date from " + \
                db_table + queryTail
    else:
        query = "select Tc, Tmin, Tmax, ETo_CIMIS_raw, Rain_raw, Date from " + \
                db_table + queryTail
    
    return query



def dailyData(serial, date=None):

    Data = None
    date_str = None
    status = 'success'

    try:

        if serial == 'PH1' or serial == 'PH2':
            query = queryMaker(serial, date)
            sql_query = sqlalchemy.text(query)
            with engine.connect() as connection:
                result = connection.execute(sql_query)
            result = result.fetchall()[0]

            try:
                Tc = '%.2f' % ((result[0] - 32.) / 1.80)
            except BaseException:
                Tc = 'nan'
            try:
                ETo = '%.3f' % result[1]
            except BaseException:
                ETo = 'nan'
            try:
                Rain = '%.3f' % result[2]
            except BaseException:
                Rain = 'nan'

            Data = {'Tc': Tc, 'ETo': ETo, 'Rain': Rain}
            date_str = result[3]

        else:
            query = queryMaker(serial, date)
            sql_query = sqlalchemy.text(query)
            with engine.connect() as connection:
                result = connection.execute(sql_query)
            result = result.fetchall()[0]

            try:
                Tc = '%.2f' % result[0]
            except BaseException:
                Tc = 'nan'
            try:
                Tmin = '%.2f' % result[1]
            except BaseException:
                Tmin = 'nan'
            try:
                Tmax = '%.2f' % result[2]
            except BaseException:
                Tmax = 'nan'
            try:
                ETo = '%.3f' % result[3]
            except BaseException:
                ETo = 'nan'
            try:
                Rain = '%.3f' % result[4]
            except BaseException:
                Rain = 'nan'

            Data = {
                'Tc': Tc,
                'Tmin': Tmin,
                'Tmax': Tmax,
                'ETo': ETo,
                'Rain': Rain}

            date_str = result[5]

    except BaseException:
        status = 'failed'

    if serial in stationInfo:
        station = stationInfo[serial]
    else:
        station = 'not found'
        status = 'failed'

    units = {"Temperature": "Celsius", "ETo": "Inch/day", "Rainfall": "Inch"}

    outDict = {'Status': status, 'Serial': serial, 'Station': station,
                    'Date': date_str, 'Data': Data, "Units": units}

    return outDict

##########################################################################


def format(number, f=2):
    format = "%." + str(f) + "f"
    try:
        return format % number
    except BaseException:
        return None


@app.route('/forecast/<serial>', methods=['GET'])
def Forecast(serial):

    Data = {}

    status = "success"

    if serial in stationInfo:
        station = stationInfo[serial]
    else:
        station = 'not found'
        status = 'failed'

    Data["Serial"] = serial
    Data["Station"] = station

    try:
        query = "select * from Forecasts where serial = '" + \
            serial + "' order by last_update desc limit 1;"
        sql_query = sqlalchemy.text(query)
        with engine.connect() as connection:
            result = connection.execute(sql_query)
        result = result.fetchall()[0]

        Data["Last_date"] = result[2].strftime("%Y-%m-%d")
        Data["ETo_ave3"] = format(result[5], f=3)
        Data["Rain_ave3"] = format(result[17], f=3)

        Day1_ahead = {}
        Day1_ahead["Date"] = result[3]
        Day1_ETo = {}
        Day1_ETo["ETo"] = format(result[4], f=3)
        Day1_ETo["MAE"] = format(result[6], f=3)
        Day1_ETo["R2"] = format(result[7], f=2)
        Day1_ahead["ETo"] = Day1_ETo
        Day1_rain = {}
        Day1_rain["Rain"] = format(result[16], f=3)
        Day1_rain["MAE"] = format(result[18], f=3)
        Day1_rain["R2"] = format(result[19], f=2)
        Day1_ahead["Rain"] = Day1_rain

        Day3_ahead = {}
        Day3_ahead["Date"] = result[8]
        Day3_ETo = {}
        Day3_ETo["ETo"] = format(result[9], f=3)
        Day3_ETo["MAE"] = format(result[10], f=3)
        Day3_ETo["R2"] = format(result[11], f=2)
        Day3_ahead["ETo"] = Day3_ETo

        Day5_ahead = {}
        Day5_ahead["Date"] = result[12]
        Day5_ETo = {}
        Day5_ETo["ETo"] = format(result[13], f=3)
        Day5_ETo["MAE"] = format(result[14], f=3)
        Day5_ETo["R2"] = format(result[15], f=2)
        Day5_ahead["ETo"] = Day5_ETo

        predict = {}
        predict['Day1_ahead'] = Day1_ahead
        predict['Day3_ahead'] = Day3_ahead
        predict['Day5_ahead'] = Day5_ahead

        Data["Forecast"] = predict

        Data["Units"] = {
            "Temperature": "Celsius",
            "ETo": "Inch/day",
            "Rainfall": "Inch"}

        Metadata = {}
        Metadata["Last_date"] = "The most recent date with available measurements"
        Metadata["Rain_ave3"] = "The average of the measured rainfall in the previous three days"
        Metadata["ETo_ave3"] = "The average of the measured ETo in the previous three days"
        Metadata["MAE"] = "Mean Absolute Error of the model that is evaluated based on the training data"
        Metadata["R2"] = "R-squared, a statistical measure of how closely the model fits the data"
        Metadata["last_update"] = "The server clock when the latest forecasts were processed"
        Data["Metadata"] = Metadata

        Data["last_update"] = result[20]

    except BaseException:
        status = 'failed'

    Data['status'] = status

    return jsonify(Data)


# If we're running in sdate_strtand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
