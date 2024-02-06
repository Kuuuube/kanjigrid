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
    "jafontcss": "font-family: \"ヒラギノ角ゴ Pro W3\", \"Hiragino Kaku Gothic Pro\", Osaka, \"メイリオ\", Meiryo, \"ＭＳ Ｐゴシック\", \"MS PGothic\", \"MS UI Gothic\", Mincho, sans-serif;",
    "zhfontcss": "",
    "zhhansfontcss": "",
    "zhhantfontcss": "",
    "kofontcss": "",
    "vifontcss": "",
    "jasearch": "https://jisho.org/search/%s %23kanji",
    "zhsearch": "",
    "zhhanssearch": "",
    "zhhantsearch": "",
    "kosearch": "",
    "visearch": ""
}

def validate_config(config):
    for config_schema_key in config_schema.keys():
        if config_schema_key in config.keys():
            if type(config_schema[config_schema_key]) == type(config[config_schema_key]):
                continue
        config[config_schema_key] = config_schema[config_schema_key]
    return config
