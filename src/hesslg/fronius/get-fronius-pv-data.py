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
    url = "http://" + FRONIUS_INVERTER_HOSTNAME + FRONIUS_API_STRING + cgi_code
    return json.loads(requests.get(url).text)


meter_data = get_data("GetMeterRealtimeData.cgi")["Body"]["Data"]["0"]
inverter_data = get_data("GetInverterRealtimeData.cgi")
storage_data = get_data("GetStorageRealtimeData.cgi")["Body"]["Data"]["0"]["Controller"]
power_flow_data = get_data("GetPowerFlowRealtimeData.fcgi")
power_flow_time = power_flow_data["Head"]["Timestamp"]
power_flow_site = power_flow_data["Body"]["Data"]["Site"]

client = InfluxDBClient(database='hesslg')


def power_flow(feature_string):
    return {
        "measurement": feature_string,
        "tags": {
            "type": "measurement",
            "source": "Fronius Inverter",
        },
        "fields": {
            "value": power_flow_site[feature_string],
        },
        "time": power_flow_time,
    }


json_body = [
    {
        "measurement": "EnergyReal_WAC_Minus_Absolute",
        "tags": {
            "type": "measurement",
            "source": "Fronius Smart Meter TS 65A-3"
        },
        "fields": {
            "value": meter_data["EnergyReal_WAC_Minus_Absolute"],

        },
        "time": meter_data["TimeStamp"]
    }, {
        "measurement": "EnergyReal_WAC_Plus_Absolute",
        "tags": {
            "type": "measurement",
            "source": "Fronius Smart Meter TS 65A-3"
        },
        "fields": {
            "value": meter_data["EnergyReal_WAC_Plus_Absolute"],

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
        "measurement": "Battery_SOC",
        "tags": {
            "type": "measurement",
            "source": "BYD Battery-Box Premium HV",
        },
        "fields": {
            "value": storage_data["StateOfCharge_Relative"],
        },
    }, {
        "measurement": "Battery_Temperature",
        "tags": {
            "type": "measurement",
            "source": "BYD Battery-Box Premium HV",
        },
        "fields": {
            "value": storage_data["Temperature_Cell"],
        },
    }, {
        "measurement": "P_PV_extra",
        "tags": {
            "type": "measurement",
            "source": "Fronius Smart Meter TS 65A-3",
        },
        "fields": {
            "value": power_flow_data["Body"]["Data"]["SecondaryMeters"]["1"]["P"],
        },
    }, {
        "measurement": "P_PV_total",
        "tags": {
            "type": "derived",
        },
        "fields": {
            "value":
                power_flow_data["Body"]["Data"]["SecondaryMeters"]["1"]["P"]
                + power_flow_site["P_PV"]
        },
    }, {
        "measurement": "P_HP",
        "tags": {
            "type": "measurement",
            "source": "Fronius Smart Meter TS 65A-3",
        },
        "fields": {
            "value": power_flow_data["Body"]["Data"]["SecondaryMeters"]["2"]["P"],
        },
    },
    power_flow("P_Akku"),
    power_flow("P_Grid"),
    power_flow("P_Load"),
    power_flow("P_PV"),
]

client.write_points(json_body)
