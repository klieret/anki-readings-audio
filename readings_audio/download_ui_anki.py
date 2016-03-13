#!/usr/bin/env python
# -*- coding: utf-8 -*-

# todo: import only wat's needed
from download_ui import *
from anki_api import *


class MainGui(MainGuiNoAnki):
    def __init__(self):
        print("This is MainGui. init for {}".format(super(self.__class__, self)))
        super(MainGui, self).__init__()
        self.crawler = AnkiCrawler()

    def run(self):
        self.label_status.setText("Status: Running...")

        self.progressBar.setEnabled(True)
        self.tableWidget.setEnabled(True)

        self.pushButton_stop.setEnabled(True)
        self.pushButton_quit.setEnabled(False)
        self.pushButton_start.setEnabled(False)

        self.batch_process_all()

        self.label_status.setText("Status: Idle...")

        self.pushButton_stop.setEnabled(False)

        self.pushButton_quit.setEnabled(True)
        self.pushButton_quit.setFocus()
        self.pushButton_quit.setDefault(True)
        self.pushButton_quit.setAutoDefault(True)

        self.pushButton_start.setEnabled(True)
        self.pushButton_start.clearFocus()
        self.pushButton_start.setDefault(False)
        self.pushButton_start.setAutoDefault(False)

        self.progressBar.setEnabled(False)
        self.progressBar.reset()

    def display_statistics(self):
        self.tableWidget.setEnabled(True)
        keys_in_order = ["total_notes", "total_audio_files", "missing_audio", "newly_downloaded", "failed_to_download"]
        for row, key in enumerate(keys_in_order):
            item = QtGui.QTableWidgetItem(str(self.crawler.statistics[key]))
            item.setTextAlignment(QtCore.Qt.AlignRight)
            self.tableWidget.setItem(0, row, item)


    def batch_process_all(self):
        nids = []
        for deck in self.crawler.target_decks:
            nids += mw.col.findCards("deck:%s" % deck)
        print "There's a total of %d notes." % len(nids)
        self.crawler.statistics["total_notes"] = len(nids)
        self.progressBar.setMaximum(len(nids))

        add_mode = AddMode()
        add_mode.set_defaults()
        download_mode = DownloadMode()
        download_mode.set_defaults()
        download_mode.enabled = False
        mode = CrawlingMode(add_mode, download_mode)
        mode.check_options()

        for num, nid in enumerate(nids):
            card = mw.col.getCard(nid)
            note = card.note()
            # todo: carefull overwrite!

            print(num)

            self.progressBar.setValue(num)
            self.crawler.update_statistics()
            self.display_statistics()

            self.crawler.process_single(note, mode)

            # if num == 10:
            #     todo: remove; for testing only
                # print("abort because testing only")
                # break

        print(self.crawler.missing_audio)