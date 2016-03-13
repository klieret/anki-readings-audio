#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aqt import mw
import romkan
from .downloader_api import get_audio_entries
import time
from .audiocollection import AudioCollection
from .field_operations import split_readings, extend_audio_field
import sys


import logging
logger = logging.getLogger("test")
sh = logging.StreamHandler(stream=sys.stdout)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.DEBUG)
from .modes import *
from collections import defaultdict


class AnkiCrawler(object):
    def __init__(self):
        self.target_decks = ["KANJI::readings"]
        self.reading_fields = ["kunyomi", "onyomi"]
        self.audio_field = "Audio"
        self.missing_audio = set()
        self.audio_collection = AudioCollection()
        # important: do include japanese version of ',' etc.!
        self.statistics = defaultdict(int)

    def update_statistics(self):
        self.statistics["total_audio_files"] = len(self.audio_collection.content)
        self.statistics["missing_audio"] = len(self.missing_audio)

    def process_readings(self, note):
        # get readings from reading fields
        readings = []
        for field in self.reading_fields:
            if field in note.keys():
                readings.extend(split_readings(note[field]))
        return readings

    def process_download(self, readings, dl_mode, no_download=False):
        # handle missing audio files
        for reading in readings:
            if reading not in self.audio_collection:
                if dl_mode.enabled and not no_download:
                    # todo: blacklisting?
                    num = self.audio_collection.download(reading)
                    self.statistics["newly_downloaded"] += num
                    if num == 0:
                        # don't do anything with statistics["missing_audio"] yet
                        self.statistics["failed_to_download"] += 1
                        self.missing_audio.add(reading)
                else:
                    logger.debug("Reading {} is missing.".format(reading))
                    self.missing_audio.add(reading)

    def process_add(self, note, readings, add_mode, do_flush = True):
        # possibly add new audio files
        if add_mode.enabled:
            new_paths = []
            for reading in readings:
                if reading in self.audio_collection and self.audio_collection[reading]:
                    # only add the first audio file:
                    new_paths.append(self.audio_collection[reading][0])
                    logger.debug(u"Extended with sound files {}".format(self.audio_collection[reading][0]))

            if new_paths:
                note[self.audio_field] = extend_audio_field(note[self.audio_field], new_paths, add_mode)
            if do_flush:
                # we can't flush inside of a thread, that's why we need to postpone flush sometimes
                note.flush()
            # todo: return note? or something?

    # for batch/testing
    def batch_process_all(self, mode):
        self.audio_collection.scan()
        self.update_statistics()
        nids = []
        for deck in self.target_decks:
            nids += mw.col.findCards("deck:%s" % deck)

        for num, nid in enumerate(nids):
            card = mw.col.getCard(nid)
            note = card.note()
            readings = self.process_readings(note)
            self.process_download(readings, mode.download)
            self.process_add(note, readings, mode.add)
            self.update_statistics()

        print(self.missing_audio)