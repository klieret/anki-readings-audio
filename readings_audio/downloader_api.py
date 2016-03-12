#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Download audio with the help of the download audio Addon.
"""

try:
    from downloadaudio.field_data import JapaneseFieldData
    from downloadaudio.downloaders import downloaders
except ImportError:
    # Abort. Anki will catch this and display the error message.
    raise ImportError("The addon readings_audio needs the addon downloadaudio to be installed!")

from .utility import timeout_wrap
# todo: really neccessary?
import romkan


def get_audio_entries(reading, timeout=10):
    """ Try to download audio files with given reading. Abort the search
    after 10 seconds.
    :param reading: the reading
    :param timeout: timeout time in seconds
    :return: a list of download entries (type name: DownloadEntry)
    """
    return timeout_wrap(get_audio_entries, args=[reading], timeout=timeout)


def _get_audio_entries(reading):
    """ Try to download audio files with given reading.
    :param reading: the reading
    :return: a list of download entries (type name: DownloadEntry)
    """
    retrieved_entries = []
    hiragana = romkan.to_hiragana(reading)
    field_data = JapaneseFieldData("", "", hiragana)
    for dloader in downloaders:
        dloader.language = "ja"
        try:
            dloader.download_files(field_data)
        except:
            continue
        retrieved_entries += dloader.downloads_list
    return retrieved_entries
