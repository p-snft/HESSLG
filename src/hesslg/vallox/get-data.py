#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from pprint import pprint
from vallox_websocket_api import Client

VALLOX_510_MV_IP = '192.168.178.29'

client = Client(VALLOX_510_MV_IP)


async def fetch_current():
    metrics = await client.fetch_metrics([
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
    print(*list(metrics.keys()), sep=", ")
    print(*list(metrics.values()), sep=", ")


asyncio.run(fetch_current())
