#!/usr/bin/env python
# -*- coding: utf-8 -*-

# todo: import only what's needed
from download_ui import *
from anki_api import *

from PyQt4.QtCore import QThread, SIGNAL


class ScanMediaThread(QThread):
    def __init__(self, crawler):
        QThread.__init__(self)
        self.crawler = crawler

    def run(self):
        self.crawler.audio_collection.scan()
        self.terminate()

class MainGui(MainGuiNoAnki):
    def __init__(self):
        super(MainGui, self).__init__()
        self.crawler = None
        self.thread = None

    def run(self):
        self.progressBar.setEnabled(True)
        self.progressBar.setRange(0, 0)
        self.crawler = AnkiCrawler()
        self.thread = ScanMediaThread(self.crawler)
        self.connect(self.thread, SIGNAL("finished()"), self.unsplittable_finished)
        self.thread.start()
        print "dispatched"

    def scan_media_finished(self):
        # stop pulsing
        self.progressBar.setEnabled(False)
        self.progressBar.setRange(0, 1)
        print "finished"

    # def run_(self):
    #     # todo: maybe inherit from top class. also use threading
    #     # something like threading=False
    #     self.label_status.setText("Status: Running...")
    #
    #     self.progressBar.setEnabled(True)
    #     self.tableWidget.setEnabled(True)
    #
    #     self.pushButton_stop.setEnabled(True)
    #     self.pushButton_quit.setEnabled(False)
    #     self.pushButton_start.setEnabled(False)
    #
    #     add_mode = AddMode()
    #     add_mode.set_defaults()
    #     download_mode = DownloadMode()
    #     download_mode.set_defaults()
    #     mode = CrawlingMode(add_mode, download_mode)
    #     mode.check_options()
    #
    #     self.batch_process_all(mode)
    #
    #     self.label_status.setText("Status: Idle...")
    #
    #     self.pushButton_stop.setEnabled(False)
    #
    #     self.pushButton_quit.setEnabled(True)
    #     self.pushButton_quit.setFocus()
    #     self.pushButton_quit.setDefault(True)
    #     self.pushButton_quit.setAutoDefault(True)
    #
    #     self.pushButton_start.setEnabled(True)
    #     self.pushButton_start.clearFocus()
    #     self.pushButton_start.setDefault(False)
    #     self.pushButton_start.setAutoDefault(False)
    #
    #     self.progressBar.setEnabled(False)
    #     self.progressBar.reset()

    # def display_statistics(self):
    #     self.tableWidget.setEnabled(True)
    #     keys_in_order = ["total_notes", "total_audio_files", "missing_audio", "newly_downloaded", "failed_to_download"]
    #     for row, key in enumerate(keys_in_order):
    #         item = QtGui.QTableWidgetItem(str(self.crawler.statistics[key]))
    #         item.setTextAlignment(QtCore.Qt.AlignRight)
    #         self.tableWidget.setItem(0, row, item)


    # def batch_process_all(self, mode):
    #
    #     # todo: threading and everything
    #     # self.label_status.setText("Status: Scanning Media Collection.")
    #     # thread = ScanMediaThread(self.crawler)
    #     self.crawler.audio_collection.scan()
    #     # thread.start()
    #     # self.progressBar.setEnabled(True)
    #     # self.progressBar.setRange(0,0)
    #     # print("in front of wait")
    #     # while not thread.isFinished():
    #     #     time.sleep(0.1)
    #     #     self.progressBar.update()
    #     # print("throuh wait")
    #     # self.progressBar.setRange(0,1)
    #
    #     nids = []
    #     for deck in self.crawler.target_decks:
    #         nids += mw.col.findCards("deck:%s" % deck)
    #     print "There's a total of %d notes." % len(nids)
    #     self.crawler.statistics["total_notes"] = len(nids)
    #     self.progressBar.setMaximum(len(nids))
    #
    #     # make into 2 rounds...
    #
    #     self.label_status.setText("Status: Main Queue")
    #     for num, nid in enumerate(nids):
    #         card = mw.col.getCard(nid)
    #         note = card.note()
    #         self.progressBar.setValue(num)
    #         self.crawler.update_statistics()
    #         self.display_statistics()
    #         readings = self.crawler.process_readings(note)
    #         self.crawler.process_download(readings, mode.download)
    #         self.crawler.process_add(note, readings, mode.add)
    #         self.crawler.update_statistics()
    #
    #     print(self.crawler.missing_audio)