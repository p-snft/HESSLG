# -*- coding: utf-8 -*-
"""
This is part of a longer pipeline:
1.  Meter data is loaded from /dev/ttyUSB0
2.  raw SML is converted to text using sml_server
    cat ${DIRECTORY}/${TIMESTAMP}.raw | /usr/local/bin/sml_server - | tail -n 4 > ${DIRECTORY}/${TIMESTAMP}.txt
3.  This data is interpreted using the present script:
    python3 interpret-meter-data.py ${DIRECTORY}/${TIMESTAMP}.txt >> ${BASEDIR}/meter-data.csv
"""
import sys
from datetime import datetime

from influxdb import InfluxDBClient

if len(sys.argv) != 2 or sys.argv[1][-4:] != ".txt":
    print("Usage: " + sys.argv[0] + " (meter-file).txt")
    sys.exit()

FILE_BASENAME = sys.argv[1][:-4]

influx_client = InfluxDBClient(database='hesslg')

bought = 0.0
sold = 0.0

with open(FILE_BASENAME + ".txt", 'r') as meter_file:
    content = meter_file.read().split('\n')

    # casts to check data validity
    time_format_windows_friendly = "%Y-%m-%dT%H-%M-%SZ"
    time_format_user_friendly = "%Y-%m-%dT%H:%M:%SZ"
    time_string = FILE_BASENAME.split('/')[-1].split('.')[0]
    timestamp = datetime.strptime(time_string, time_format_windows_friendly)
    bought = float(content[1].split('#')[1])
    sold = float(content[2].split('#')[1])

    print(timestamp.strftime(time_format_user_friendly) + "," + str(bought) + "," + str(sold))

json_body = [
    {
                "measurement": "total bought electricity",
                "tags": {
                    "type": "measurement",
                    "source": "dzg"
                },
                "fields": {
                    "value": bought
                }
            }, {
                "measurement": "total sold electricity",
                "tags": {
                    "type": "measurement",
                    "source": "dzg"
                },
                "fields": {
                    "value": sold
                }
    }
]

influx_client.write_points(json_body)
