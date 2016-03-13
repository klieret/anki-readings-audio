#!/usr/bin/env python
# -*- coding: utf-8 -*-

# todo: import only what's needed
from download_ui import *
from anki_api import *

from PyQt4.QtCore import QThread, SIGNAL

# todo: quit should properly close thread & Co....

class RunMethodThread(QThread):
    def __init__(self, obj, method_name, *args, **kwargs):
        QThread.__init__(self)
        self.object = obj
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        getattr(self.object, self.method_name)(*self.args, **self.kwargs)
        self.terminate()


def progress_bar_text(progress_bar):
    current = progress_bar.value()
    max = progress_bar.maximum()
    return "{}/{} ({}%)".format(current, max, int(current/max))


class MainThread(QThread):
    def __init__(self, crawler, mode, notes):
        QThread.__init__(self)
        self.crawler = crawler
        self.notes = notes
        self.mode = mode
        self.num = 0
        self.stop = False

    def run(self):
        for num, note in enumerate(self.notes):
            if self.stop:
                print("abort")
                self.terminate()
            print("note", num)
            self.num = num
            self.crawler.update_statistics()
            readings = self.crawler.process_readings(note)
            self.crawler.process_download(readings, self.mode.download)
            # flush must happen outside of threading
            self.crawler.process_add(note, readings, self.mode.add, do_flush = False)
            self.crawler.update_statistics()
            self.emit(SIGNAL("update_progress()"))
        self.terminate()

class MainGui(MainGuiNoAnki):
    def __init__(self):
        super(MainGui, self).__init__()
        self.crawler = None
        self.scan_thread = None
        self.main_thread = None
        self.pushButton_stop.clicked.connect(self.stop)



    def stop(self):
        self.main_thread.stop = True


    def get_mode(self):
        add_mode = AddMode()
        add_mode.set_defaults()
        download_mode = DownloadMode()
        download_mode.set_defaults()
        download_mode.enabled = True
        mode = CrawlingMode(add_mode, download_mode)
        mode.check_options()
        return mode

    def run(self):
        self.stop = False
        # can't abort anyway
        self.pushButton_start.setEnabled(False)
        self.pushButton_stop.setEnabled(False)
        self.pushButton_quit.setEnabled(False)
        # enable pulsing progress bar
        self.progressBar.setEnabled(True)
        self.progressBar.setRange(0, 0)
        # Start thread
        self.crawler = AnkiCrawler()
        self.scan_thread = RunMethodThread(self.crawler.audio_collection, "scan")
        self.connect(self.scan_thread, SIGNAL("finished()"), self.run1)
        self.scan_thread.start()
        print("dispatched")


    def run1(self):
        print("scan_mdeia_finished")
        # stop pulsing
        self.progressBar.setRange(0, 1)

        self.tableWidget.setEnabled(True)
        self.pushButton_stop.setEnabled(True)
        self.pushButton_quit.setEnabled(False)
        self.pushButton_start.setEnabled(False)

        nids = []
        for deck in self.crawler.target_decks:
            nids += mw.col.findCards("deck:%s" % deck)

        notes = []
        for nid in nids:
            card = mw.col.getCard(nid)
            notes.append(card.note())

        self.crawler.statistics["total_notes"] = len(notes)
        self.progressBar.setMaximum(len(notes))

        # make into 2 rounds...

        mode = self.get_mode()

        self.label_status.setText("Status: Main Queue")

        print("building next thread")
        self.main_thread = MainThread(self.crawler, mode, notes)
        print 2
        self.connect(self.main_thread, SIGNAL("finished()"), self.all_finished)
        print 3
        self.connect(self.main_thread, SIGNAL("update_progress()"), self.update_progress)
        print 4
        self.main_thread.start()
        print("main tjread dispatched")

    def all_finished(self):
        print("flushing all")
        for note in self.main_thread.notes:
            note.flush()
        print("all finished")
        print(self.crawler.missing_audio)
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

    def update_progress(self):
        self.progressBar.setEnabled(True)
        self.progressBar.setValue(self.main_thread.num)
        print(progress_bar_text(self.progressBar))
        self.progressBar.setFormat(progress_bar_text(self.progressBar))
        self.tableWidget.setEnabled(True)
        keys_in_order = ["total_notes", "total_audio_files", "missing_audio", "newly_downloaded", "failed_to_download"]
        for row, key in enumerate(keys_in_order):
            item = QtGui.QTableWidgetItem(str(self.crawler.statistics[key]))
            item.setTextAlignment(QtCore.Qt.AlignRight)
            self.tableWidget.setItem(0, row, item)


        # def batch_process_all(self, mode):

        # todo: threading and everything
        # self.label_status.setText("Status: Scanning Media Collection.")
        # thread = ScanMediaThread(self.crawler)
        # self.crawler.audio_collection.scan()
        # thread.start()
        # self.progressBar.setEnabled(True)
        # self.progressBar.setRange(0,0)
        # print("in front of wait")
        # while not thread.isFinished():
        #     time.sleep(0.1)
        #     self.progressBar.update()
        # print("throuh wait")
        # self.progressBar.setRange(0,1)

        # nids = []
        # for deck in self.crawler.target_decks:
        #     nids += mw.col.findCards("deck:%s" % deck)
        # print "There's a total of %d notes." % len(nids)
        # self.crawler.statistics["total_notes"] = len(nids)
        # self.progressBar.setMaximum(len(nids))
        #
        # # make into 2 rounds...
        #
        # self.label_status.setText("Status: Main Queue")
        # for num, nid in enumerate(nids):
        #     card = mw.col.getCard(nid)
        #     note = card.note()
        #     self.progressBar.setValue(num)
        #     self.crawler.update_statistics()
        #     self.update_progress()
        #     readings = self.crawler.process_readings(note)
        #     self.crawler.process_download(readings, mode.download)
        #     self.crawler.process_add(note, readings, mode.add)
        #     self.crawler.update_statistics()
        #
        # print(self.crawler.missing_audio)