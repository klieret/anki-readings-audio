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


class ReadingsAudio(object):
    def __init__(self):
        self.target_decks = ["KANJI::readings"]
        self.reading_fields = ["kunyomi", "onyomi"]
        self.audio_field = "Audio"
        self.missing_audio = set()
        self.audio_collection = AudioCollection()
        self.audio_collection.scan()
        # important: do include japanese version of ',' etc.!

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
                    # todo: also consider the case of failed downloading
                    num = self.audio_collection.download(reading)
                    if num == 0:
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
                else:
                    logger.warning("Still missing audio for reading {}".format(reading))
            print(new_paths)
            if new_paths:
                note[self.audio_field] = extend_audio_field(note[self.audio_field], new_paths, mode.add)
            note.flush()
        # todo: return note? or something?

    # for batch/testing
    def process_all(self):
        nids = []
        for deck in self.target_decks:
            nids += mw.col.findCards("deck:%s" % deck)
        print "There's a total of %d notes." % len(nids)

        for num, nid in enumerate(nids):
            card = mw.col.getCard(nid)
            note = card.note()
            # todo: carefull overwrite!
            add_mode = AddMode()
            add_mode.set_defaults()
            download_mode = DownloadMode()
            download_mode.set_defaults()
            mode = CrawlingMode(add_mode, download_mode)
            mode.check_options()
            self.process_single(note, mode)
            # if num >= 10:
            #     # todo: remove; for testing only
            #     break

        print(self.missing_audio)