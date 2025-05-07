import traceback
import types
from enum import Enum

from aqt import dialogs, mw
from aqt.qt import QApplication, qconnect
from aqt.utils import tooltip
from aqt.webview import AnkiWebView

from . import logger, util


# mimic `AnkiWebViewKind`
# https://github.com/ankitects/anki/blob/1a68c9f5d5bcc197b641fe7405e5d9a4823928f3/qt/aqt/webview.py#L34-L59
class KanjiGridWebViewKind(Enum):
    DEFAULT = "kanjigrid webview"

def init_webview() -> None:
    webview = AnkiWebView()
    try:
        webview.set_kind(KanjiGridWebViewKind.DEFAULT)
    except Exception:  # noqa: BLE001
        logger.error_log("Failed to set webview kind", traceback.format_exc())
    return webview

def open_search_link(wv: AnkiWebView, config: types.SimpleNamespace, char: str) -> None:
    link = util.get_search(config, char)
    # aqt.utils.openLink is an alternative
    wv.eval(f"window.open('{link}', '_blank');")

def open_note_browser(deckname: str, fields_list: list, additional_search_filters: str, search_string: str) -> None:
    fields_string = ""
    for i, field in enumerate(fields_list):
        if i != 0:
            fields_string += " OR "
        fields_string += field + ":*" + search_string + "*"
    if len(fields_list) > 1:
        fields_string = "(" + fields_string + ")"
    browser = dialogs.open("Browser", mw)
    browser.form.searchEdit.lineEdit().setText("deck:\"" + deckname + "\" " + fields_string + " " + additional_search_filters)
    browser.onSearchActivated()

def on_copy_cmd(char: str) -> None:
    QApplication.clipboard().setText(char)

def on_browse_cmd(char: str, config: types.SimpleNamespace, deckname: str) -> None:
    open_note_browser(deckname, config.fieldslist, config.searchfilter, char)

def on_search_cmd(char: str, wv: AnkiWebView, config: types.SimpleNamespace) -> None:
    open_search_link(wv, config, char)

def on_find_cmd(wv: AnkiWebView) -> None:
    char = QApplication.clipboard().text().strip()

    # limit searches to kanji to prevent js injection
    if not util.is_kanji(char):
        # truncate in case there's random garbage in the clipboard
        len_limit = 20
        tooltip_char = char if len(char) <= len_limit else char[:len_limit] + "..."
        tooltip(f"\"{tooltip_char}\" is not valid kanji.")
        return

    def find_text_callback(found: bool) -> None:
        if not found:
          tooltip(f"\"{char}\" not found in grid.")

    # qt's findText impl is bugged and inconvenient, so we use our own
    wv.evalWithCallback(f"findChar('{char}');", find_text_callback)

def add_webview_context_menu_items(wv: AnkiWebView, expected_wv: AnkiWebView, menu, config: types.SimpleNamespace, deckname: str, char: str) -> None:
    # hook is active while kanjigrid is open, and right clicking on the main window (deck list) will also trigger this, so check wv
    if wv is not expected_wv:
      return
    if char != "":
        menu.clear()
        copy_action = menu.addAction(f"Copy {char} to clipboard")
        qconnect(copy_action.triggered, lambda: on_copy_cmd(char))
        browse_action = menu.addAction(f"Browse deck for {char}")
        qconnect(browse_action.triggered, lambda: on_browse_cmd(char, config, deckname))
        search_action = menu.addAction(f"Search online for {char}")
        qconnect(search_action.triggered, lambda: on_search_cmd(char, wv, config))
    else:
        find_action = menu.addAction("Find copied kanji")
        qconnect(find_action.triggered, lambda: on_find_cmd(wv))
