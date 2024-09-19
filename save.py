import os
import json
import datetime
import re
from aqt.utils import showInfo, showCritical
from aqt.qt import (QStandardPaths, QFileDialog, QTimer, QPageLayout, QPageSize,
                    QMarginsF)

def get_filename(name):
    current_date = datetime.datetime.now().strftime("%Y_%m_%d")
    return re.sub("(\s|<|>|:|\"|/|\\\|\||\?|\*)", "_", name) + "_" + current_date

def savehtml(self, mw, config, deckname):
    fileName = QFileDialog.getSaveFileName(self.win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".html", "Web Page (*.html *.htm)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".htm" not in fileName:
            fileName += ".html"
        with open(fileName, 'w', encoding='utf-8') as fileOut:
            units = self.kanjigrid(config)
            self.generate(config, units)
            fileOut.write(self.html)
        mw.progress.finish()
        showInfo("Page saved to %s!" % os.path.abspath(fileOut.name))

def savepng(self, mw, config, deckname):
    oldsize = self.wv.size()

    content_size = self.wv.page().contentsSize().toSize()
    content_size.setWidth(self.wv.size().width() * config.saveimagequality) #width does not need to change to content size
    content_size.setHeight(content_size.height() * config.saveimagequality)
    self.wv.resize(content_size)

    if config.saveimagequality != 1:
        self.wv.page().setZoomFactor(config.saveimagequality)

        def resize_to_content():
            content_size = self.wv.page().contentsSize().toSize()
            content_size.setWidth(self.wv.size().width()) #width does not need to change to content size
            content_size.setHeight(content_size.height())
            self.wv.resize(content_size)
        QTimer.singleShot(config.saveimagedelay, resize_to_content)

    fileName = QFileDialog.getSaveFileName(self.win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".png", "Portable Network Graphics (*.png)")[0]
    if fileName != "":
        if ".png" not in fileName:
            fileName += ".png"

        success = self.wv.grab().save(fileName, b"PNG")
        if success:
            showInfo("Image saved to %s!" % os.path.abspath(fileName))
        else:
            showCritical("Failed to save the image.")

    self.wv.page().setZoomFactor(1)
    self.wv.resize(oldsize)

def savepdf(self, mw, deckname):
    fileName = QFileDialog.getSaveFileName(self.win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".pdf", "PDF (*.pdf)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".pdf" not in fileName:
            fileName += ".pdf"

        def finish():
            mw.progress.finish()
            showInfo("PDF saved to %s!" % os.path.abspath(fileName))
            self.wv.pdfPrintingFinished.disconnect()

        self.wv.pdfPrintingFinished.connect(finish)
        page_size = self.wv.page().contentsSize()
        page_size.setWidth(page_size.width() * 0.75) #`pixels * 0.75 = points` with default dpi used by printToPdf or QPageSize
        page_size.setHeight(page_size.height() * 0.75)
        self.wv.printToPdf(fileName, QPageLayout(QPageSize(QPageSize(page_size, QPageSize.Unit.Point, None, QPageSize.SizeMatchPolicy.ExactMatch)), QPageLayout.Orientation.Portrait, QMarginsF()))

def savejson(self, mw, config, deckname, units):
    fileName = QFileDialog.getSaveFileName(self.win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".json", "JSON (*.json)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".json" not in fileName:
            fileName += ".json"
        with open(fileName, 'w', encoding='utf-8') as fileOut:
            self.timepoint("JSON start")
            json_dump = json.dumps({'units':units, 'config':config}, default=lambda x: x.__dict__, indent=4)
            fileOut.write(json_dump)
        mw.progress.finish()
        showInfo("JSON saved to %s!" % os.path.abspath(fileOut.name))

def savetxt(self, mw, config, deckname, units):
    fileName = QFileDialog.getSaveFileName(self.win, "Save Page", QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0] + "/" + get_filename(deckname) + ".txt", "TXT (*.txt)")[0]
    if fileName != "":
        mw.progress.start(immediate=True)
        if ".txt" not in fileName:
            fileName += ".txt"
        with open(fileName, 'w', encoding='utf-8') as fileOut:
            self.timepoint("TXT start")
            fileOut.write("".join(units.keys()))
        mw.progress.finish()
        showInfo("TXT saved to %s!" % os.path.abspath(fileOut.name))
