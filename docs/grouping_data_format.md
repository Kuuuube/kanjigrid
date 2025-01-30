# Grouping Data Format

Groupings use JSON format. [View the schema here](../tests/data_schema.json).

## Grouping Fields

### `version`

This is used by Kanji Grid to determine the data format version. If `version` is lower than the latest version, Kanji Grid will migrate it to the latest version on load.

When creating a new grouping, always use the latest value specified in the schema. It is defined under `version` as `const` in the schema.

### `name`

The name of the grouping.

- Displayed in the `Group by` dropdown.

### `lang`

The target language of the grouping's data. Use the `ISO 639-1` language code.

- Displayed in the `Group by` dropdown before the grouping's name.

- Sets the language attribute in the html.

- Determines which font css is injected.

- Determines which search url to use if the user has `onclickaction` set to `search`.

### `source`

Attribution list for sources used to compile or create the grouping data.

- Displayed at the bottom of the page when it is rendered.

### `leftover_group`

Name of the group to put characters in that do not fit in any of the grouping's defined groups.

- Displayed below all other groups.

### `Groups`

Array of group objects. A group object consists of two strings: `name` and `characters`.

- `name`: The name of the grouping.

- `characters`: A single string of all characters in the grouping.

## Minimal Example

### Version 1

```json
{
    "version": 1,
    "name": "Minimal Example Kanji Grouping",
    "lang": "ja",
    "source": "https://github.com/Kuuuube/kanjigrid",
    "leftover_group": "Not in Minimal Example Kanji Grouping",
    "groups": [
        {
            "name": "Kanji Grouping 1",
            "characters": "一二三"
        },
        {
            "name": "Kanji Grouping 2",
            "characters": "四五六"
        }
    ]
}
```

## Older Examples

**Do not use these versions if you are creating a new grid. They are provided purely for reference.**

### Version 0

```json
{
    "name": "Minimal Example Kanji Grouping",
    "source": "https://github.com/Kuuuube/kanjigrid",
    "lang": "ja",
    "data": [
        [
            "Not in Minimal Example Kanji Grouping",
            ""
        ],
        [
            "Kanji Grouping 1",
            "一二三"
        ],
        [
            "Kanji Grouping 2",
            "四五六"
        ]
    ]
}
```
