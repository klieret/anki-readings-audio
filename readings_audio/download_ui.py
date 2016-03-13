#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import time

import sip
# Depending on the API, the QtCore.Qsettings object acts differently:
# Suppose settings=QtCore.QSettings(....), then
# settings.value(...) will return a unicode string if we have API 2
# (which we will have to cast to an int/bool etc.)
# and an object with a toInt(), toBool() etc. method if we have API 1
# Anki uses API 2, the following is for running the script
# in stand alone mode.
sip.setapi('QVariant', 2)
sip.setapi('QSettings', 2)
sip.setapi('QString', 2)
from PyQt4 import QtGui, QtCore  # do not move these lines before the sip.setapi lines!
import gui_download_design



class MainGui(QtGui.QWidget, gui_download_design.Ui_Dialog):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # Names ...................

        self.add_dependant_boxes = [self.radioButton_extend, self.radioButton_overwrite,
                                    self.radioButton_overwrite_empty]
        self.download_dependant_boxes = [self.checkBox_ignore_blacklist, self.checkBox_redownload]

        # Setup values ..................

        self.pushButton_start.setFocus()
        self.pushButton_start.setDefault(True)
        self.pushButton_start.setAutoDefault(True)

        # just to be sure ..................

        self.box_implications_add()
        self.box_implications_download()

        # Connections ..................

        self.checkBox_download_missing.stateChanged.connect(self.box_implications_download)
        self.checkBox_add_media.stateChanged.connect(self.box_implications_add)
        self.pushButton_start.clicked.connect(self.mock_loop)

    def mock_loop(self):
        self.label_status.setText("Status: Running...")

        self.progressBar.setEnabled(True)

        self.pushButton_stop.setEnabled(True)
        self.pushButton_quit.setEnabled(False)
        self.pushButton_start.setEnabled(False)

        self.progressBar.setMaximum(100)
        for i in range(100):
            self.label_status.setText("Status: {}".format(i))
            self.progressBar    .setValue(i)
            time.sleep(1)
            item = QtGui.QTableWidgetItem(str(i))
            item.setTextAlignment(QtCore.Qt.AlignRight)
            self.tableWidget.setItem(2,2, item)
            if i == 3:
                break
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

    def box_implications_add(self):
        for radio_button in self.add_dependant_boxes:
            radio_button.setEnabled(self.checkBox_add_media.isChecked())

    def box_implications_download(self):
        for check_box in self.download_dependant_boxes:
            check_box.setEnabled(self.checkBox_download_missing.isChecked())

if __name__ == '__main__':
    # for testing purposes
    app = QtGui.QApplication(sys.argv)
    mg = MainGui()
    mg.show()
    app.exec_()
