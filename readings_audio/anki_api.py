#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aqt import mw
import re
import romkan
from .downloader_api import get_audio_entries
import time


class ReadingsAudio():
    def __init__(self):
        self.target_decks = ["KANJI::readings"]
        self.reading_fields = ["kunyomi", "onyomi"]
        self.missing_audio = []
        self.audio_paths = {}
        # important: do include japanese version of ',' etc.!
        self.readings_delimeters = [u',', u"、", u';']

    def process_single(self, note):
        readings = []
        for field in self.reading_fields:
            if field in note.keys():
                if note[field].strip(): print(note[field])
                readings.extend(self.split_readings(note[field]))
        for reading in readings:
            if reading in self.audio_paths:
                continue
            else:
                self.missing_audio.append(reading)

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
        regex = '|'.join(map(re.escape, tuple(self.readings_delimeters)))
        splitted = re.split(regex, string)
        kana_only = [''.join(re.findall(u"[\u3040-\u30ff]", split)) for split in splitted]
        no_whitespace = [kana.strip() for kana in kana_only if kana.strip()]
        return [str(romkan.to_hepburn(kana)) for kana in no_whitespace]

    def process_all(self, gui=True):
        nids = []
        for deck in self.target_decks:
            nids += mw.col.findCards("deck:%s" % deck)
        print "There's a total of %d notes." % len(nids)

        # if gui:
        #     dialog, pb = progress_bar(len(nids))

        for num, nid in enumerate(nids):
            # if gui:
            #     pb.setValue(num)
            card = mw.col.getCard(nid)
            note = card.note()
            self.process_single(note)

        # if gui:
        #     dialog.destroy()

        # remove duplicates
        self.missing_audio = list(set(self.missing_audio))
        print(self.missing_audio)

    def try_downloading_audio(self, gui=True):
        for word in self.missing_audio:
            paths = get_audio_entries(word)
            print word, paths
            time.sleep(2)