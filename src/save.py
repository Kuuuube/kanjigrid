import datetime
import json
import os
import re

from aqt.operations import QueryOp
from aqt.qt import (
    QFileDialog,
    QMarginsF,
    QPageLayout,
    QPageSize,
    QStandardPaths,
    QTimer,
)
from aqt.utils import showCritical, showInfo

from . import generate_grid


def get_filename(name: str) -> str:
    current_date = datetime.datetime.now(tz = datetime.timezone.utc).strftime("%Y_%m_%d_%H_%M_%S")
    return re.sub(r"(\s|<|>|:|\"|/|\\|\||\?|\*)", "_", name) + "_" + current_date

def epoch_ms_to_date(epoch) -> str:
    # datetime wants epoch in seconds not milliseconds
    return datetime.datetime.fromtimestamp(epoch / 1000, tz = datetime.timezone.utc).strftime("%Y_%m_%d")

def savehtml(mw, win, config, deckname) -> None:
    file_name = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".html", "Web Page (*.html *.htm)")[0]
    if file_name != "":
        mw.progress.start(immediate=True)
        if ".htm" not in file_name:
            file_name += ".html"

        def save(file_name: str) -> None:
            with open(file_name, 'w', encoding='utf-8') as file_out:
                units = generate_grid.kanjigrid(mw, config)
                generated_html = generate_grid.generate(mw, config, units, export = True)
                file_out.write(generated_html)

        def on_done(file_name: str) -> None:
            mw.progress.finish()
            showInfo("HTML saved to %s!" % os.path.abspath(file_name))

        QueryOp(parent = win, op = lambda _: save(file_name), success = lambda _: on_done(file_name)).run_in_background()

def savepng(wv, win, config, deckname) -> None:
    oldsize = wv.size()

    content_size = wv.page().contentsSize().toSize()
    content_size.setWidth(wv.size().width() * config.saveimagequality) #width does not need to change to content size
    content_size.setHeight(content_size.height() * config.saveimagequality)
    wv.resize(content_size)

    if config.saveimagequality != 1:
        wv.page().setZoomFactor(config.saveimagequality)

        def resize_to_content() -> None:
            content_size = wv.page().contentsSize().toSize()
            content_size.setWidth(wv.size().width()) #width does not need to change to content size
            content_size.setHeight(content_size.height())
            wv.resize(content_size)
        QTimer.singleShot(config.saveimagedelay, resize_to_content)

    file_name = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".png", "Portable Network Graphics (*.png)")[0]
    if file_name != "":
        if ".png" not in file_name:
            file_name += ".png"

        success = wv.grab().save(file_name, b"PNG")
        if success:
            showInfo("Image saved to %s!" % os.path.abspath(file_name))
        else:
            showCritical("Failed to save the image.")

    wv.page().setZoomFactor(1)
    wv.resize(oldsize)

def savepdf(mw, wv, win, deckname) -> None:
    file_name = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".pdf", "PDF (*.pdf)")[0]
    if file_name != "":
        mw.progress.start(immediate=True)
        if ".pdf" not in file_name:
            file_name += ".pdf"

        def finish() -> None:
            mw.progress.finish()
            showInfo("PDF saved to %s!" % os.path.abspath(file_name))
            wv.pdfPrintingFinished.disconnect()

        wv.pdfPrintingFinished.connect(finish)
        page_size = wv.page().contentsSize()
        page_size.setWidth(page_size.width() * 0.75) #`pixels * 0.75 = points` with default dpi used by printToPdf or QPageSize
        page_size.setHeight(page_size.height() * 0.75)
        wv.printToPdf(file_name, QPageLayout(QPageSize(QPageSize(page_size, QPageSize.Unit.Point, None, QPageSize.SizeMatchPolicy.ExactMatch)), QPageLayout.Orientation.Portrait, QMarginsF()))

def savejson(mw, win, config, deckname, units) -> None:
    file_name = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".json", "JSON (*.json)")[0]
    if file_name != "":
        mw.progress.start(immediate=True)
        if ".json" not in file_name:
            file_name += ".json"

        def save(file_name: str) -> None:
            with open(file_name, "w", encoding="utf-8") as file_out:
                json_dump = json.dumps({"units":units, "config":config}, default=lambda x: x.__dict__, indent=4)
                file_out.write(json_dump)

        def on_done(file_name: str) -> None:
            mw.progress.finish()
            showInfo("JSON saved to %s!" % os.path.abspath(file_name))

        QueryOp(parent = win, op = lambda _: save(file_name), success = lambda _: on_done(file_name)).run_in_background()

def savetxt(mw, win, config, deckname, units) -> None:
    file_name = QFileDialog.getSaveFileName(win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".txt", "TXT (*.txt)")[0]
    if file_name != "":
        mw.progress.start(immediate=True)
        if ".txt" not in file_name:
            file_name += ".txt"

        def save(file_name: str) -> None:
            with open(file_name, 'w', encoding='utf-8') as file_out:
                file_out.write("".join(units.keys()))

        def on_done(file_name: str) -> None:
            mw.progress.finish()
            showInfo("TXT saved to %s!" % os.path.abspath(file_name))

        QueryOp(parent = win, op = lambda _: save(file_name), success = lambda _: on_done(file_name)).run_in_background()

def savetimelapsejson(mw, win, config, deckname, time_start, time_end, time_step) -> None:
    file_name = QFileDialog.getSaveFileName(win, "Save Timelapse Data", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/timelapse_" + epoch_ms_to_date(time_end) + "_" + epoch_ms_to_date(time_end) + "_" + "{0:.2g}".format(time_step / 86400000) + "d_" + get_filename(deckname) + ".json", "JSON (*.json)")[0]
    if file_name != "":
        mw.progress.start(immediate=True)
        if ".json" not in file_name:
            file_name += ".json"

        def save(file_name: str) -> None:
            with open(file_name, "w", encoding="utf-8") as file_out:
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
                file_out.write(json_dump)

        def on_done(file_name: str) -> None:
            mw.progress.finish()
            showInfo("Timelapse JSON saved to %s!" % os.path.abspath(file_name))

        QueryOp(parent = win, op = lambda _: save(file_name), success = lambda _: on_done(file_name)).run_in_background()

