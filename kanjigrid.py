import types
import shlex

from aqt import mw, gui_hooks
from aqt.webview import AnkiWebView
from aqt.qt import (QAction, QSizePolicy, QDialog, QHBoxLayout,
                    QVBoxLayout, QTabWidget, QLabel, QCheckBox, QSpinBox,
                    QComboBox, QPushButton, QLineEdit, Qt, qconnect,
                    QScrollArea, QWidget, QMessageBox, QDateTimeEdit,
                    QDateTime)

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
        if units is not None:
            self.displaygrid(config, util.get_deck_name(mw, config), units)

    def setup(self):
        config = types.SimpleNamespace(**config_util.get_config(mw))
        config.did = mw.col.conf['curDeck']

        data.init_groups()

        setup_win = QDialog(mw)
        vertical_layout = QVBoxLayout()

        deck_horizontal_layout = QHBoxLayout()
        deckcb = QComboBox()
        deckcb.addItem("*") # * = all decks
        deckcb.addItems(sorted(mw.col.decks.all_names()))
        deckcb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        deck_horizontal_layout.addWidget(QLabel("Deck: "))
        deckcb.setCurrentText(mw.col.decks.get(config.did)['name'])
        def change_did(deckname):
            if deckname == "*":
                config.did = "*"
                return
            config.did = mw.col.decks.by_name(deckname)['id']
        deckcb.currentTextChanged.connect(change_did)
        deck_horizontal_layout.addWidget(deckcb)
        vertical_layout.addLayout(deck_horizontal_layout)

        tabs_frame = QTabWidget()
        vertical_layout.addWidget(tabs_frame)

        #General Tab
        general_tab = QWidget()
        general_tab_scroll_area = QScrollArea()
        general_tab_scroll_area.setWidgetResizable(True)
        general_tab_vertical_layout = QVBoxLayout()
        general_tab_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        field_horizontal_layout = QHBoxLayout()
        general_tab_vertical_layout.addWidget(QLabel("Field: "))
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
        field_horizontal_layout.addWidget(field)
        general_tab_vertical_layout.addLayout(field_horizontal_layout)

        groupby = QComboBox()
        groupby.addItems([
            "None",
            *(("[" + x.lang + "] " + x.name) for x in data.groupings),
        ])
        groupby.setCurrentIndex(config.groupby)
        general_tab_vertical_layout.addWidget(QLabel("Group by:"))
        general_tab_vertical_layout.addWidget(groupby)

        sortby = QComboBox()
        sortby.addItems([
            *(x.pretty_value().capitalize() for x in util.SortOrder)
        ])
        sortby.setCurrentIndex(config.sortby)
        general_tab_vertical_layout.addWidget(QLabel("Sort by:"))
        general_tab_vertical_layout.addWidget(sortby)

        pagelang = QComboBox()
        pagelang.addItems(["ja", "zh","zh-Hans", "zh-Hant", "ko", "vi"])
        def update_pagelang_dropdown():
            index = groupby.currentIndex() - 1
            if index > 0:
                pagelang.setCurrentText(data.groupings[index].lang)
        groupby.currentTextChanged.connect(update_pagelang_dropdown)
        pagelang.setCurrentText(config.lang)
        general_tab_vertical_layout.addWidget(QLabel("Language:"))
        general_tab_vertical_layout.addWidget(pagelang)

        shnew = QCheckBox("Show units not yet seen")
        shnew.setChecked(config.unseen)
        general_tab_vertical_layout.addWidget(shnew)

        general_tab.setLayout(general_tab_vertical_layout)
        general_tab_scroll_area.setWidget(general_tab)
        tabs_frame.addTab(general_tab_scroll_area, "General")

        #Advanced Tab
        advanced_tab = QWidget()
        advanced_tab_scroll_area = QScrollArea()
        advanced_tab_scroll_area.setWidgetResizable(True)
        advanced_tab_vertical_layout = QVBoxLayout()
        advanced_tab_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        strong_interval = QSpinBox()
        strong_interval.setRange(1, 65536)
        strong_interval.setValue(config.interval)
        advanced_tab_vertical_layout.addWidget(QLabel("Card interval considered strong:"))
        advanced_tab_vertical_layout.addWidget(strong_interval)

        search_filter = QLineEdit()
        search_filter.setText(config.searchfilter)
        search_filter.setPlaceholderText("e.g. \"is:new\" or \"tag:mining_deck\"")
        advanced_tab_vertical_layout.addWidget(QLabel("Additional Search Filters:"))
        advanced_tab_vertical_layout.addWidget(search_filter)

        time_travel_datetime = QDateTimeEdit()
        time_travel_default_time = QDateTime.currentDateTime()
        time_travel_datetime.setDateTime(time_travel_default_time)
        time_travel_datetime.setCalendarPopup(True)
        advanced_tab_vertical_layout.addWidget(QLabel("Time Travel:"))
        advanced_tab_vertical_layout.addWidget(time_travel_datetime)
        time_travel_note = QLabel("Generated grid might not match actual past grid exactly")
        time_travel_note.setStyleSheet("color: gray")
        advanced_tab_vertical_layout.addWidget(time_travel_note)

        advanced_tab.setLayout(advanced_tab_vertical_layout)
        advanced_tab_scroll_area.setWidget(advanced_tab)
        tabs_frame.addTab(advanced_tab_scroll_area, "Advanced")

        #Data Tab
        data_tab = QWidget()
        data_tab_scroll_area = QScrollArea()
        data_tab_scroll_area.setWidgetResizable(True)
        data_tab_vertical_layout = QVBoxLayout()
        data_tab_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        def set_config_attributes(config):
            config.fieldslist = shlex.split(field.currentText().lower())
            config.searchfilter = search_filter.text()
            config.interval = strong_interval.value()
            config.groupby = groupby.currentIndex()
            config.sortby = sortby.currentIndex()
            config.lang = pagelang.currentText()
            config.unseen = shnew.isChecked()
            config.timetravel_enabled = time_travel_default_time.toMSecsSinceEpoch() != time_travel_datetime.dateTime().toMSecsSinceEpoch()
            config.timetravel_time = time_travel_datetime.dateTime().toMSecsSinceEpoch()
            return config

        data_tab_vertical_layout.addWidget(QLabel("Save grid without rendering:"))
        save_grid_buttons_horizontal_layout = QHBoxLayout()
        data_tab_vertical_layout.addLayout(save_grid_buttons_horizontal_layout)

        def save_html_grid(config):
            new_config = set_config_attributes(config)
            save.savehtml(mw, mw, new_config, util.get_deck_name(mw, new_config))

        save_html_button = QPushButton("Save HTML", clicked = lambda _: save_html_grid(config))
        save_grid_buttons_horizontal_layout.addWidget(save_html_button)

        def save_json_grid(config):
            new_config = set_config_attributes(config)
            units = generate_grid.kanjigrid(mw, new_config)
            save.savejson(mw, mw, new_config, util.get_deck_name(mw, new_config), units)

        save_json_button = QPushButton("Save JSON", clicked = lambda _: save_json_grid(config))
        save_grid_buttons_horizontal_layout.addWidget(save_json_button)

        def save_txt_grid(config):
            new_config = set_config_attributes(config)
            units = generate_grid.kanjigrid(mw, new_config)
            save.savetxt(mw, mw, new_config, util.get_deck_name(mw, new_config), units)

        save_txt_button = QPushButton("Save TXT", clicked = lambda _: save_txt_grid(config))
        save_grid_buttons_horizontal_layout.addWidget(save_txt_button)

        data_tab_vertical_layout.addWidget(QLabel("Timelapse:"))
        timelapse_dates_horizontal_layout = QHBoxLayout()
        data_tab_vertical_layout.addLayout(timelapse_dates_horizontal_layout)
        timelapse_default_time = QDateTime.currentDateTime()
        timelapse_start_time = QDateTimeEdit()
        timelapse_start_time.setDateTime(timelapse_default_time)
        timelapse_start_time.setCalendarPopup(True)
        timelapse_start_time.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        timelapse_dates_horizontal_layout.addWidget(timelapse_start_time)
        timelapse_end_time = QDateTimeEdit()
        timelapse_end_time.setDateTime(timelapse_default_time)
        timelapse_end_time.setCalendarPopup(True)
        timelapse_end_time.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        timelapse_dates_inbetween_label = QLabel("to")
        timelapse_dates_inbetween_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        timelapse_dates_horizontal_layout.addWidget(timelapse_dates_inbetween_label)
        timelapse_dates_horizontal_layout.addWidget(timelapse_end_time)
        timelapse_step_length = QLineEdit()
        timelapse_step_length.setText("10")
        timelapse_steps_horizontal_layout = QHBoxLayout()
        timelapse_steps_horizontal_layout.addWidget(QLabel("Step size (days):"))
        timelapse_steps_horizontal_layout.addWidget(timelapse_step_length)
        data_tab_vertical_layout.addLayout(timelapse_steps_horizontal_layout)

        def generate_timelapse(config):
            step_size = int(float(timelapse_step_length.text()) * 86400000)
            save.savetimelapsejson(mw, mw, set_config_attributes(config), util.get_deck_name(mw, config), timelapse_start_time.dateTime().toMSecsSinceEpoch(), timelapse_end_time.dateTime().toMSecsSinceEpoch(), step_size)

        generate_timelapse_button = QPushButton("Generate Timelapse Data", clicked = lambda _: generate_timelapse(config))
        data_tab_vertical_layout.addWidget(generate_timelapse_button)
        timelapse_note = QLabel("Timelapse data requires external tools to process")
        timelapse_note.setStyleSheet("color: gray")
        data_tab_vertical_layout.addWidget(timelapse_note)

        save_reset_buttons_horizontal_layout = QHBoxLayout()
        data_tab_vertical_layout.addWidget(QLabel("Manage settings:"))
        data_tab_vertical_layout.addLayout(save_reset_buttons_horizontal_layout)

        def save_settings(config):
            config_util.set_config(mw, set_config_attributes(config))

        save_settings_button = QPushButton("Save Settings", clicked = lambda _: save_settings(config))
        save_reset_buttons_horizontal_layout.addWidget(save_settings_button)

        def reset_settings(setup_win):
            reply = QMessageBox.question(setup_win, "Reset Settings", "Confirm reset settings")
            if reply == QMessageBox.StandardButton.Yes:
                config_util.reset_config(mw)
                setup_win.reject()

        reset_settings_button = QPushButton("Reset Settings", clicked = lambda _: reset_settings(setup_win))
        save_reset_buttons_horizontal_layout.addWidget(reset_settings_button)

        data_tab.setLayout(data_tab_vertical_layout)
        data_tab_scroll_area.setWidget(data_tab)
        tabs_frame.addTab(data_tab_scroll_area, "Data")

        #Bottom Buttons
        bottom_buttons_horizontal_layout = QHBoxLayout()
        vertical_layout.addLayout(bottom_buttons_horizontal_layout)
        generate_button = QPushButton("Generate", clicked = setup_win.accept)
        bottom_buttons_horizontal_layout.addWidget(generate_button)
        close_button = QPushButton("Close", clicked = setup_win.reject)
        bottom_buttons_horizontal_layout.addWidget(close_button)

        setup_win.setLayout(vertical_layout)
        setup_win.resize(500, 400)
        if setup_win.exec():
            mw.progress.start(immediate=True)
            config = set_config_attributes(config)
            self.makegrid(config)
            mw.progress.finish()
            self.win.show()