# Kanji Grid Kuuube

Kanji Grid for Anki 23.10+ with improvements and bug fixes.

![](https://raw.githubusercontent.com/Kuuuube/kanjigrid/master/kanji_grid_banner.png)

## Installation

1. Open Anki.

2. On the top menu, go to `Tools` > `Add-ons`.

3. Click `Get Add-ons...`.

4. Input `1610304449`.

5. Click `OK`.

6. Restart Anki.

## Usage

1. On the top menu, go to `Tools` > `Generate Kanji Grid`.

2. Select the deck to generate from with the `Deck` dropdown.

3. Select the card field to check for kanji with the `Field` dropdown or type in multiple fields to check.

    Use the following format for searching multiple fields: `field1 field2 "field with spaces"`.

4. Optionally, edit any of the other settings to your liking.

5. Click `Generate`.

## Known Issues

- On Linux, some users have experienced issues with crashing when generating the grid. If this happens, try changing Anki to `Vulkan` or `Software` renderer.

    `Tools` > `Preferences` > `Appearance` > `Video driver` > `Vulkan` or `Software`

## Config Values

- `pattern` The default text in the `Field` dropdown box. Controls which field(s) to look for kanji in. Defaults to the first field of the selected deck if no value is found.

- `interval` The default text in the `Card interval considered strong` box. Sets the interval for cards to be given the Strong color on the grid.

- `groupby` The default setting in the `Group by` dropdown. The first dropdown item is number 0.

- `sortby` The default setting in the `Sort by` dropdown. The first dropdown item is number 0.

- `lang` The default setting in the `Language` dropdown. This controls fontcss and search options.

- `unseen` Whether or not to display kanji that has not been viewed yet in the deck.

- `tooltips` Whether or not to display tooltips when hovering over kanji in the grid.

- `kanjionly` Whether or not to only show kanji in the grid.

- `saveimagequality` The quality to save the grid at when seleting `Save Image` on the grid. Accepted values are 0-5. WARNING: On large grids using anything except `1` may crash anki.

- `copyonclick` Copies kanji when clicked on instead of searching in a web browser or note browser.

- `browseonclick` Opens the Anki note browser when clicking on kanji instead of searching in a web browser.

- `saveimagedelay` The delay in ms to wait when resizing the image if `saveimagequality` is not 1. Setting this to a higher value may help mitigate crashes.

- `jafontcss` `zhfontcss` `zhhansfontcss` `zhhantfontcss` `kofontcss` `vifontcss` The css to apply to the grid for the respective language. This is intended to be used for fonts but accepts all css. For fonts, use the following syntax: `font-family:%s;`. Replace `%s` with your fonts list.

- `jasearch` `zhsearch` `zhhanssearch` `zhhantsearch` `kosearch` `visearch` The search option to provide for the respective language. Use `%s` to define the kanji's position in the search string.

- `searchfilter` The default setting for `Additional Search Filters`. This is appended to the existing filtering and must use the same format as [Anki's Browser Searching](https://docs.ankiweb.net/searching.html).

## Improvements and Bug Fixes

Changelog compared to the old kanji grid add-on.

<details>
<summary>Improvements</summary>

### UI/UX

- Field selector now uses a dropdown/text box combo instead of a text box.

    The default field value can be overwritten by setting `pattern` in `config.json`.

- All decks can be searched at once by selecting `*` in the deck dropdown.

- Key and key label are now centered.

- Kanji grid and header line now fill the entire window width.

- Background color is no longer hardcoded and will adapt to your Anki theme.

- Default window size is larger to better fit modern display resolutions.

- Kanji are rendered in a dynamic grid that will adapt to window size instead of a static table.

- Automatically set language tag based on grouping and manual language tag setting.

- Added better counts and percentages to grids.

### Config and Options

- Config validation and safer loading to help prevent crashes.

- Added option to copy kanji on click instead of searching in a web browser.

- Added option to search in the Anki note browser instead of a web browser when clicking on kanji.

- Added option for Additional Search Filters.

- Option to set custom fonts per language setting.

- Search option when clicking on a kanji is customizeable for each language.

- Added option to sort within groupings.

### Groupings

- Chinese character groupings can be selected.

- Added Basic Kanji Book (BKB) V1 & V2 grouping.

- Added JPDB Kanji Frequency List grouping.

- Added The Kodansha Kanji Learner's Course (KLC) grouping.

- Added JIS Levels grouping.

- Renamed `Probably Chinese` Kanji Kentei Level sort category to `Non-Kanji Kentei`.

- Removed `Missing Kanji` in groupings when there are no missing kanji.

### Exporting

- Added option to save Kanji Grid as JSON.

- `Save Image` saves the entire page instead of only the visible portion.

- `Save Image` can optionally save at up to 5x the displayed quality. Configurable in `config.json` with the `saveimagequality` setting.

    WARNING: On extremely large kanji grids this can cause anki to crash. Consider saving as a PDF for higher quality instead if that is an issue.

- Added option to save Kanji Grid as PDF.

- Filename is autofilled with deck name and date when saving.

- Added option to save all kanji as TXT.

</details>

<details>
<summary>Bug Fixes</summary>

- `Save HTML` and `Save Image` now properly function.

- Fields with spaces in their name are now properly searchable.

- Fixed divide by zero error when no kanji are found and a kanji grouping is selected.

- Fixed JLPT kanji lists missing some characters.

- Added missing characters (mostly kyujitai) to Kanji Kentei Levels.

</details>

## Info

[Github Repository](https://github.com/Kuuuube/kanjigrid)

[Report Issues Here](https://github.com/Kuuuube/kanjigrid/issues)
