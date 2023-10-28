#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime
from dataclasses import asdict
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
        "outdoor temperature (°C)": system_status['outdoor_temperature'],
        "24 h average outdoor temperature (°C)": system_status['outdoor_temperature_average24h'],
        "flow temperature (°C)": system_status['system_flow_temperature'],
        "water pressure (bar)": system_status['system_water_pressure'],
        "circuit state": circuit_status['circuit_state'],
        "circuit temperature (°C)": circuit_status['current_circuit_flow_temperature'],
        "room temperature setpoint (°C)": home_status['desired_room_temperature_setpoint_heating'],
        "room temperature (°C)": home_status['current_room_temperature'],
        "dhw temperature (°C)": dhw_status['current_dhw_temperature'],
        "dhw state": dhw_status['current_special_function'],
    }

    return live_data


def print_multimatic_live_data(username, password):
    data = get_myvaillant_live_data(username, password)

    print(*list(data.keys()), sep=", ")
    print(*list(data.values()), sep=", ")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        settings_file_name = sys.argv[1]
    else:
        settings_file_name = "../settings.yaml"
    with open(settings_file_name, "r") as settings_file:
        settings = yaml.safe_load(settings_file)
    username = settings["multimatic"]["username"]
    password = settings["multimatic"]["password"]
    print_multimatic_live_data(username, password)


