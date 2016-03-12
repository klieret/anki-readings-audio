#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os.path
import os
import shutil
import collections
from downloader_api import get_audio_entries


class AudioCollection(object):
    def __init__(self, media_dir=None):
        if not media_dir:
            from aqt import mw
            media_dir = mw.col.media.dir()
        self.media_dir = media_dir
        self.content = collections.defaultdict(list)  # structure: syllable: [reading: [path1, path2,...]]

    @staticmethod
    def get_reading_from_name(path):
        """ Input: path/filename to an audio file.
        Checks if that audio file belongs to a reading and
        if yes, returns that reading and the number, else
        raises Exception
        :param path: string
        :return: (reading, number)
        """
        base = os.path.splitext(os.path.basename(path))[0]
        if not base.startswith("raudio_"):
            raise ValueError
        # of course throws an exception if more than 1 '_' left
        # (feature not a bug)
        reading, number = base.replace("raudio_", "").split('_')
        if not reading.isalpha() and number.isdigit():
            raise ValueError
        return reading, number

    @staticmethod
    def _name(entry, reading):
        if not reading:
            raise ValueError
        return "raudio_" + reading

    def dupe_proof_names(self, dl_entries, reading):
        """ Does the following:
         1. Use _name() to get preliminary names
         2. checks the list for duplicates and amends them by appending _1, _2 etc.
        :param dl_entries: The entries
        :param reading: The reading (str)
        :return: Entries with modified names
        """
        # overwrite the default names with the names as returned
        # from _name
        for i in range(len(dl_entries)):
            dl_entries[i].base_name = self._name(dl_entries[i], reading)
        # if there are duplicates, enumerate them (also add _0 for the first name)
        for i in range(len(dl_entries)):
            duplicates = 0
            for j in range(len(dl_entries)):
                if dl_entries[i].base_name == dl_entries[j].base_name:
                    dl_entries[j].base_name += str(duplicates)
                    duplicates += 1
        return dl_entries

    def download(self, reading):
        # return number of downloaded items
        try:
            entries = self.dupe_proof_names(get_audio_entries(reading), reading)
        except:
            return 0
        # delete previos entries
        self.content[reading] = []
        for entry in entries:
            new_path = os.path.join(self.media_dir, entry.base_name + entry.file_extension)
            # overwrites exting files!
            shutil.move(entry.file_path, new_path)
            self.content[reading].append(os.path.basename(new_path))

    def scan(self):
        file_names = os.listdir(self.media_dir)
        for file_name in file_names:
            try:
                reading, number = self.get_reading_from_name(file_name)
                self.content[reading].append(file_name)
            except ValueError:
                # not one of our files
                continue
        # sort the paths by name
        for key in self.content:
            self.content[key] = sorted(self.content[key])

    def __contains__(self, item):
        if not isinstance(item, str):
            raise ValueError
        return item in self.content

    def __getitem__(self, item):
        return self.content[item]


if __name__ == "__main__":
    # for testing purposes
    c = AudioCollection(media_dir=os.path.expanduser("~/Anki/fuchurMain/collection.media"))
    c.scan()
