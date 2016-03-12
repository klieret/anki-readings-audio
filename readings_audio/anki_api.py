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


class ReadingsAudio(object):
    def __init__(self):
        self.target_decks = ["KANJI::readings"]
        self.reading_fields = ["kunyomi", "onyomi"]
        self.audio_field = "Audio"
        self.missing_audio = set()
        self.audio_collection = AudioCollection()
        self.audio_collection.scan()
        # important: do include japanese version of ',' etc.!

    def process_single(self, note, download=False, add=True, overwrite=False):
        """Processes single note.
        :param note: The note.
        :param download: Download missing audio.
        :param add: Add the audio to the audio field on the note.
        :param overwrite: Overwrite audio field (else extend it, while leaving out duplicates)
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
                if download:
                    # todo
                    # todo: also consider the case of failed downloading
                    raise NotImplementedError
                else:
                    logger.debug("Reading {} is missing.".format(reading))
                    self.missing_audio.add(reading)
        # possibly add new audio files
        if add:
            new_paths = []
            for reading in readings:
                if reading in self.audio_collection:
                    # only add the first audio file:
                    new_paths.extend(self.audio_collection[reading][0])
                    logger.debug("Extended with sound files {}".format(self.audio_collection[reading][0]))
                else:
                    logger.warning("Still missing audio for reading {}".format(reading))
            new_paths = ["test"]
            if new_paths:
                note[self.audio_field] = extend_audio_field(note[self.audio_field], new_paths, overwrite=overwrite)
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
            self.process_single(note, download=False, add=True, overwrite=False)

        print(self.missing_audio)

    def try_downloading_audio(self, gui=True):
        for word in self.missing_audio:
            paths = get_audio_entries(word)
            print word, paths
            time.sleep(2)