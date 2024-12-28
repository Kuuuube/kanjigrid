config_schema = {
    "version": {
        "default": 1,
    },
    "pattern": {
        "default": "",
    },
    "literal": {
        "default": False,
    },
    "interval": {
        "default": 180,
    },
    "groupby": {
        "default": 0,
    },
    "sortby": {
        "default": 2,
        "enum": range(0, 4)
    },
    "lang": {
        "default": "ja",
    },
    "unseen": {
        "default": True,
    },
    "tooltips": {
        "default": True,
    },
    "kanjionly": {
        "default": True,
    },
    "saveimagequality": {
        "default": 1,
    },
    "saveimagedelay": {
        "default": 1000,
    },
    "onclickaction": {
        "default": "browse",
        "enum": ["", "browse", "copy", "search"],
    },
    "jafontcss": {
        "default": "font-family: \"ヒラギノ角ゴ Pro W3\", \"Hiragino Kaku Gothic Pro\", Osaka, \"メイリオ\", Meiryo, \"ＭＳ Ｐゴシック\", \"MS PGothic\", \"MS UI Gothic\", Mincho, sans-serif;",
    },
    "zhfontcss": {
        "default": "font-family: PingFang SC, Hiragino Sans GB, \"Microsoft YaHei New\", \"Microsoft Yahei\", \"微软雅黑\", 宋体, SimSun, STXihei, \"华文细黑\", sans-serif;",
    },
    "zhhansfontcss": {
        "default": "font-family: PingFang SC, Hiragino Sans GB, \"Microsoft YaHei New\", \"Microsoft Yahei\", \"微软雅黑\", 宋体, SimSun, STXihei, \"华文细黑\", sans-serif;",
    },
    "zhhantfontcss": {
        "default": "font-family: \"微軟正黑體\", \"Microsoft JhengHei\", \"Microsoft JhengHei UI\", \"微軟雅黑\", \"Microsoft YaHei\", \"Microsoft YaHei UI\", sans-serif;",
    },
    "kofontcss": {
        "default": "font-family: \"Nanum Barun Gothic\", \"New Gulim\", \"새굴림\", \"애플 고딕\", \"맑은 고딕\", \"Malgun Gothic\", Dotum, \"돋움\", \"Noto Sans CJK KR\", \"Noto Sans CJK TC\", \"Noto Sans KR\", \"Noto Sans TC\", sans-serif;",
    },
    "vifontcss": {
        "default": "font-family: \"Han-Nom Gothic\", \"Han Nom Gothic\", sans-serif;",
    },
    "jasearch": {
        "default": "https://jisho.org/search/%s %23kanji",
    },
    "zhsearch": {
        "default": "",
    },
    "zhhanssearch": {
        "default": "",
    },
    "zhhantsearch": {
        "default": "",
    },
    "kosearch": {
        "default": "",
    },
    "visearch": {
        "default": "",
    },
    "searchfilter": {
        "default": ""
    },
}

def set_config(mw, namespace_config):
    config = dict(namespace_config.__dict__)
    for key in list(config.keys()):
        if key not in config_schema.keys():
            del config[key]
    mw.addonManager.writeConfig(__name__, config)

def get_config(mw):
    config = mw.addonManager.getConfig(__name__)

    if "defaults" in config: #migrate legacy configs that nested settings inside "defaults"
        config = config["defaults"]
        mw.addonManager.writeConfig(__name__, config)

    if config_schema["version"]["default"] > config["version"]:
        config = migrate_config(config)
        mw.addonManager.writeConfig(__name__, config)

    return validate_config(config)

def reset_config(mw):
    default_config = dict(map(lambda item: (item[0], item[1]["default"]), config_schema.items()))
    mw.addonManager.writeConfig(__name__, default_config)

def validate_config(config):
    for config_schema_key in config_schema.keys():
        if config_schema_key in config.keys():
            if type(config_schema[config_schema_key]["default"]) is type(config[config_schema_key]):
                if "enum" in config_schema[config_schema_key]:
                    if config[config_schema_key] in config_schema[config_schema_key]["enum"]:
                        continue
                else:
                    continue
        config[config_schema_key] = config_schema[config_schema_key]["default"]
    return config

def migrate_config(config):
    config_updates = [config_update_1]
    if len(config_updates) > config["version"]:
        for config_update in config_updates[config["version"]:]:
            config = config_update(config)
        config["version"] = config_schema["version"]["default"]
    return config

def config_update_1(config):
    if "browseonclick" in config and "copyonclick" in config:
        if not config["browseonclick"] and not config["copyonclick"]:
            config["onclickaction"] = "search"
        elif config["copyonclick"]:
            config["onclickaction"] = "copy"
        else:
            config["onclickaction"] = "browse"

        del config["browseonclick"]
        del config["copyonclick"]
    return config
