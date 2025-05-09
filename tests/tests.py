import sys
# add src folder to path to allow accessing module there
sys.path.append(sys.path[0] + "/../src/.")

JSON_DATA_FOLDER = "./data"

def test_config_update():
    import json

    import config_util

    config_v0 = json.load(open("./tests/config_v0.json", "r"))
    config_current = json.load(open("./src/config.json", "r"))

    config_migrated = config_util.migrate_config(config_v0)
    config_validated = config_util.validate_config(config_migrated)

    config_migrated_validated_string = json.dumps(config_validated, sort_keys = True, indent = 4)
    config_current_string = json.dumps(config_current, sort_keys = True, indent = 4)

    assert(config_migrated_validated_string == config_current_string)

def test_data_load():
    import data
    data.load_from_folder(data.groupings, JSON_DATA_FOLDER)

def test_data_schema():
    import jsonschema
    import json
    import os

    data_schema = json.load(open("./tests/data_schema.json", "r", encoding = "UTF8"))

    for file in os.listdir(JSON_DATA_FOLDER):
        filepath = JSON_DATA_FOLDER + "/" + file
        data_json = json.load(open(filepath, "r", encoding = "UTF8"))
        jsonschema.validate(instance = data_json, schema = data_schema)

def test_data_group_duplicates():
    import json
    import os

    for file in os.listdir(JSON_DATA_FOLDER):
        filepath = JSON_DATA_FOLDER + "/" + file
        data_json = json.load(open(filepath, "r", encoding = "UTF8"))
        for grouping_data in data_json["groups"]:
            kanji_list = sorted(list(grouping_data["characters"]))
            kanji_list_deduped = sorted(list(set(kanji_list)))

            assert((filepath, kanji_list) == (filepath, kanji_list_deduped))

def test_data_format():
    import json
    import os

    for file in os.listdir(JSON_DATA_FOLDER):
        filepath = JSON_DATA_FOLDER + "/" + file
        data_file_str = open(filepath, "r", encoding = "UTF8").read()
        data_json = json.loads(data_file_str)
        formatted_json_string = json.dumps(data_json, indent = 4, ensure_ascii = False)

        assert(formatted_json_string == data_file_str)

def test_data_contains_only_cjk_characters():
    import json
    import os

    import util

    for file in os.listdir(JSON_DATA_FOLDER):
        filepath = JSON_DATA_FOLDER + "/" + file
        data_json = json.load(open(filepath, "r", encoding = "UTF8"))
        for grouping_data in data_json["groups"]:
            kanji_list = grouping_data["characters"]
            for kanji in kanji_list:
                assert(util.is_kanji(kanji)), (filepath, kanji)

def test_data_update():
    import json
    import jsonschema
    import data

    data_schema = json.load(open("./tests/data_schema.json", "r", encoding = "UTF8"))

    data_v0 = json.load(open("./tests/data_v0.json", "r", encoding = "UTF8"))
    data_current = json.load(open("./tests/data_current.json", "r", encoding = "UTF8"))
    data_migrated = data.migrate_grouping(data_v0)

    jsonschema.validate(instance = data_migrated, schema = data_schema)
    jsonschema.validate(instance = data_current, schema = data_schema)

    assert(data_migrated == data_current)
