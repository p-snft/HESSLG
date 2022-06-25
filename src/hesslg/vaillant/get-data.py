#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import asyncio
from datetime import datetime
import sys
import yaml

from pymultimatic.api import Connector, ApiError, urls
from pymultimatic.model import mapper


async def _get_multimatic_live_data(user, password):
    async with aiohttp.ClientSession() as sess:

        connector = Connector(user, password, sess)

        try:
            await connector.login(True)
        except ApiError as err:
            print('Cannot login: ' + await err.response.text())

        facilities = await connector.get(urls.facilities_list())
        serial = mapper.map_serial_number(facilities)

        requests = {}
        params = {'serial': serial}
        req = connector.get(urls.live_report(**params))
        requests.update({urls.live_report.__name__: req})

        responses = {}
        for key in requests:
            try:
                responses.update({key: await requests[key]})
            except ApiError as api_err:
                responses.update({key: api_err.response})
            except err:
                print('Cannot get response for {}, skipping it'.format(key))

        data = dict()

        for key in responses:
            reports = responses[key]["body"]["devices"]
            meta = responses[key]["meta"]["resourceState"]
            for report_group, report_meta in zip(reports, meta):
                for report in report_group["reports"]:
                    datetime_obj = datetime.utcfromtimestamp(report_meta["timestamp"])
                    timestamp = datetime_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                    data[report["_id"] + " (timestamp)"] = timestamp
                    data[report["_id"] + " (" + report["unit"] + ")"] = report["value"]

        return data


def get_multimatic_live_data(username, password):
    return asyncio.get_event_loop().run_until_complete(
        _get_multimatic_live_data(username, password))


def print_multimatic_live_data(username, password):
    data = get_multimatic_live_data(username, password)

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


