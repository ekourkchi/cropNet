#!/usr/bin/bash

. "/home/share/anaconda3/etc/profile.d/conda.sh"
export PATH="/home/share/anaconda3/bin:$PATH"

cd /home/weather/GetData

python api_server.py 



