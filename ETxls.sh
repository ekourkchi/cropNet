#!/usr/bin/bash

echo begin `date`

. "/home/share/anaconda3/etc/profile.d/conda.sh"
export PATH="/home/share/anaconda3/bin:$PATH"

cd /home/weather/GetData

# Downloading new data and updating the database
python Hobo_LONG_getData.py

# Generating the Excel file for all HOBO stations
python ET2XLS_HOBO.py

# Adding Campbell stations to the Excel file
python ET2XLS_Campbell.py

# transerind data to the http zone
cp HOBO_CAMPBELL_ET0_Rain.xlsx /home/weather/public_html/.

# managing the ownership of the file
chown weather:weather /home/weather/public_html/HOBO_CAMPBELL_ET0_Rain.xlsx


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

