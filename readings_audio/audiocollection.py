#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os.path
import os
import sys
import shutil
import collections
from downloader_api import get_audio_entries
from collections import defaultdict
import traceback

# todo: format logger
import logging
logger = logging.getLogger("test")

# todo: use unicode normalisation in some string  comparisons!
# todo: implement proper blacklist
# todo: option to skip the blacklist of audiodownloader
# todo: pickle stuff/save configuration
# todo: create database of downloaded entries for later filtering
# todo: backups

class AudioCollection(object):
    def __init__(self, media_dir=None):
        if not media_dir:
            from aqt import mw
            media_dir = mw.col.media.dir()
        self.media_dir = media_dir
        self.content = collections.defaultdict(list)  # structure: syllable: [reading: [path1, path2,...]]
        self.tmp_blacklist = set()

    @staticmethod
    def get_reading_from_name(path):
        """ Input: path/filename to an audio file.
        Checks if that audio file belongs to a reading and
        if yes, returns that reading and the number, else
        raises Exception
        :param path: string
        :return: (reading, number, max_number)
        """
        base = os.path.splitext(os.path.basename(path))[0]
        # todo: better solution thatn this hack to incorporate own readings (with less priority)
        if not base.startswith("raudio_") or base.startswith("saudio_"):
            raise ValueError
        # of course throws an exception if more than 1 '_' left
        # (feature not a bug)
        reading, number, max_number = base.replace("raudio_", "").split('_')
        if not reading.isalpha() and number.isdigit():
            raise ValueError
        return reading, number, max_number

    @staticmethod
    def _base_name(entry, reading):
        if not reading:
            raise ValueError
        return "raudio_" + reading

    def dupe_proof_names(self, dl_entries, reading):
        """ Does the following:
         1. Use _name() to get preliminary names
         2. checks the name list for duplicates and amends them by appending _1, _2 etc.
         3. Appends the extension.
        :param dl_entries: The entries
        :param reading: The reading (str)
        :return: List of modified names in the same order as entries.
        """
        name_list = [self._base_name(entry, reading) for entry in dl_entries]

        # there might be duplicates in $name_list
        # if there are $m items with an identical name
        # we want to append _$m_$i to the $i'th of those identically named items.
        # first we append _$m to every item.
        name_list_copy = name_list[:]  # deep copy of name_list that preserves the original state in the following
        for index, item in enumerate(name_list_copy):
            name_list[index] += "_{}".format(name_list_copy.count(item))
        # now we append _$i:
        counter = defaultdict(int)
        for index, item in enumerate(name_list_copy):
            counter[item] += 1
            name_list[index] += "_{}".format(counter[item])

        # finally append the extension:
        for i in range(len(dl_entries)):
            name_list[i] += dl_entries[i].file_extension
        return name_list

    def download(self, reading):
        # return number of downloaded items
        if reading in self.tmp_blacklist:
            logger.debug("Skipping {}. tmp blacklist.".fomrat(reading))
            return 0
        logger.debug(u"Dl: Downloading {}".format(reading))
        try:
            dl_entries = get_audio_entries(reading)
        except:
            e = sys.exc_info()[0]
            logger.warning(u"Failed to download: {}".format(e))
            self.tmp_blacklist.add(reading)
            traceback.print_exc()
            return 0
        name_list = self.dupe_proof_names(dl_entries, reading)
        logger.debug("Downloaded {} items".format(len(dl_entries)))
        # delete previous entries
        self.content[reading] = []
        for entry, name in zip(dl_entries, name_list):
            new_path = os.path.join(self.media_dir, name)
            # overwrites exting files!
            shutil.move(entry.file_path, new_path)
            self.content[reading].append(name)
        logger.debug("content[{}]: {}".format(reading, self.content[reading]))
        return len(dl_entries)

    def scan(self):
        logger.debug("Scan: Scanning audio collection.")
        logger.debug("Scan: #Elements before scan: {}".format(len(self.content)))
        file_names = os.listdir(self.media_dir)

        for file_name in file_names:
            try:
                reading, number, max_number = self.get_reading_from_name(file_name)
            except ValueError:
                # not one of our files
                continue
            else:
                self.content[reading].append(file_name)

        logger.debug("Scan: #Elements after scan: {}".format(len(self.content)))
        logger.debug("Scan: Sorting audio collection items.")
        # sort the paths by name
        for key in self.content:
            self.content[key] = sorted(self.content[key])
        logger.debug("Scan: Scanning done.")

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
