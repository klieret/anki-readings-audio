#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aqt import mw
import romkan
from .downloader_api import get_audio_entries
import time
from .audiocollection import AudioCollection
from .field_operations import split_readings


class ReadingsAudio():
    def __init__(self):
        self.target_decks = ["KANJI::readings"]
        self.reading_fields = ["kunyomi", "onyomi"]
        self.missing_audio = []
        self.audio_collection = AudioCollection()
        self.audio_collection.scan()
        # important: do include japanese version of ',' etc.!

    def process_single(self, note, download=False, add=True, overwrite=True):
        """Processes single note.
        :param note: The note.
        :param download: Download missing audio.
        :param add: Add the audio to the audio field on the note.
        :param overwrite: Overwrite audio field (else extend it, while leaving out duplicates)
        :return: None
        """
        readings = []
        audio_paths = []
        for field in self.reading_fields:
            if field in note.keys():
                readings.extend(split_readings(note[field]))
        for reading in readings:
            if reading in self.audio_collection:
                audio_paths.append(self.audio_collection[reading])
            else:
                if download:
                    # todo
                    pass
                else:
                    self.missing_audio.append(reading)
        if add:
            for audio_path in audio_paths:
                # todo
                pass

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