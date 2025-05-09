import json
import os
import sys


def dedupe_groups_characters(data_directory: str) -> None:
    for file in os.listdir(data_directory):
        filepath = data_directory + "/" + file
        data_json = json.load(open(filepath, "r", encoding = "UTF8"))
        for i, grouping_data in enumerate(data_json["groups"]):
            kanji_list = list(grouping_data["characters"])
            kanji_list_deduped = list(dict.fromkeys(kanji_list))

            data_json["groups"][i]["characters"] = "".join(kanji_list_deduped)
            json.dump(data_json, open(filepath, "w", encoding = "UTF8"), indent = 4, ensure_ascii = False)

dedupe_groups_characters(sys.path[0] + "/../data")
