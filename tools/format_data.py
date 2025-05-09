import os
import json
import sys

def format_data(data_directory):
    for file in os.listdir(data_directory):
        filepath = data_directory + "/" + file
        data_json = json.load(open(filepath, "r", encoding = "UTF8"))
        json.dump(data_json, open(filepath, "w", encoding = "UTF8"), indent = 4, ensure_ascii = False)

format_data(sys.path[0] + "/../data")
