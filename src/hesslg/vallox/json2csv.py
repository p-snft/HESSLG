# -*- coding: utf-8 -*-

import fileinput
import re
import datetime
import json
import pandas as pd


def fix_json(vallox_json_file_name, fixed_json_file_name):
    with open(fixed_json_file_name, "w") as fixed_file:
        for line in fileinput.input(files=vallox_json_file_name):
            date_string = re.findall("datetime.datetime\(.*\)", line)
            line = line.replace("'", '"')
            if len(date_string) > 0:
                date_string = date_string[0]
                # FIXME: Interprets and runs part of the "json".
                #  It would be safer to grep the correct parts
                #  from the line and treat it as data.
                date = eval(date_string)
                fixed_file.write(line.replace(date_string, '"' + str(date) + '"'))
            else:
                fixed_file.write(line)

        fixed_file.close()


def json2csv(json_file_name, csv_file_name):
    with open(json_file_name, "r") as fixed_file:
        vallox_data = json.load(fixed_file)

        data_table = pd.DataFrame(columns=[
            'extract_air_temp',
            'outdoor_air_temp',
            'supply_air_temp',
            'exhaust_air_temp',
            'co2',
            'humidity',
            '8',
        ])

        for data_list in vallox_data:
            for item in data_list:
                data_table.loc[item["date"], item["name"]] = item["value"]

        data_table.sort_index(inplace=True)
        data_table.to_csv(csv_file_name)


if __name__ == "__main__":
    vallox_json_file = "2021-12-28_vallox-data.json"
    fixed_json_file = vallox_json_file.replace("-data.json", "-data-fixed.json")
    vallox_csv_file = vallox_json_file.replace(".json", ".csv")

    fix_json(vallox_json_file, fixed_json_file)
    json2csv(fixed_json_file, vallox_csv_file)
