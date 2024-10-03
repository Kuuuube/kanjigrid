#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Upstream: https://github.com/kuuuube/kanjigrid
# AnkiWeb:  https://ankiweb.net/shared/info/1610304449

import operator
import re
import time
import types
import unicodedata
import urllib.parse
import shlex
from functools import reduce

from anki.utils import ids2str
from aqt import mw
from aqt.webview import AnkiWebView
from aqt.qt import (QAction, QSizePolicy, QDialog, QHBoxLayout,
                    QVBoxLayout, QGroupBox, QLabel, QCheckBox, QSpinBox,
                    QComboBox, QPushButton, QLineEdit)

from . import config_util, data, util, save

class KanjiGrid:
    def __init__(self, mw):
        if mw:
            self.menuAction = QAction("Generate Kanji Grid", mw, triggered=self.setup)
            mw.form.menuTools.addSeparator()
            mw.form.menuTools.addAction(self.menuAction)

    def generate(self, config, units):
        def kanjitile(char, bgcolor, count = 0, avg_interval = 0):
            tile = ""
            color = "#000"

            if config.tooltips:
                tooltip = "Character: %s" % unicodedata.name(char)
                if avg_interval:
                    tooltip += " | Avg Interval: " + str("{:.2f}".format(avg_interval)) + " | Score: " + str("{:.2f}".format(util.scoreAdjust(avg_interval / config.interval)))
                tile += "\t<div class=\"grid-item\" style=\"background:%s;\" title=\"%s\">" % (bgcolor, tooltip)
            else:
                tile += "\t<div style=\"background:%s;\">" % (bgcolor)

            if config.copyonclick:
                tile += "<a style=\"color:" + color + ";cursor: pointer;\">" + char + "</a>"
            else:
                tile += "<a href=\"" + util.get_search(config, char) + "\" style=\"color:" + color + ";\">" + char + "</a>"

            tile += "</div>\n"

            return tile

        deckname = "*"
        if config.did != "*":
            deckname = mw.col.decks.name(config.did).rsplit('::', 1)[-1]

        self.html  = "<!doctype html><html lang=\"%s\"><head><meta charset=\"UTF-8\" /><title>Anki Kanji Grid</title>" % config.lang
        self.html += "<style type=\"text/css\">body{text-align:center;}.grid-container{display:grid;grid-gap:2px;grid-template-columns:repeat(auto-fit,23px);justify-content:center;" + util.get_font_css(config) + "}.key{display:inline-block;width:3em}a,a:visited{color:#000;text-decoration:none;}</style>"
        self.html += "</head>\n"
        if config.copyonclick:
            self.html += "<script>function copyText(text) {const range = document.createRange();const tempElem = document.createElement('div');tempElem.textContent = text;document.body.appendChild(tempElem);range.selectNode(tempElem);const selection = window.getSelection();selection.removeAllRanges();selection.addRange(range);document.execCommand('copy');document.body.removeChild(tempElem);}document.addEventListener('click', function(e) {e.preventDefault();if (e.srcElement.tagName == 'A') {copyText(e.srcElement.textContent);}}, false);</script>"
        self.html += "<body>\n"
        self.html += "<div style=\"font-size: 3em;color: #888;\">Kanji Grid - %s</div>\n" % deckname
        self.html += "<p style=\"text-align: center\">Key</p>"
        self.html += "<p style=\"text-align: center\">Weak&nbsp;"
	# keycolors = (hsvrgbstr(n/6.0) for n in range(6+1))
        for c in [n/6.0 for n in range(6+1)]:
            self.html += "<span class=\"key\" style=\"background-color: %s;\">&nbsp;</span>" % util.hsvrgbstr(c/2)
        self.html += "&nbsp;Strong</p></div>\n"
        self.html += "<hr style=\"border-style: dashed;border-color: #666;width: 100%;\">\n"
        self.html += "<div style=\"text-align: center;\">\n"
        if config.groupby >= len(util.SortOrder):
            groups = data.groups[config.groupby - len(util.SortOrder)]
            kanji = [u.value for u in units.values()]
            for i in range(1, len(groups.data)):
                self.html += "<h2 style=\"color:#888;\">%s Kanji</h2>\n" % groups.data[i][0]
                table = "<div class=\"grid-container\">\n"
                count_found = 0
                count_known = 0
                for unit in [units[c] for c in groups.data[i][1] if c in kanji]:
                    if unit.count != 0 or config.unseen:
                        count_found += 1
                        bgcolor = util.get_background_color(unit.avg_interval, config.interval, unit.count, missing = False)
                        if unit.count != 0 or bgcolor not in ["#E62E2E", "#FFF"]:
                            count_known += 1
                        table += kanjitile(unit.value, bgcolor, count_found, unit.avg_interval)
                table += "</div>\n"
                total_count = len(groups.data[i][1])
                if config.unseen:
                    unseen_kanji = []
                    count = 0
                    for char in [c for c in groups.data[i][1] if c not in kanji]:
                        count += 1
                        bgcolor = "#EEE"
                        unseen_kanji.append(kanjitile(char, bgcolor))
                    if count != 0:
                        table += "<details><summary>Missing kanji</summary><div class=\"grid-container\">\n"
                        for element in unseen_kanji:
                            table += element
                    table += "</div></details>\n"
                self.html += "<h4 style=\"color:#888;\">" + str(count_found) + " of " + str(total_count) + " Found - " + "{:.2f}".format(round(count_found / (total_count if total_count > 0 else 1) * 100, 2)) + "%, " + str(count_known) + " of " + str(total_count) + " Known - " + "{:.2f}".format(round(count_known / (total_count if total_count > 0 else 1) * 100, 2)) + "%</h4>\n"
                self.html += table

            chars = reduce(lambda x, y: x+y, dict(groups.data).values())
            self.html += "<h2 style=\"color:#888;\">" + str(groups.data[0][0]) + "</h2>" #label for "not in group" groups
            table = "<div class=\"grid-container\">\n"
            total_count = 0
            count_known = 0
            for unit in [u for u in units.values() if u.value not in chars]:
                if unit.count != 0 or config.unseen:
                    total_count += 1
                    bgcolor = util.get_background_color(unit.avg_interval, config.interval, unit.count, missing = False)
                    if unit.count != 0 or bgcolor not in ["#E62E2E", "#FFF"]:
                        count_known += 1
                    table += kanjitile(unit.value, bgcolor, total_count, unit.avg_interval)
            table += "</div>\n"
            self.html += "<h4 style=\"color:#888;\">" + str(count_known) + " of " + str(total_count) + " Known - " + "{:.2f}".format(round(count_known / (total_count if total_count > 0 else 1) * 100, 2)) + "%</h4>\n"
            self.html += table
            self.html += "<style type=\"text/css\">.datasource{font-style:italic;font-size:0.75em;margin-top:1em;overflow-wrap:break-word;}.datasource a{color:#1034A6;}</style><span class=\"datasource\">Data source: " + ' '.join("<a href=\"{}\">{}</a>".format(w, urllib.parse.unquote(w)) if re.match("https?://", w) else w for w in groups.source.split(' ')) + "</span>"
        else:
            table = "<div class=\"grid-container\">\n"
            unitsList = {
                util.SortOrder.NONE:      sorted(units.values(), key=lambda unit: (unit.idx, unit.count)),
                util.SortOrder.UNICODE:   sorted(units.values(), key=lambda unit: (unicodedata.name(unit.value), unit.count)),
                util.SortOrder.SCORE:     sorted(units.values(), key=lambda unit: (util.scoreAdjust(unit.avg_interval / config.interval), unit.count), reverse=True),
                util.SortOrder.FREQUENCY: sorted(units.values(), key=lambda unit: (unit.count, util.scoreAdjust(unit.avg_interval / config.interval)), reverse=True),
            }[util.SortOrder(config.groupby)]
            total_count = 0
            count_known = 0
            for unit in unitsList:
                if unit.count != 0 or config.unseen:
                    total_count += 1
                    bgcolor = util.get_background_color(unit.avg_interval,config.interval, unit.count)
                    if unit.count != 0 or bgcolor not in ["#E62E2E", "#FFF"]:
                        count_known += 1
                    table += kanjitile(unit.value, bgcolor, total_count, unit.avg_interval)
            table += "</div>\n"
            if total_count != 0:
                self.html += "<h4 style=\"color:#888;\">" + str(count_known) + " of " + str(total_count) + " Known - " + "{:.2f}".format(round(count_known / (total_count if total_count > 0 else 1) * 100, 2)) + "%</h4>\n"
            else:
                self.html += "<h4 style=\"color:#888;\">" + str(count_known) + " of " + str(total_count) + " Known - 0%</h4>\n"
            self.html += table
        self.html += "</div></body></html>\n"

    def displaygrid(self, config, deckname, units):
        self.generate(config, units)
        self.timepoint("HTML generated")
        self.win = QDialog(mw)
        self.wv = AnkiWebView()
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.wv)
        self.wv.stdHtml(self.html)
        hl = QHBoxLayout()
        vl.addLayout(hl)
        save_html = QPushButton("Save HTML", clicked=lambda: save.savehtml(self, mw, config, deckname))
        hl.addWidget(save_html)
        same_image = QPushButton("Save Image", clicked=lambda: save.savepng(self, mw, config, deckname))
        hl.addWidget(same_image)
        save_pdf = QPushButton("Save PDF", clicked=lambda: save.savepdf(self, mw, deckname))
        hl.addWidget(save_pdf)
        save_json = QPushButton("Save JSON", clicked=lambda: save.savejson(self, mw, config, deckname, units))
        hl.addWidget(save_json)
        save_txt = QPushButton("Save TXT", clicked=lambda: save.savetxt(self, mw, config, deckname, units))
        hl.addWidget(save_txt)
        bb = QPushButton("Close", clicked=self.win.reject)
        hl.addWidget(bb)
        self.win.setLayout(vl)
        self.win.resize(1000, 800)
        self.timepoint("Window complete")
        return 0

    def kanjigrid(self, config):
        dids = [config.did]
        if config.did == "*":
            dids = mw.col.decks.all_ids()
        for deck_id in dids:
            for _, id_ in mw.col.decks.children(int(deck_id)):
                dids.append(id_)
        self.timepoint("Decks selected")
        cids = []
        #mw.col.find_cards and mw.col.db.list sort differently
        #mw.col.db.list is kept due to some users being very picky about the order of kanji when using `Group by: None, sorted by order found`
        if len(config.searchfilter) > 0 and len(config.pattern) > 0 and len(dids) > 0:
            cids = mw.col.find_cards("(" + util.make_query(dids, config.pattern) + ") " + config.searchfilter)
        else:
            cids = mw.col.db.list("select id from cards where did in %s or odid in %s" % (ids2str(dids), ids2str(dids)))
        self.timepoint("Cards selected")

        units = dict()
        notes = dict()
        for i in cids:
            card = mw.col.get_card(i)
            if card.nid not in notes.keys():
                keys = card.note().keys()
                unitKey = set()
                matches = operator.eq
                for keyword in config.pattern:
                    for key in keys:
                        if matches(key.lower(), keyword):
                            unitKey.update(set(card.note()[key]))
                            break
                notes[card.nid] = unitKey
            else:
                unitKey = notes[card.nid]
            if unitKey is not None:
                for ch in unitKey:
                    util.addUnitData(units, ch, i, card, config.kanjionly)
        self.timepoint("Units created")
        return units

    def makegrid(self, config):
        self.time = time.time()
        self.timepoint("Start")
        units = self.kanjigrid(config)
        deckname = config.did
        if config.did != "*":
            deckname = mw.col.decks.name(config.did)
        if units is not None:
            self.displaygrid(config, deckname, units)

    def setup(self):
        addonconfig = mw.addonManager.getConfig(__name__)
        validated_config = config_util.validate_config(addonconfig["defaults"])
        config = types.SimpleNamespace(**validated_config)
        if addonconfig.get("_debug_time", False):
            self.timepoint = lambda c: print("%s: %0.3f" % (c, time.time()-self.time))
        else:
            self.timepoint = lambda _: None
        config.did = mw.col.conf['curDeck']

        swin = QDialog(mw)
        vl = QVBoxLayout()
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
        vl.addLayout(fl)
        frm = QGroupBox("Settings")
        vl.addWidget(frm)
        il = QVBoxLayout()
        fl = QHBoxLayout()
        il.addWidget(QLabel("Field: "))
        field = QComboBox()
        field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        def update_fields_dropdown(deckname):
            if config.pattern != "":
                field.setCurrentText(config.pattern)
                return
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
            *("None, sorted by " + x.pretty_value() for x in util.SortOrder),
            *(x.name for x in data.groups),
        ])
        groupby.setCurrentIndex(config.groupby)
        il.addWidget(QLabel("Group by:"))
        il.addWidget(groupby)

        pagelang = QComboBox()
        pagelang.addItems(["ja", "zh","zh-Hans", "zh-Hant", "ko", "vi"])
        def update_pagelang_dropdown():
            index = groupby.currentIndex() - 4
            if index > 0:
                pagelang.setCurrentText(data.groups[groupby.currentIndex() - 4].lang)
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
        vl.addLayout(hl)
        gen = QPushButton("Generate", clicked=swin.accept)
        hl.addWidget(gen)
        cls = QPushButton("Close", clicked=swin.reject)
        hl.addWidget(cls)
        swin.setLayout(vl)
        swin.setTabOrder(gen, cls)
        swin.setTabOrder(cls, field)
        swin.setTabOrder(stint, groupby)
        swin.setTabOrder(groupby, shnew)
        swin.resize(500, swin.height())
        if swin.exec():
            mw.progress.start(immediate=True)
            config.pattern = field.currentText().lower()
            config.pattern = shlex.split(config.pattern)
            config.searchfilter = search_filter.text()
            config.interval = stint.value()
            config.groupby = groupby.currentIndex()
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
