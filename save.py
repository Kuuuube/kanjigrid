import os
import json
import datetime
import re
from aqt.utils import showInfo, showCritical
from aqt.operations import QueryOp
from aqt.qt import (QStandardPaths, QFileDialog, QTimer, QPageLayout, QPageSize,
                    QMarginsF)

from . import generate_grid

def get_filename(name):
    current_date = datetime.datetime.now().strftime("%Y_%m_%d")
    return re.sub(r"(\s|<|>|:|\"|/|\\|\||\?|\*)", "_", name) + "_" + current_date

def epoch_ms_to_date(epoch):
    # datetime wants epoch in seconds not milliseconds
    return datetime.datetime.fromtimestamp(epoch / 1000).strftime("%Y_%m_%d")

def savehtml(mw, win, config, deckname):
    fileName = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".html", "Web Page (*.html *.htm)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".htm" not in fileName:
            fileName += ".html"

        def save(fileName):
            with open(fileName, 'w', encoding='utf-8') as fileOut:
                units = generate_grid.kanjigrid(mw, config)
                generated_html = generate_grid.generate(mw, config, units, export = True)
                fileOut.write(generated_html)

        def on_done(fileName):
            mw.progress.finish()
            showInfo("HTML saved to %s!" % os.path.abspath(fileName))

        QueryOp(parent = win, op = lambda _: save(fileName), success = lambda _: on_done(fileName)).run_in_background()

def savepng(wv, win, config, deckname):
    oldsize = wv.size()

    content_size = wv.page().contentsSize().toSize()
    content_size.setWidth(wv.size().width() * config.saveimagequality) #width does not need to change to content size
    content_size.setHeight(content_size.height() * config.saveimagequality)
    wv.resize(content_size)

    if config.saveimagequality != 1:
        wv.page().setZoomFactor(config.saveimagequality)

        def resize_to_content():
            content_size = wv.page().contentsSize().toSize()
            content_size.setWidth(wv.size().width()) #width does not need to change to content size
            content_size.setHeight(content_size.height())
            wv.resize(content_size)
        QTimer.singleShot(config.saveimagedelay, resize_to_content)

    fileName = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".png", "Portable Network Graphics (*.png)")[0]
    if fileName != "":
        if ".png" not in fileName:
            fileName += ".png"

        success = wv.grab().save(fileName, b"PNG")
        if success:
            showInfo("Image saved to %s!" % os.path.abspath(fileName))
        else:
            showCritical("Failed to save the image.")

    wv.page().setZoomFactor(1)
    wv.resize(oldsize)

def savepdf(mw, wv, win, deckname):
    fileName = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".pdf", "PDF (*.pdf)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".pdf" not in fileName:
            fileName += ".pdf"

        def finish():
            mw.progress.finish()
            showInfo("PDF saved to %s!" % os.path.abspath(fileName))
            wv.pdfPrintingFinished.disconnect()

        wv.pdfPrintingFinished.connect(finish)
        page_size = wv.page().contentsSize()
        page_size.setWidth(page_size.width() * 0.75) #`pixels * 0.75 = points` with default dpi used by printToPdf or QPageSize
        page_size.setHeight(page_size.height() * 0.75)
        wv.printToPdf(fileName, QPageLayout(QPageSize(QPageSize(page_size, QPageSize.Unit.Point, None, QPageSize.SizeMatchPolicy.ExactMatch)), QPageLayout.Orientation.Portrait, QMarginsF()))

def savejson(mw, win, config, deckname, units):
    fileName = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".json", "JSON (*.json)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".json" not in fileName:
            fileName += ".json"

        def save(fileName):
            with open(fileName, 'w', encoding='utf-8') as fileOut:
                json_dump = json.dumps({'units':units, 'config':config}, default=lambda x: x.__dict__, indent=4)
                fileOut.write(json_dump)

        def on_done(fileName):
            mw.progress.finish()
            showInfo("JSON saved to %s!" % os.path.abspath(fileName))

        QueryOp(parent = win, op = lambda _: save(fileName), success = lambda _: on_done(fileName)).run_in_background()

def savetxt(mw, win, config, deckname, units):
    fileName = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".txt", "TXT (*.txt)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".txt" not in fileName:
            fileName += ".txt"

        def save(fileName):
            with open(fileName, 'w', encoding='utf-8') as fileOut:
                fileOut.write("".join(units.keys()))

        def on_done(fileName):
            mw.progress.finish()
            showInfo("TXT saved to %s!" % os.path.abspath(fileName))

        QueryOp(parent = win, op = lambda _: save(fileName), success = lambda _: on_done(fileName)).run_in_background()

def savetimelapsejson(mw, win, config, deckname, time_start, time_end, time_step):
    fileName = QFileDialog.getSaveFileName(win, "Save Timelapse Data", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/timelapse_" + epoch_ms_to_date(time_end) + "_" + epoch_ms_to_date(time_end) + "_" + "{0:.2g}".format(time_step / 86400000) + "d_" + get_filename(deckname) + ".json", "JSON (*.json)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".json" not in fileName:
            fileName += ".json"

        def save(fileName):
            with open(fileName, 'w', encoding='utf-8') as fileOut:
                html_list = []
                config.timetravel_enabled = True

                timelapse_range = list(range(time_start, time_end, time_step))
                if time_start not in timelapse_range:
                    timelapse_range.append(time_start)
                if time_end not in timelapse_range:
                    timelapse_range.append(time_end)

                for current_time in timelapse_range:
                    config.timetravel_time = current_time
                    units = generate_grid.kanjigrid(mw, config)
                    html_list.append(generate_grid.generate(mw, config, units, export = True))

                json_dump = json.dumps(html_list, indent=4)
                fileOut.write(json_dump)

        def on_done(fileName):
            mw.progress.finish()
            showInfo("Timelapse JSON saved to %s!" % os.path.abspath(fileName))

        QueryOp(parent = win, op = lambda _: save(fileName), success = lambda _: on_done(fileName)).run_in_background()

