import collections
import enum
import re
import types
import unicodedata

unit_tuple = collections.namedtuple("unit", "idx value avg_interval seen_cards_count unseen_cards_count")

class SortOrder(enum.Enum):
    NONE = 0
    UNICODE = 1
    SCORE = 2
    SEEN_CARDS_COUNT = 3
    UNSEEN_CARDS_COUNT = 4

    def pretty_value(self) -> str:
        return (
            "none",
            "unicode order",
            "score",
            "seen cards count",
            "unseen cards count",
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
def is_kanji(unichar: str) -> bool:
    return bool(cjk_re.match(safe_unicodedata_name(unichar)))

def score_adjust(score: float) -> float:
    score += 1
    return 1 - 1 / (score * score)

def add_unit_data(units, unit_key, i, card, kanjionly) -> None:
    valid_key = ignored_characters.find(unit_key) == -1 and (not kanjionly or is_kanji(unit_key))
    if valid_key:
        if unit_key not in units:
            unit = unit_tuple(0, unit_key, 0.0, 0, 0)
            units[unit_key] = unit
        units[unit_key] = add_data_from_card(units[unit_key], i, card)

def add_data_from_card(unit, idx, card):
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

def hex_to_rgb(hex_string: str) -> (int, int, int):
    try:
        hex_string = hex_string.replace("#", "")
        return int(hex_string[0:2], 16), int(hex_string[2:4], 16), int(hex_string[4:6], 16)
    except Exception:  # noqa: BLE001
        return 0, 0, 0

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"

def get_gradient_color_hex(score, gradient_colors) -> str:
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

def get_background_color(avg_interval, config_interval, count, gradient_colors, kanjitileunseencolor) -> str:
    if count != 0:
        return get_gradient_color_hex(score_adjust(avg_interval / config_interval), gradient_colors)
    return kanjitileunseencolor

def get_font_css(config: types.SimpleNamespace) -> str:
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
    return ""

def get_search(config: types.SimpleNamespace, char: str) -> str:
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

def get_browse_command(char: str) -> str:
    return "javascript:bridgeCommand('" + char + "');"

def fields_to_query(fields: list) -> str:
    query_strings = []
    for field in fields:
        query_strings.append("\"" + str(field) + ":*\"")
    return " OR ".join(query_strings)

def make_query(deck_ids: list, fields: list) -> str:
    query_strings = []
    fields_string = fields_to_query(fields)
    for deck_id in deck_ids:
        query_strings.append("(did:" + str(deck_id) + " AND (" + fields_string + "))")

    return " OR ".join(query_strings)

def safe_unicodedata_name(char: str, default: str = "") -> str:
    try:
        return unicodedata.name(char)
    except Exception:  # noqa: BLE001
        return default

def get_deck_name(mw, config: types.SimpleNamespace) -> str:
    deckname = config.did
    if config.did != "*":
        deckname = mw.col.decks.name(config.did)
    return deckname

def truncate_text(text: str, length: int) -> str:
    new_text = text[:length - 3]
    if len(new_text) != len(text):
        return new_text + "..."
    return text
