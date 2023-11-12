# -*- coding: utf-8 -*-

import json
import numpy as np
import pandas as pd
import sys
from datetime import datetime, timedelta

if len(sys.argv) != 2 or sys.argv[1][-5:] != ".json":
    print("Usage: " + sys.argv[0] + " (Pico-File).json")
    sys.exit()

JSON_FILE_BASENAME=sys.argv[1][:-5]

with open(JSON_FILE_BASENAME+".json", 'r') as json_file:
    data = json.load(json_file)
    
    produced_date = datetime.strptime(
        data['DayCurves']['Datasets'][0]['Data'][0]['Timestamp'],
        "%Y-%m-%d")
    produced_step = data['DayCurves']['Datasets'][0]['Data'][0]['Offset']
    produced_hour = produced_step//6
    produced_minute = produced_step%6*10
    
    produced_start = produced_date + timedelta(hours = produced_hour,
                                               minutes = produced_minute)
    
    produced_data = np.array(data['DayCurves']['Datasets'][0]['Data'][0]['Data'])
    produced_time = [produced_start + i*timedelta(minutes=10)
                      for i in range(len(produced_data))]
    
    produced_df = pd.DataFrame(produced_data,
                               columns=['produced (W)'],
                               index=produced_time)

    produced_df.to_csv(JSON_FILE_BASENAME+".csv",
                       date_format='%Y-%m-%dT%H:%M:%S')


