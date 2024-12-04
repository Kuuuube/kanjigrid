from aqt import mw, dialogs
from aqt.qt import qconnect, QApplication
from aqt.utils import tooltip
from aqt.webview import AnkiWebView

from . import util

def open_search_link(wv, config, char):
    link = util.get_search(config, char)
    # aqt.utils.openLink is an alternative
    wv.eval(f"window.open('{link}', '_blank');")

def open_note_browser(deckname, fields_list, additional_search_filters, search_string):
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

def on_copy_cmd(char):
    QApplication.clipboard().setText(char)

def on_browse_cmd(char, config, deckname):
    open_note_browser(deckname, config.fieldslist, config.searchfilter, char)

def on_search_cmd(char, wv, config):
    open_search_link(wv, config, char)

def on_find_cmd(wv: AnkiWebView):
    char = QApplication.clipboard().text().strip()

    # limit searches to kanji to prevent js injection
    if not util.isKanji(char):
        # truncate in case there's random garbage in the clipboard
        LEN_LIMIT = 20
        tooltip_char = char if len(char) <= LEN_LIMIT else char[:LEN_LIMIT] + "..."
        tooltip(f"\"{tooltip_char}\" is not valid kanji.")
        return
    
    def findTextCallback(found):
        if not found:
          tooltip(f"\"{char}\" not found in grid.")
    
    # qt's findText impl is bugged and inconvenient, so we use our own
    wv.evalWithCallback(f"findChar('{char}');", findTextCallback)

def add_webview_context_menu_items(wv, expected_wv, menu, config, deckname, char):
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
