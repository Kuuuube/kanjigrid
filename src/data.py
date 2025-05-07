import collections
import json
import os
import sys
import traceback

if "pytest" not in sys.modules:
    from . import logger

GROUPING_JSON_VERSION = 1

KanjiGrouping = collections.namedtuple("KanjiGroups", ["version", "name", "lang", "source", "leftover_group", "groups"])
KanjiGroup = collections.namedtuple("KanjiGroup", ["name", "characters"])

groupings = []


def load_from_folder(groupings: KanjiGrouping, path: str) -> None:
    for file in os.listdir(path):
        filepath = path + "/" + file
        try:
            grouping_json = json.loads(open(filepath, "r", encoding = "utf-8", errors = "replace").read())  # noqa: SIM115

            if "version" not in grouping_json or GROUPING_JSON_VERSION > grouping_json["version"]:
                grouping_json = migrate_grouping(grouping_json)

            groups = []
            for group in grouping_json["groups"]:
                groups.append(KanjiGroup(group["name"], group["characters"]))
            groupings.append(KanjiGrouping(grouping_json["version"], grouping_json["name"], grouping_json["lang"], grouping_json["source"], grouping_json["leftover_group"], groups))
        except Exception:  # noqa: BLE001
            logger.error_log(f"Failed to load Kanji Grid data file \"{filepath}\". It might be corrupted or outdated.", traceback.format_exc())

def init_groups() -> None:
    global groupings  # noqa: PLW0603
    groupings = []
    cwd = os.path.dirname(__file__)
    data_folder = cwd + "/data"
    load_from_folder(groupings, data_folder)

    # user_files persists across addon updates
    user_data_folder = cwd + "/user_files/data"
    os.makedirs(user_data_folder, exist_ok=True)
    load_from_folder(groupings, user_data_folder)

    groupings.sort(key = lambda group: group.lang + group.name)

def migrate_grouping(grouping_json: dict) -> dict:
    if "version" not in grouping_json:
        grouping_json["version"] = 0

    grouping_json_updates = [grouping_update_1]
    if len(grouping_json_updates) > grouping_json["version"]:
        for grouping_json_update in grouping_json_updates[grouping_json["version"]:]:
            grouping_json = grouping_json_update(grouping_json)
        grouping_json["version"] = GROUPING_JSON_VERSION
    return grouping_json

def grouping_update_1(grouping_json: dict) -> dict:
    new_grouping_json = {}
    new_grouping_json["version"] = grouping_json["version"]
    new_grouping_json["name"] = grouping_json["name"]
    new_grouping_json["lang"] = grouping_json["lang"]
    new_grouping_json["source"] = grouping_json["source"]
    new_grouping_json["leftover_group"] = grouping_json["data"][0][0]
    del grouping_json["data"][0]
    new_grouping_json["groups"] = []
    for group in grouping_json["data"]:
        new_grouping_json["groups"].append({"name": group[0], "characters": group[1]})
    return new_grouping_json
