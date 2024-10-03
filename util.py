import re
import unicodedata
import collections
import enum

from . import data

unit_tuple = collections.namedtuple("unit", "idx value avg_interval count")

class SortOrder(enum.Enum):
    NONE = 0
    UNICODE = 1
    SCORE = 2
    FREQUENCY = 3

    def pretty_value(self):
        return (
            "order found",
            "unicode order",
            "score",
            "frequency",
        )[self.value]

cjk_re = re.compile("CJK (UNIFIED|COMPATIBILITY) IDEOGRAPH")
def isKanji(unichar):
    return bool(cjk_re.match(unicodedata.name(unichar, "")))

def scoreAdjust(score):
    score += 1
    return 1 - 1 / (score * score)

def addUnitData(units, unitKey, i, card, kanjionly):
    validKey = data.ignore.find(unitKey) == -1 and (not kanjionly or isKanji(unitKey))
    if validKey:
        if unitKey not in units:
            unit = unit_tuple(0, unitKey, 0.0, 0)
            units[unitKey] = unit
        units[unitKey] = addDataFromCard(units[unitKey], i, card)

def addDataFromCard(unit, idx, card):
    new_idx = unit.idx
    new_avg_interval = unit.avg_interval
    new_count = unit.count

    if card.type > 0:
        newTotal = (unit.avg_interval * unit.count) + card.ivl
        new_count = unit.count + 1
        new_avg_interval = newTotal / new_count

    if new_idx < unit.idx or unit.idx == 0:
        new_idx = idx

    return unit_tuple(new_idx, unit.value, new_avg_interval, new_count)

def hsvrgbstr(h, s=0.8, v=0.9):
    def _256(x):
        return round(x * 256)
    i = int(h*6.0)
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i % 6
    if i == 0:
            return "#%0.2X%0.2X%0.2X" % (_256(v), _256(t), _256(p))
    if i == 1:
            return "#%0.2X%0.2X%0.2X" % (_256(q), _256(v), _256(p))
    if i == 2:
            return "#%0.2X%0.2X%0.2X" % (_256(p), _256(v), _256(t))
    if i == 3:
            return "#%0.2X%0.2X%0.2X" % (_256(p), _256(q), _256(v))
    if i == 4:
            return "#%0.2X%0.2X%0.2X" % (_256(t), _256(p), _256(v))
    if i == 5:
            return "#%0.2X%0.2X%0.2X" % (_256(v), _256(p), _256(q))

def get_background_color(avg_interval, config_interval, count, missing = False):
    if count != 0:
        return hsvrgbstr(scoreAdjust(avg_interval / config_interval)/2)
    elif missing:
        return "#EEE"
    else:
        return "#FFF"

def get_font_css(config):
    if config.lang == "ja":
        return config.jafontcss
    if config.lang ==  "zh":
        return config.zhfontcss
    if config.lang ==  "zh-Hans":
        return config.zhhansfontcss
    if config.lang ==  "zh-Hant":
        return config.zhhantfontcss
    if config.lang ==  "ko":
        return config.kofontcss
    if config.lang ==  "vi":
        return config.vifontcss

def get_search(config, char):
    search_url = ""
    if config.lang == "ja":
        search_url = config.jasearch
    if config.lang ==  "zh":
        search_url = config.zhsearch
    if config.lang ==  "zh-Hans":
        search_url = config.zhhanssearch
    if config.lang ==  "zh-Hant":
        search_url = config.zhhantsearch
    if config.lang ==  "ko":
        search_url = config.kosearch
    if config.lang ==  "vi":
        search_url = config.visearch
    return search_url.replace("%s", char)

def fields_to_query(fields):
    query_strings = []
    for field in fields:
        query_strings.append("\"" + str(field) + ":*\"")
    return " OR ".join(query_strings)

def make_query(deck_ids, fields):
    query_strings = []
    fields_string = fields_to_query(fields)
    for deck_id in deck_ids:
        query_strings.append("(did:" + str(deck_id) + " AND (" + fields_string + "))")

    return " OR ".join(query_strings)
