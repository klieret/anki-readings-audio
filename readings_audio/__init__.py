#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anki.hooks import addHook
from aqt.qt import QAction, SIGNAL
from aqt import mw
import re
import romkan


class ReadingsAudio():
    def __init__(self):
        self.target_decks = ["KANJI::readings"]
        self.reading_fields = ["kunyomi", "onyomi"]
        self.missing_audio = []
        self.audio_paths = {}
        self.readings_delimeters = [',']

    def process_single(self, note):
        readings = []
        for field in self.reading_fields:
            if field in note.keys():
                readings.extend(self.split_readings(note[field]))
        print(readings)

    def split_readings(self, string):
        """ Takes input string and does 5 things:
        1. Split the string on the delimeters self.delimeters
        2. Removed all non-hiragana-katakana letters
        3. Removes whitespace and all empty strings
        4. Converts all kana to romaji (hepburn transcription)
        5. Converts unicode strings to strings (since now only romaji)
        returns this as a list.
        :param string: Input string, containing readings as hiragana/katakana, separated by delimters.
        :return: List of the readings.
        """
        regex = '|'.join(map(re.escape, self.readings_delimeters))
        splitted = re.split(regex, string)
        kana_only = [''.join(re.findall(u"[\u3040-\u30ff]", split)) for split in splitted]
        no_whitespace = [kana.strip() for kana in kana_only if kana.strip()]
        return [str(romkan.to_hepburn(kana)) for kana in no_whitespace]

    def process_all(self):
        for deck in self.target_decks:
            nids = mw.col.findCards("deck:%s" % deck)
            print("%d nids" % len(nids))
            for nid in nids:
                card = mw.col.getCard(nid)
                note = card.note()
                self.process_single(note)


def run():
    ra = ReadingsAudio()
    ra.process_all()


def setup_menu(browser):
    a = QAction("Sync readings Audio", browser)
    browser.form.menuEdit.addAction(a)
    browser.connect(a, SIGNAL("triggered()"), run)


addHook('browser.setupMenus', setup_menu)
