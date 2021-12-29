#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from vallox_websocket_api import Client

VALLOX_510_MV_IP = '192.168.178.29'

client = Client(VALLOX_510_MV_IP)


async def run():
    data = await client.fetch_raw_logs()

    from pprint import pprint
    pprint(data)
asyncio.get_event_loop().run_until_complete(run())
