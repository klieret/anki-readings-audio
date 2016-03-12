#!/usr/bin/env python
# -*- coding: utf-8 -*-

# todo: use try/except
from downloadaudio.field_data import JapaneseFieldData
from downloadaudio.downloaders import downloaders
import time
import signal
import romkan


def timeout(func, args=(), kwargs={}, timeout_duration=10, default=None):
    import signal

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError as exc:
        print("Timeout!")
        result = default
    finally:
        signal.alarm(0)

    return result


def get_path_to_audio(word):
    return timeout(get_path_to_audio, args=[word], timeout_duration=10)


def _get_path_to_audio(word):
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
    file_paths = []
    for entry in retrieved_entries:
        entry.process()
        file_paths.append(entry.file_path)
    return file_paths