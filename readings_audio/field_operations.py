#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" In this module defines function to perform some operations on the content of two kinds of (Anki) fields:
1. Audio field: The field which contains the paths to audio files and is used for the play button addon etc.
    the [sound:...] tag is referred to by 'audio_field_entry'
2. Reading field: A field that holds readings.
"""

import re
import os.path
import romkan
from .utility import remove_duplicates, remove_intersection


def get_audio_field_entry_from_path(path):
    """ Takes a path to an audio file and creates an audio field entry
    from it.
    :param path: input path (str)
    :return: audio field entry (str)
    """
    # Entry looks like this: '[sound:帰還_きかん.mp3]'
    return u"[sound:{}]".format(path)


def get_paths_from_audio_field(audio_field):
    """ Takes an audio field and extracts all paths to (audio) files.
    :param audio_field: Content of the audio field
    :return:list of paths to (audio) files.
    """
    regex = re.compile("\[sound:([^\[\]]*)\]")
    return regex.findall(audio_field)


def extend_audio_field(old_audio_field, new_paths, do_remove_duplicates=True, new_entries_first=False):
    """ Takes the content of an audio field and extends it with paths for more audio files.
    Furthermore:
    1. Any text in between audio field entries is removed
    2. The paths to the audio files are normalized
    3. Duplicates are removed if do_remove_duplicates == True
    :param old_audio_field: The content of the old audio field.
    :param new_paths: Paths to audio files that we want to add to the audio field.
    :param do_remove_duplicates: Do we want to remove duplicate entries?
    :param new_entries_first: Should the new entries (possibly with removed duplicates)
    :return: New string for the audio field
    """
    # convert both inputs to lists of strings [sound:....]
    old_paths = get_paths_from_audio_field(old_audio_field)

    # normalise paths
    new_paths = [os.path.normpath(path) for path in new_paths]
    old_paths = [os.path.normpath(path) for path in old_paths]

    # remove duplicated paths:
    if do_remove_duplicates:
        # remove internal duplicates:
        new_paths = remove_duplicates(new_paths)
        old_paths = remove_duplicates(old_paths)
        # remove intersection:
        new_paths = remove_intersection(old_paths, new_paths)

    # build audio field entries:
    new_audio_field_entries = [get_audio_field_entry_from_path(path) for path in new_paths]
    old_audio_field_entries = [get_audio_field_entry_from_path(path) for path in old_paths]

    # return them in right order:
    if new_entries_first:
        return ''.join(new_audio_field_entries) + ''.join(old_audio_field_entries)
    else:
        return ''.join(old_audio_field_entries) + ''.join(new_audio_field_entries)


def split_readings(string, delimeters=(u',', u"、", u';')):
    """ Takes input string and does 5 things:
    1. Split the string on the delimeters self.delimeters
    2. Removed all non-hiragana-katakana letters
    3. Removes whitespace and all empty strings
    4. Converts all kana to romaji (hepburn transcription)
    5. Converts unicode strings to strings (since now only romaji)
    returns this as a list.
    :param string: Input string, containing readings as hiragana/katakana, separated by delimters.
    :param delimeters: delimeters like ',' and ';' which separate differnt readings in $string
    :return: List of the readings.
    """
    # since we are splitting with respect to multiple delimeters (e.g. ',', ';' etc.)
    # build the regex ",|;|..." etc. and use re..split to do the splitting.
    regex = '|'.join(map(re.escape, tuple(delimeters)))
    splitted = re.split(regex, string)
    kana_only = [''.join(re.findall(u"[\u3040-\u30ff]", split)) for split in splitted]
    no_whitespace = [kana.strip() for kana in kana_only if kana.strip()]
    return [str(romkan.to_hepburn(kana)) for kana in no_whitespace]
