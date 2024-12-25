import os
import collections
import json

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
        with open(filepath, encoding = "utf-8") as f:
            try:
                grouping_json = json.loads(f.read())
                groups.append(KanjiGroups(grouping_json["name"], grouping_json["source"], grouping_json["lang"], grouping_json["data"]))
            except Exception:
                # rethrow with msg in case a custom file in user_files is outdated
                raise Exception(f"Failed to load Kanji Grid data file \"{file}\". It might be corrupted or outdated.")


def init_groups():
    global groups
    groups = []
    cwd = os.path.dirname(__file__)
    data_folder = cwd + "/data"
    load_from_folder(groups, data_folder)

    # user_files persists across addon updates
    user_files_folder = cwd + "/user_files"
    if os.path.exists(user_files_folder):
        load_from_folder(groups, user_files_folder)

    groups.sort(key = lambda group: group.name)
