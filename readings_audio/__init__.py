#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anki.hooks import addHook
from aqt.qt import QAction, SIGNAL

from .anki_api import ReadingsAudio


def run():
    ra = ReadingsAudio()
    ra.process_all()
    # ra.try_downloading_audio()


def setup_menu(browser):
    a = QAction("Sync readings Audio", browser)
    browser.form.menuEdit.addAction(a)
    browser.connect(a, SIGNAL("triggered()"), run)


addHook('browser.setupMenus', setup_menu)
