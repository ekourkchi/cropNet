#!/usr/bin/bash

. "/home/share/anaconda3/etc/profile.d/conda.sh"
export PATH="/home/share/anaconda3/bin:$PATH"

cd /home/weather/GetData

# This code starts the python flask server that  runs the API
# This code is executed when the server boots up and autoamtically starts the API service

python api_server.py



