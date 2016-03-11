#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anki.hooks import addHook
from aqt.qt import QAction, SIGNAL
from aqt import mw
import re
import romkan
# todo: use try/except
from downloadaudio.field_data import JapaneseFieldData
from downloadaudio.download import do_download
from downloadaudio.downloaders import downloaders

import signal


def timeout(func, args=(), kwargs={}, timeout_duration=10, default=None):
    import signal

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError as exc:
        print("Timeout!")
        result = default
    finally:
        signal.alarm(0)

    return result

def get_path_to_audio(word):
    retrieved_entries = []
    hiragana = romkan.to_hiragana(word)
    field_data = JapaneseFieldData("onyomi", "sound", hiragana)
    field_data.word = u""
    for dloader in downloaders:
        # Use a public variable to set the language.
        dloader.language = "ja"
        try:
            # print("Testing", dloader)
            # Make it easer inside the downloader. If anything
            # goes wrong, don't catch, or raise whatever you want.
            dloader.download_files(field_data)
        except:
            #  # Uncomment this raise while testing a new
            #  # downloaders.  Also use the “For testing”
            #  # downloaders list with your downloader in
            #  # downloaders.__init__
            raise
            continue
        retrieved_entries += dloader.downloads_list
    file_paths = []
    for entry in retrieved_entries:
        entry.process()
        file_paths.append(entry.file_path)
    return file_paths


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
        self.missing_audio = list(set(self.missing_audio))
        print(self.missing_audio)

    def try_downloading_audio(self):
        for word in self.missing_audio:
            paths = timeout(get_path_to_audio, args=[word])
            print word, paths

def run():
    ra = ReadingsAudio()
    ra.process_all()
    ra.try_downloading_audio()

def setup_menu(browser):
    a = QAction("Sync readings Audio", browser)
    browser.form.menuEdit.addAction(a)
    browser.connect(a, SIGNAL("triggered()"), run)


addHook('browser.setupMenus', setup_menu)
