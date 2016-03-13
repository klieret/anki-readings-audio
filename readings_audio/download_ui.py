#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import gui_download_design
from PyQt4 import QtGui
import sys


class MainGui(QtGui.QWidget, gui_download_design.Ui_Dialog):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # Names ...................

        self.add_dependant_boxes = [self.radioButton_extend, self.radioButton_overwrite,
                                    self.radioButton_overwrite_empty]
        self.download_dependant_boxes = [self.checkBox_ignore_blacklist, self.checkBox_redownload]

        # Setup values ..................

        # just to be sure ..................

        self.box_implications_add()
        self.box_implications_download()

        # Connections ..................

        self.checkBox_download_missing.stateChanged.connect(self.box_implications_download)
        self.checkBox_add_media.stateChanged.connect(self.box_implications_add)


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
