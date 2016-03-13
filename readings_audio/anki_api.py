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
        self.audio_collection.scan()
        # important: do include japanese version of ',' etc.!
        self.statistics = defaultdict(int)
        self.update_statistics()

    def update_statistics(self):
        self.statistics["total_audio_files"] = len(self.audio_collection.content)
        self.statistics["missing_audio"] = len(self.missing_audio)

    def process_single(self, note, mode):
        """Processes single note.
        :param note: The note.
        :param mode: CrawlingMode object containing options.
        :return:
        """

        # get readings from reading fields
        readings = []
        for field in self.reading_fields:
            if field in note.keys():
                readings.extend(split_readings(note[field]))

        # handle missing audio files
        for reading in readings:
            if reading not in self.audio_collection:
                if mode.download.enabled:
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

        # possibly add new audio files
        if mode.add.enabled:
            new_paths = []
            for reading in readings:
                if reading in self.audio_collection and self.audio_collection[reading]:
                    # only add the first audio file:
                    new_paths.append(self.audio_collection[reading][0])
                    logger.debug(u"Extended with sound files {}".format(self.audio_collection[reading][0]))

            if new_paths:
                note[self.audio_field] = extend_audio_field(note[self.audio_field], new_paths, mode.add)
            note.flush()
            # todo: return note? or something?

    # for batch/testing
    def batch_process_all(self):
        nids = []
        for deck in self.target_decks:
            nids += mw.col.findCards("deck:%s" % deck)
        print "There's a total of %d notes." % len(nids)
        self.statistics["total_notes"] = len(nids)

        add_mode = AddMode()
        add_mode.set_defaults()
        download_mode = DownloadMode()
        download_mode.set_defaults()
        mode = CrawlingMode(add_mode, download_mode)
        mode.check_options()

        for num, nid in enumerate(nids):
            card = mw.col.getCard(nid)
            note = card.note()
            # todo: carefull overwrite!

            self.process_single(note, mode)
            if num >= 10:
                # todo: remove; for testing only
                break

        print(self.missing_audio)