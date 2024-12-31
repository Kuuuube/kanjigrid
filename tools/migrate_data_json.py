import sys
# add main folder to path to allow accessing module there
sys.path.append(sys.path[0] + "/../.")

import os
import json

import data

def migrate(data_directory):
    for file in os.listdir(data_directory):
        filepath = data_directory + "/" + file
        data_json = json.load(open(filepath, "r", encoding = "UTF8"))
        data_json = data.migrate_grouping(data_json)
        json.dump(data_json, open(filepath, "w", encoding = "UTF8"), indent = 4, ensure_ascii = False)

migrate(sys.path[0] + "/../data")
