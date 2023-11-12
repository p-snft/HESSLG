#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from vallox_websocket_api import Client
from influxdb import InfluxDBClient


VALLOX_510_MV_IP = '192.168.178.29'

vallox_client = Client(VALLOX_510_MV_IP)


async def fetch_current():
    data = await vallox_client.fetch_metrics([
        'A_CYC_CO2_VALUE',
        'A_CYC_EXTRACT_EFFICIENCY',
        'A_CYC_FAN_SPEED',
        'A_CYC_HOME_AIR_TEMP_TARGET',
        'A_CYC_RH_VALUE',
        'A_CYC_TEMP_EXHAUST_AIR',
        'A_CYC_TEMP_EXTRACT_AIR',
        'A_CYC_TEMP_OUTDOOR_AIR',
        'A_CYC_TEMP_SUPPLY_AIR',
        'A_CYC_TEMP_SUPPLY_CELL_AIR',
    ])


    influx_client = InfluxDBClient(database='hesslg')

    def _datapoint_dict(label):
        datapoint_dict = {
                "measurement": label,
                "tags": {
                    "type": "measurement",
                    "source": "vallox"
                },
                "fields": {
                    "value": data[label]
                }
            }
        return datapoint_dict

    json_body = [
        _datapoint_dict("A_CYC_TEMP_EXHAUST_AIR"),
        _datapoint_dict("A_CYC_TEMP_EXTRACT_AIR"),
        _datapoint_dict("A_CYC_TEMP_OUTDOOR_AIR"),
        _datapoint_dict("A_CYC_TEMP_SUPPLY_AIR"),
        _datapoint_dict("A_CYC_TEMP_SUPPLY_CELL_AIR")
    ]

    influx_client.write_points(json_body)

    print(*list(data.keys()), sep=", ")
    print(*list(data.values()), sep=", ")


if __name__ == "__main__":
    asyncio.run(fetch_current())
