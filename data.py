import os
import collections
import json

GROUPING_JSON_VERSION = 1

KanjiGroups = collections.namedtuple("KanjiGroups", ["name", "source", "lang", "data"])

ignore = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + \
          "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ" + \
          "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ" + \
          "1234567890１２３４５６７８９０" + \
          "あいうゔえおぁぃぅぇぉかきくけこがぎぐげごさしすせそざじずぜぞ" + \
          "たちつてとだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽ" + \
          "まみむめもやゃゆゅよょらりるれろわをんっ" + \
          "アイウヴエオァィゥェォカキクケコガギグゲゴサシスセソザジズゼゾ" + \
          "タチツテトダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポ" + \
          "マミムメモヤャユュヨョラリルレロワヲンッ" + \
          "!\"$%&'()|=~-^@[;:],./`{+*}<>?\\_" + \
          "＠「；：」、。・‘｛＋＊｝＜＞？＼＿！”＃＄％＆’（）｜＝．〜～ー＾ ゙゙゚" + \
          "☆★＊○●◎〇◯“…『』#♪ﾞ〉〈→》《π×"

groups = []


def load_from_folder(groups, path):
    for file in os.listdir(path):
        filepath = path + "/" + file
        try:
            grouping_json = json.loads(open(filepath, "r", encoding = "utf-8").read())

            if "version" not in grouping_json or GROUPING_JSON_VERSION > grouping_json["version"]:
                grouping_json = migrate_data(grouping_json)

            groups.append(KanjiGroups(grouping_json["name"], grouping_json["source"], grouping_json["lang"], grouping_json["data"]))
        except Exception:
            # rethrow with msg in case a custom file in user_files is outdated
            raise Exception(f"Failed to load Kanji Grid data file \"{filepath}\". It might be corrupted or outdated.")

def init_groups():
    global groups
    groups = []
    cwd = os.path.dirname(__file__)
    data_folder = cwd + "/data"
    load_from_folder(groups, data_folder)

    # user_files persists across addon updates
    user_data_folder = cwd + "/user_files/data"
    os.makedirs(user_data_folder, exist_ok=True)
    load_from_folder(groups, user_data_folder)

    groups.sort(key = lambda group: group.lang + group.name)

def migrate_data(grouping_json):
    if "version" not in grouping_json:
        grouping_json["version"] = 0

    grouping_json_updates = [data_update_1]
    if len(grouping_json_updates) > grouping_json["version"]:
        for grouping_json_update in grouping_json_updates[grouping_json["version"]:]:
            grouping_json = grouping_json_update(grouping_json)
        grouping_json["version"] = GROUPING_JSON_VERSION
    return grouping_json

def data_update_1(grouping_json):
    return grouping_json
