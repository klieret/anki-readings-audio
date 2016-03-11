#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anki.hooks import addHook
from aqt.qt import *


def run():
    print("readings_audio being run...")


def setup_menu(browser):
    a = QAction("Sync readings Audio", browser)
    browser.form.menuEdit.addAction(a)
    browser.connect(a, SIGNAL("triggered()"), run)


addHook('browser.setupMenus', setup_menu)
