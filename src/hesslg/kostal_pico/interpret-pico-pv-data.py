# -*- coding: utf-8 -*-

import json
import numpy as np
import pandas as pd
import sys
from datetime import datetime, timedelta

from influxdb import InfluxDBClient

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


client = InfluxDBClient(database='hesslg')

def store_piko_live_data(data):

    def datapoint(point):
        return {
            "measurement": "PV Power",
            "tags": {
                "type": "measurement",
                "source": "kostal pico"
            },
            "fields": {
                "value": point[1][0]
            },
            "time": point[0].tz_localize(tz='Europe/Berlin')
        }


    json_body = [
        datapoint(item) for item in data.iterrows()
    ]

    client.write_points(json_body)

store_piko_live_data(produced_df)


