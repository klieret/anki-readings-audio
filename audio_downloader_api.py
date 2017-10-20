#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("/usr/share/anki")
sys.path.append("/home/fuchur/Anki/addons")
import sip
import re
import time
import aqt
import os.path
import unicodedata
from anki.utils import stripHTML
from aqt.qt import QAction, SIGNAL
from anki.hooks import addHook
from downloadaudio.field_data import JapaneseFieldData
from downloadaudio.downloaders import downloaders
from downloadaudio.mediafile_utils import unmunge_to_mediafile
from downloadaudio.mediafile_utils import exists_lc
from collections import defaultdict

# To run in stand-alone mode without anki:
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
sip.setapi("QUrl", 2)


class MockMw(object):
    """ The downloadaudio plugin assumes that
    it is run together with Anki and makes use of methods
    such as aqt.mw.pm.addonFolder.
    However if this program is run stand alone (not plugged
    into anki), aqt.mw will be of type None and any calls
    to aqt.mw.etc. will result in Exceptions. Therefore
    we build this mock object to overwrite mw with it. """
    # from http://stackoverflow.com/questions/15430104/how-can-i-create-a-class-method-with-multiple-dots
    def __init__(self, addon_folder, media_folder):
        self._attr_path = []
        self.addon_folder = addon_folder
        self.media_folder = media_folder
        # target dir where the downloaded media will be saved to.
        # can be arbitrary.

    def __getattr__(self, attr):
        self._attr_path.append(attr)
        return self
        # this means if you call Mock.a.b.c, the
        # __getattr__ will be called 3 times with the arguments
        # a, b, c. At the end we will have self._attr_path = ['a', 'b', 'c']

    def __call__(self, *args, **kw):
        # If the call is MockMw.a.b.c, we will call
        # the method MockMw.a__b__c
        name = self._attr_path[-1]
        del self._attr_path[:]
        for name in dir(self):
            return self.__getattr__(name)(args, kw)
        else:
            # else we would run in infinite loops
            raise AttributeError

    # noinspection PyPep8Naming
    # mw.pm.addonFolder
    def addonFolder(self):
        return self.addon_folder

    # mw.col.media.dir
    def dir(self):
        return self.media_folder

# don't move this to the bottom. Has to run before using the (re)defined
# variables.

if __name__ == "__main__":
    # if run in stand-alone mode
    aqt.mw = MockMw(addon_folder=unicode(os.path.expanduser("~/Anki/addons")),
                    media_folder=unicode(os.path.expanduser("~")))


def media_file_exists(word):
    """Check if the media from dl_entry has already been downloaded.
    :return: False if doesn't exist, else the path relative to media dir
    """
    base = word
    end = ".mp3"
    # adapted from the function free_media_name of
    # downloadaudio.media_utils: Get the path to which the download_entry
    # would have been downloaded to (so like free_media_name without
    # avoid name clashes).
    base = stripHTML(base)
    # Strip the ‘invalidFilenameChars’ by hand.
    base = re.sub(ur'[\\/:\*?\'"<>\|]', '', base)
    base = unicodedata.normalize('NFC', base)
    # Looks like the normalization issue has finally been
    # solved. Always use NFC versions of file names now.
    mdir = aqt.mw.col.media.dir()
    if exists_lc(mdir, base + end):
        return base + end
    else:
        return False


def download(word=u"", language="ja", redownload=False):
    if not word:
        return []
    if not redownload:
        previous = media_file_exists(word)
        if previous:
            return [previous]

    field_data = JapaneseFieldData(u"", u"", word)
    # Arguments: Word field, Audio field, Word.
    # Actually the first 2 arguments do not matter for us,
    # word is the Expression in the form <kanji>[<hiragana>]
    retrieved_entries = []
    for dloader in downloaders:
        dloader.language = language
        # noinspection PyBroadException
        try:
            dloader.download_files(field_data)
        except:
            # blacklist also raises Exceptions for communication etc.
            continue
        retrieved_entries += dloader.downloads_list
    file_paths = []
    for entry in retrieved_entries:
        if not redownload:
            # fixme: still nescessary after guessing?
            previous = media_file_exists(entry.word)
        else:
            previous = False
        if previous:
            file_paths.append(previous)
        else:
            entry.process()  # download to /tmp/
            file_paths.append(unmunge_to_mediafile(entry))  # unmunge moves it to real location
    return file_paths


def setup_menu(browser):
    a = QAction("Bulk add Audio.", browser)
    browser.form.menuEdit.addAction(a)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: handle_bulk(e))


class Tracker(object):
    def __init__(self):
        self.stats = defaultdict(int)
        self.total = 0

    def track(self, state):
        self.stats[state] += 1

    def sleep_time(self, state):
        if state == NoteState.downloaded_audio:
            # wait so that we don't trouble the server
            return 5 if self.total <= 20 else 10
        elif state == NoteState.no_audio:
            # wait a bit less because we didn't download the audio,
            # only checked that it was available
            return 0 if self.total <= 20 else 1
        else:
            return 0

    @property
    def checked(self):
        return sum(self.stats.values())

    def estimate_remaining_time(self):
        if self.total == 0:
            return 0
        # how many notes of given state do we expect?
        estimate = {key: max(0, (1.*self.total/self.checked -1) * self.stats[key]) for key in self.stats}
        return int(sum([estimate[state]*self.sleep_time(state) for state in self.stats]))


def handle_bulk(browser):
    nids = browser.selectedNotes()
    tracker = Tracker()
    tracker.total = len(nids)
    aqt.mw.progress.start()
    note = None
    for nid in nids:
        note = aqt.mw.col.getNote(nid)
        state = handle_note(note)
        tracker.track(state)
        sleep_time = tracker.sleep_time(state)
        time.sleep(sleep_time)
        print("ETA: {}".format(tracker.estimate_remaining_time()))
    aqt.mw.progress.finish()
    aqt.mw.reset()


class NoteState(object):
    no_audio, previous_audio, downloaded_audio, found_audio = range(4)


def handle_note(note):
    if stripHTML(note["Audio"]).strip():
        # Audio field already has something in it,
        # we can skip.
        return NoteState.previous_audio
    word = note["Reading"]
    existing = media_file_exists(word)
    if existing:
        paths = [existing]
    else:
        paths = download(word)
    if not paths:
        return NoteState.no_audio
    for path in paths:
        note["Audio"] += u"[sound:{}]".format(os.path.basename(path))
    note.flush()
    if existing:
        return NoteState.found_audio
    else:
        return NoteState.downloaded_audio

if __name__ == "__main__":
    download()
else:
    addHook('browser.setupMenus', setup_menu)
