#!/usr/bin/bash

# This script is run by the server everyday at 1:00 AM

echo begin `date`

# Setting up the python essentials
. "/home/share/anaconda3/etc/profile.d/conda.sh"
export PATH="/home/share/anaconda3/bin:$PATH"

# Changing to the work directory
cd /home/weather/GetData

# Downloading new data and updating the database
python Hobo_LONG_getData.py

# Generating the Excel file for all HOBO stations
python ET2XLS_HOBO.py

# Adding Campbell stations to the Excel file
python ET2XLS_Campbell.py

# Transering data to the http zone
cp HOBO_CAMPBELL_ET0_Rain.xlsx /home/weather/public_html/.

# Managing the ownership of the file
chown weather:weather /home/weather/public_html/HOBO_CAMPBELL_ET0_Rain.xlsx

# Forecasting ETo and Rainfall for a list of stations
# usage$ python forecaste_ETrain.py <seril_type> <serial_no>
# serial_type: the data type of the serial number, either "integer" or "string"
# serial_no: the serial number or the assigned code of the desired station
# Note: the addressed station should have vlaid data input in the database

python forecaste_ETrain.py integer 10906989
python forecaste_ETrain.py integer 20173022
python forecaste_ETrain.py integer 20009161
python forecaste_ETrain.py integer 20121046
python forecaste_ETrain.py integer 20006321
python forecaste_ETrain.py integer 20173020
python forecaste_ETrain.py integer 20173019
python forecaste_ETrain.py integer 20824841
python forecaste_ETrain.py integer 20824842
python forecaste_ETrain.py integer 20121045
python forecaste_ETrain.py string  PH1
python forecaste_ETrain.py string  PH2



echo end `date`

