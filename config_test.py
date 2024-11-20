import json
import difflib

import config_util

config_v0 = json.load(open("./tests/config_v0.json", "r"))
config_current = json.load(open("./config.json", "r"))

config_migrated = config_util.migrate_config(config_v0)

config_migrated_string = json.dumps(config_migrated, sort_keys = True, indent = 4)
config_current_string = json.dumps(config_current, sort_keys = True, indent = 4)

if config_migrated_string == config_current_string:
    print("Config test passed")
else:
    print("Config test failed")

    diff = difflib.unified_diff(config_current_string.split("\n"), config_migrated_string.split("\n"), fromfile="expected", tofile="result")
    for line in diff:
        print(line)
