import os
import json
import sys

def dedupe_data(data_directory):
    for file in os.listdir(data_directory):
        filepath = data_directory + "/" + file
        data_json = json.load(open(filepath, "r", encoding = "UTF8"))
        for i, grouping_data in enumerate(data_json["data"]):
            kanji_list = list(grouping_data[1])
            kanji_list_deduped = list(dict.fromkeys(kanji_list))

            data_json["data"][i][1] = "".join(kanji_list_deduped)
            json.dump(data_json, open(filepath, "w", encoding = "UTF8"), indent = 4, ensure_ascii = False)

dedupe_data(sys.path[0] + "/../data")
