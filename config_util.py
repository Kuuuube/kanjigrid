config_schema = {
    "pattern": "",
    "literal": False,
    "interval": 180,
    "groupby": 2,
    "lang": "ja",
    "unseen": True,
    "tooltips": True,
    "kanjionly": True,
    "saveimagequality": 1,
    "saveimagedelay": 1000,
    "copyonclick": False,
    "jafontcss": "font-family: \"ヒラギノ角ゴ Pro W3\", \"Hiragino Kaku Gothic Pro\", Osaka, \"メイリオ\", Meiryo, \"ＭＳ Ｐゴシック\", \"MS PGothic\", \"MS UI Gothic\", Mincho, sans-serif;",
    "zhfontcss": "font-family: PingFang SC, Hiragino Sans GB, \"Microsoft YaHei New\", \"Microsoft Yahei\", \"微软雅黑\", 宋体, SimSun, STXihei, \"华文细黑\", sans-serif;",
    "zhhansfontcss": "font-family: PingFang SC, Hiragino Sans GB, \"Microsoft YaHei New\", \"Microsoft Yahei\", \"微软雅黑\", 宋体, SimSun, STXihei, \"华文细黑\", sans-serif;",
    "zhhantfontcss": "font-family: \"微軟正黑體\", \"Microsoft JhengHei\", \"Microsoft JhengHei UI\", \"微軟雅黑\", \"Microsoft YaHei\", \"Microsoft YaHei UI\", sans-serif;",
    "kofontcss": "font-family: \"Nanum Barun Gothic\", \"New Gulim\", \"새굴림\", \"애플 고딕\", \"맑은 고딕\", \"Malgun Gothic\", Dotum, \"돋움\", \"Noto Sans CJK KR\", \"Noto Sans CJK TC\", \"Noto Sans KR\", \"Noto Sans TC\", sans-serif;",
    "vifontcss": "font-family: \"Han-Nom Gothic\", \"Han Nom Gothic\", sans-serif;",
    "jasearch": "https://jisho.org/search/%s %23kanji",
    "zhsearch": "",
    "zhhanssearch": "",
    "zhhantsearch": "",
    "kosearch": "",
    "visearch": "",
    "searchfilter": ""
}

def validate_config(config):
    for config_schema_key in config_schema.keys():
        if config_schema_key in config.keys():
            if type(config_schema[config_schema_key]) is type(config[config_schema_key]):
                continue
        config[config_schema_key] = config_schema[config_schema_key]
    return config
