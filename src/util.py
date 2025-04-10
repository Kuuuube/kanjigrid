import re
import unicodedata
import collections
import enum
from colorsys import hsv_to_rgb

unit_tuple = collections.namedtuple("unit", "idx value avg_interval seen_cards_count unseen_cards_count")

class SortOrder(enum.Enum):
    NONE = 0
    UNICODE = 1
    SCORE = 2
    SEEN_CARDS_COUNT = 3
    UNSEEN_CARDS_COUNT = 4

    def pretty_value(self):
        return (
            "none",
            "unicode order",
            "score",
            "seen cards count",
            "unseen cards count"
        )[self.value]

ignored_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + \
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

cjk_re = re.compile("CJK (UNIFIED|COMPATIBILITY) IDEOGRAPH")
def isKanji(unichar):
    return bool(cjk_re.match(safe_unicodedata_name(unichar)))

def scoreAdjust(score):
    score += 1
    return 1 - 1 / (score * score)

def addUnitData(units, unitKey, i, card, kanjionly):
    validKey = ignored_characters.find(unitKey) == -1 and (not kanjionly or isKanji(unitKey))
    if validKey:
        if unitKey not in units:
            unit = unit_tuple(0, unitKey, 0.0, 0, 0)
            units[unitKey] = unit
        units[unitKey] = addDataFromCard(units[unitKey], i, card)

def addDataFromCard(unit, idx, card):
    new_idx = unit.idx
    new_avg_interval = unit.avg_interval
    seen_cards_count = unit.seen_cards_count
    unseen_cards_count = unit.unseen_cards_count

    if card.type > 0:
        new_total = (unit.avg_interval * unit.seen_cards_count) + card.ivl
        seen_cards_count = unit.seen_cards_count + 1
        new_avg_interval = new_total / seen_cards_count
    else:
        unseen_cards_count = unit.unseen_cards_count + 1

    if new_idx < unit.idx or unit.idx == 0:
        new_idx = idx

    return unit_tuple(new_idx, unit.value, new_avg_interval, seen_cards_count, unseen_cards_count)

def hsvrgbstr(h, s=0.8, v=0.9):
    def _256(x):
        return round(x * 256)
    r, g, b = hsv_to_rgb(h, s, v)
    return "#%0.2X%0.2X%0.2X" % (_256(r), _256(g), _256(b))

def hex_to_rgb(hex_string):
    try:
        hex_string = hex_string.replace("#", "")
        return int(hex_string[0:2], 16), int(hex_string[2:4], 16), int(hex_string[4:6], 16)
    except Exception:
        return 0, 0, 0

def rgb_to_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"

def get_gradient_color_hex(score, gradient_colors):
    max_color_index = len(gradient_colors) - 1

    starting_color_index = int(score * max_color_index)
    ending_color_index = min(starting_color_index + 1, max_color_index)

    starting_color = gradient_colors[starting_color_index]
    ending_color = gradient_colors[ending_color_index]

    percent = (score * max_color_index) - starting_color_index

    # Linear interpolation
    r1, g1, b1 = hex_to_rgb(starting_color)
    r2, g2, b2 = hex_to_rgb(ending_color)
    r = round(r1 + (r2 - r1) * percent)
    g = round(g1 + (g2 - g1) * percent)
    b = round(b1 + (b2 - b1) * percent)
    return rgb_to_hex(r, g, b)

def get_background_color(avg_interval, config_interval, count, gradient_colors, kanjitileunseencolor, missing=False):
    if count != 0:
        return get_gradient_color_hex(scoreAdjust(avg_interval / config_interval), gradient_colors)
    return kanjitileunseencolor

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

def get_browse_command(char):
    return "javascript:bridgeCommand('" + char + "');"

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

def safe_unicodedata_name(char, default = ""):
    try:
        return unicodedata.name(char)
    except Exception:
        return default

def get_deck_name(mw, config):
    deckname = config.did
    if config.did != "*":
        deckname = mw.col.decks.name(config.did)
    return deckname