#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from downloadaudio.field_data import JapaneseFieldData
    from downloadaudio.downloaders import downloaders
except ImportError:
    # Abort. Anki will catch this and display the error message.
    raise ImportError("The addon readings_audio needs the addon downloadaudio to be installed!")

import time
import signal

# todo: really neccessary?
import romkan


def timeout_wrap(func, args=(), kwargs={}, timeout=10):
    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)

    try:
        return func(*args, **kwargs)
    except TimeoutError:
        raise RuntimeError
    finally:
        signal.alarm(0)


def get_audio_entries(word, timeout=10):
    return timeout_wrap(get_audio_entries, args=[word], timeout=timeout)


def _get_audio_entries(word):
    retrieved_entries = []
    hiragana = romkan.to_hiragana(word)
    field_data = JapaneseFieldData("", "", hiragana)
    for dloader in downloaders:
        dloader.language = "ja"
        try:
            dloader.download_files(field_data)
        except:
            continue
        retrieved_entries += dloader.downloads_list
    return retrieved_entries
