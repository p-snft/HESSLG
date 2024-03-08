# -*- coding: utf-8 -*-

import json
import requests
import sys

from influxdb import InfluxDBClient

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " (host)")
    # sys.exit()
    FRONIUS_INVERTER_HOSTNAME = "192.168.178.56"
else:
    FRONIUS_INVERTER_HOSTNAME = sys.argv[1][:-5]

FRONIUS_API_STRING = "/solar_api/v1/"

def get_data(cgi_code):
    url = "http://" + FRONIUS_INVERTER_HOSTNAME + FRONIUS_API_STRING + cgi_code + ".cgi"
    return json.loads(requests.get(url).text)


meter_data = get_data("GetMeterRealtimeData")["Body"]["Data"]["0"]
inverter_data = get_data("GetInverterRealtimeData")
storage_data = get_data("GetStorageRealtimeData")["Body"]["Data"]["0"]["Controller"]

client = InfluxDBClient(database='hesslg')

json_body = [
    {
        "measurement": "MeterData0",
        "tags": {
            "type": "measurement",
            "source": "Fronius Smart Meter TS 65A-3"
        },
        "fields": {
            "EnergyReal_WAC_Minus_Absolute": meter_data["EnergyReal_WAC_Minus_Absolute"],
            "EnergyReal_WAC_Plus_Absolute": meter_data["EnergyReal_WAC_Plus_Absolute"],

        },
        "time": meter_data["TimeStamp"]
    }, {
        "measurement": "InverterData",
        "tags": {
            "type": "measurement",
            "source": "Fronius Inverter"
        },
        "fields": {
            "value": inverter_data["Body"]["Data"]["TOTAL_ENERGY"]["Values"]["1"],
        },
        "time": inverter_data["Head"]["Timestamp"]
    }, {
        "measurement": "StorageData",
        "tags": {
            "type": "measurement",
            "source": "BYD Battery-Box Premium HV",
        },
        "fields": {
            "StateOfCharge_Relative": storage_data["StateOfCharge_Relative"],
            "Temperature_Cell": storage_data["Temperature_Cell"],
        },
        "time": storage_data["TimeStamp"]
    }
]

client.write_points(json_body)
