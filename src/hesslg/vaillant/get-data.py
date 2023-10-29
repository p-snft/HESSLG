#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime
from dataclasses import asdict
from influxdb import InfluxDBClient
import sys
import yaml

from myPyllant.api import MyPyllantAPI


async def _get_myvaillant_live_data(
        user,
        password,
        brand="vaillant",
        country="germany",
):
    async with MyPyllantAPI(user, password, brand, country) as api:
        data = []
        async for system in api.get_systems():
            data.append(asdict(system))
        return data


def get_myvaillant_live_data(username, password):
    data = asyncio.get_event_loop().run_until_complete(
        _get_myvaillant_live_data(
            username,
            password,
        )
    )
    system_status = data[0]['state']['system']
    home_status = data[0]['state']['zones'][0]
    circuit_status = data[0]['state']['circuits'][0]
    dhw_status = data[0]['state']['dhw'][0]

    live_data = {
        "timestamp": (data[0]['devices'][0]['last_data']).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "outdoor_temperature": system_status['outdoor_temperature'],
        "outdoor_temperature_average24h": system_status['outdoor_temperature_average24h'],
        "system_flow_temperature": system_status['system_flow_temperature'],
        "system_water_pressure": system_status['system_water_pressure'],
        "circuit_state": circuit_status['circuit_state'],
        "current_circuit_flow_temperature": circuit_status['current_circuit_flow_temperature'],
        "desired_room_temperature_setpoint_heating": home_status['desired_room_temperature_setpoint_heating'],
        "current_room_temperature": home_status['current_room_temperature'],
        "current_dhw_temperature": dhw_status['current_dhw_temperature'],
        "dhw_state": dhw_status['current_special_function'],
    }

    return live_data


def print_myvaillant_live_data(data):
    print(*list(data.keys()), sep=", ")
    print(*list(data.values()), sep=", ")

def store_myvaillant_live_data(data):
    client = InfluxDBClient(database='hesslg')

    def _datapoint_dict(label):
        datapoint_dict = {
                "measurement": label,
                "tags": {
                    "type": "measurement",
                    "source": "vaillant"
                },
                "fields": {
                    "value": data[label]
                }
            }
        return datapoint_dict

    json_body = [
        _datapoint_dict("outdoor_temperature"),
        _datapoint_dict("system_flow_temperature"),
        _datapoint_dict("system_water_pressure"),
        _datapoint_dict("current_circuit_flow_temperature"),
        _datapoint_dict("current_room_temperature"),
        _datapoint_dict("current_dhw_temperature")
    ]

    client.write_points(json_body)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        settings_file_name = sys.argv[1]
    else:
        settings_file_name = "../settings.yaml"
    with open(settings_file_name, "r") as settings_file:
        settings = yaml.safe_load(settings_file)
    username = settings["multimatic"]["username"]
    password = settings["multimatic"]["password"]
    data = get_myvaillant_live_data(username, password)
    print_myvaillant_live_data(data)
    store_myvaillant_live_data(data)
