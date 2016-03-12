#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aqt import mw
import re
import romkan
from .downloader_api import get_audio_entries
import time
from .audiocollection import AudioCollection


def get_audio_field_entry_from_path(path):
    # Entry looks like this: '[sound:帰還_きかん.mp3]'
    return u"[sound:{}]".format(path)


def get_paths_from_audio_field(audio_field):
    regex = re.compile("\[sound:([^\[\]]*)\]")
    return regex.findall(audio_field)


def extend_audio_field(old_field_string, new_paths, remove_duplicates=True, new_entries_first=False):
    # convert both inputs to lists of strings [sound:....]
    old_paths = get_paths_from_audio_field(old_field_string)
    # remove duplicated paths:
    if remove_duplicates:
        for old_path in old_paths:
            if old_path in new_paths:
                # remove paths (even if occuring multiple times)
                new_entries = [path for path in new_paths if path != old_path]
    # build audio field entries:
    new_audio_field_entries = [get_audio_field_entry_from_path(path) for path in new_paths]
    old_audio_field_entries = [get_audio_field_entry_from_path(path) for path in old_paths]
    # return in right order:
    if new_entries_first:
        return ''.join(new_audio_field_entries) + ''.join(old_audio_field_entries)
    else:
        return ''.join(old_audio_field_entries) + ''.join(new_audio_field_entries)


class ReadingsAudio():
    def __init__(self):
        self.target_decks = ["KANJI::readings"]
        self.reading_fields = ["kunyomi", "onyomi"]
        self.missing_audio = []
        self.audio_collection = AudioCollection()
        self.audio_collection.scan()
        # important: do include japanese version of ',' etc.!
        self.readings_delimeters = [u',', u"、", u';']

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
                readings.extend(self.split_readings(note[field]))
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
        # since we are splitting with respect to multiple delimeters (e.g. ',', ';' etc.)
        # build the regex ",|;|..." etc. and use re..split to do the splitting.
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