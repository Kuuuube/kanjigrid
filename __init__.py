#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Upstream: https://github.com/kuuuube/kanjigrid
# AnkiWeb:  https://ankiweb.net/shared/info/1610304449

import types
import shlex

from aqt import mw, gui_hooks
from aqt.webview import AnkiWebView
from aqt.qt import (QAction, QSizePolicy, QDialog, QHBoxLayout,
                    QVBoxLayout, QGroupBox, QLabel, QCheckBox, QSpinBox,
                    QComboBox, QPushButton, QLineEdit, Qt, qconnect)

from . import config_util, data, util, save, generate_grid, webview_util

class KanjiGrid:
    def __init__(self, mw):
        if mw:
            self.menuAction = QAction("Generate Kanji Grid", mw, triggered=self.setup)
            mw.form.menuTools.addSeparator()
            mw.form.menuTools.addAction(self.menuAction)

    def link_handler(self, link, config, deckname):
        link_prefix = link[:2]
        link_suffix = link[2:]
        if link_prefix == "h:":
            self.hovered = link_suffix
        elif link_prefix == "l:":
            if link_suffix == self.hovered:
                # clear when outside grid
                self.hovered = ""
        else:
            webview_util.on_browse_cmd(link, config, deckname)

    def displaygrid(self, config, deckname, units):
        generated_html = generate_grid.generate(mw, config, units)
        self.win = QDialog(mw, Qt.WindowType.Window)
        current_win = self.win
        self.wv = AnkiWebView()
        current_wv = self.wv

        def on_window_close(current_wv):
            current_wv.cleanup()
            gui_hooks.webview_will_show_context_menu.remove(webview_util.add_webview_context_menu_items)
        qconnect(current_win.finished, lambda _: on_window_close(current_wv))
        mw.garbage_collect_on_dialog_finish(current_win)

        self.hovered = ""
        current_wv.set_bridge_command(lambda link: self.link_handler(link, config, deckname), None)
        # add webview context menu hook and defer cleanup (in on_window_close)
        gui_hooks.webview_will_show_context_menu.append(lambda wv, menu: webview_util.add_webview_context_menu_items(wv, current_wv, menu, config, deckname, self.hovered))

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(current_wv)
        current_wv.stdHtml(generated_html)
        hl = QHBoxLayout()
        vl.addLayout(hl)
        save_html = QPushButton("Save HTML", clicked=lambda: save.savehtml(mw, current_win, config, deckname))
        hl.addWidget(save_html)
        same_image = QPushButton("Save Image", clicked=lambda: save.savepng(current_wv, current_win, config, deckname))
        hl.addWidget(same_image)
        save_pdf = QPushButton("Save PDF", clicked=lambda: save.savepdf(mw, current_wv, current_win, deckname))
        hl.addWidget(save_pdf)
        save_json = QPushButton("Save JSON", clicked=lambda: save.savejson(mw, current_win, config, deckname, units))
        hl.addWidget(save_json)
        save_txt = QPushButton("Save TXT", clicked=lambda: save.savetxt(mw, current_win, config, deckname, units))
        hl.addWidget(save_txt)
        bb = QPushButton("Close", clicked=current_win.reject)
        hl.addWidget(bb)
        current_win.setLayout(vl)
        current_win.resize(1000, 800)

    def makegrid(self, config):
        units = generate_grid.kanjigrid(mw, config)
        deckname = config.did
        if config.did != "*":
            deckname = mw.col.decks.name(config.did)
        if units is not None:
            self.displaygrid(config, deckname, units)

    def setup(self):
        config = types.SimpleNamespace(**config_util.get_config())
        config.did = mw.col.conf['curDeck']

        data.init_groups()

        setup_win = QDialog(mw)
        vertical_layout = QVBoxLayout()
        fl = QHBoxLayout()
        deckcb = QComboBox()
        deckcb.addItem("*") # * = all decks
        deckcb.addItems(sorted(mw.col.decks.all_names()))
        deckcb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        fl.addWidget(QLabel("Deck: "))
        deckcb.setCurrentText(mw.col.decks.get(config.did)['name'])
        def change_did(deckname):
            if deckname == "*":
                config.did = "*"
                return
            config.did = mw.col.decks.by_name(deckname)['id']
        deckcb.currentTextChanged.connect(change_did)
        fl.addWidget(deckcb)
        vertical_layout.addLayout(fl)
        frm = QGroupBox("Settings")
        vl.addWidget(frm)
        il = QVBoxLayout()
        fl = QHBoxLayout()
        il.addWidget(QLabel("Field: "))
        field = QComboBox()
        field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        def update_fields_dropdown(deckname):
            if deckname != "*":
                deckname = mw.col.decks.get(config.did)['name']
            new_text = set()
            field_names = []
            for item in mw.col.models.all_names_and_ids():
                model_id_name = str(item).replace("id: ", "").replace("name: ", "").replace("\"", "").split("\n")
                # Anki backend will return incorrectly escaped strings that need to be stripped of `\`. However, `"`, `*`, and `_` should not be stripped
                model_name = model_id_name[1].replace("\\", "").replace("*", "\\*").replace("_", "\\_").replace("\"", "\\\"")
                if len(mw.col.find_cards("\"note:" + model_name + "\" " + "\"deck:" + deckname + "\"")) > 0:
                    model_id = model_id_name[0]
                    model_fields = mw.col.models.get(model_id)['flds']
                    for field_dict in model_fields:
                        field_dict_name = field_dict['name']
                        if len(field_dict_name.split()) > 1:
                            field_dict_name = "\"" + field_dict_name + "\""
                        field_names.append(field_dict_name)

                    if len(model_fields) > 0:
                        first_field_name = model_fields[0]['name']
                        if len(first_field_name.split()) > 1:
                            first_field_name = "\"" + first_field_name + "\""
                        new_text.add(first_field_name)
            field.clear()
            field.addItems(field_names)
            if config.pattern != "":
                field.setCurrentText(config.pattern)
            else:
                field.setCurrentText(" ".join(new_text))
        field.setEditable(True)
        deckcb.currentTextChanged.connect(update_fields_dropdown)
        update_fields_dropdown(config.did)
        fl.addWidget(field)
        il.addLayout(fl)
        stint = QSpinBox()
        stint.setRange(1, 65536)
        stint.setValue(config.interval)
        il.addWidget(QLabel("Card interval considered strong:"))
        il.addWidget(stint)

        groupby = QComboBox()
        groupby.addItems([
            "None",
            *(x.name for x in data.groups),
        ])
        groupby.setCurrentIndex(config.groupby)
        il.addWidget(QLabel("Group by:"))
        il.addWidget(groupby)

        sortby = QComboBox()
        sortby.addItems([
            *(x.pretty_value().capitalize() for x in util.SortOrder)
        ])
        sortby.setCurrentIndex(config.sortby)
        il.addWidget(QLabel("Sort by:"))
        il.addWidget(sortby)

        pagelang = QComboBox()
        pagelang.addItems(["ja", "zh","zh-Hans", "zh-Hant", "ko", "vi"])
        def update_pagelang_dropdown():
            index = groupby.currentIndex() - 1
            if index > 0:
                pagelang.setCurrentText(data.groups[index].lang)
        groupby.currentTextChanged.connect(update_pagelang_dropdown)
        pagelang.setCurrentText(config.lang)
        il.addWidget(QLabel("Language:"))
        il.addWidget(pagelang)

        search_filter = QLineEdit()
        search_filter.setText(config.searchfilter)
        search_filter.setPlaceholderText("e.g. \"is:new\" or \"tag:mining_deck\"")
        il.addWidget(QLabel("Additional Search Filters:"))
        il.addWidget(search_filter)

        shnew = QCheckBox("Show units not yet seen")
        shnew.setChecked(config.unseen)
        il.addWidget(shnew)
        frm.setLayout(il)
        hl = QHBoxLayout()
        vertical_layout.addLayout(hl)
        gen = QPushButton("Generate", clicked = setup_win.accept)
        hl.addWidget(gen)
        cls = QPushButton("Close", clicked = setup_win.reject)
        hl.addWidget(cls)
        setup_win.setLayout(vertical_layout)
        setup_win.resize(500, setup_win.height())
        if setup_win.exec():
            mw.progress.start(immediate=True)
            config.pattern = field.currentText().lower()
            config.pattern = shlex.split(config.pattern)
            config.searchfilter = search_filter.text()
            config.interval = stint.value()
            config.groupby = groupby.currentIndex()
            config.sortby = sortby.currentIndex()
            config.lang = pagelang.currentText()
            config.unseen = shnew.isChecked()
            self.makegrid(config)
            mw.progress.finish()
            self.win.show()

if __name__ != "__main__":
    # Save a reference to the toolkit onto the mw, preventing garbage collection of PyQt objects
    if mw:
        mw.kanjigrid = KanjiGrid(mw)
else:
    print("This is an addon for the Anki spaced repetition learning system and cannot be run directly.")
    print("Please download Anki from <https://apps.ankiweb.net/>")
