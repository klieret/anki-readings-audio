#!/usr/bin/env python
# -*- coding: utf-8 -*-

# todo: documentation

class AddMode(object):
    def __init__(self):
        self.option_names = ["enabled", "mode", "remove_broken", "new_first"]
        # set all options to None
        for option in self.option_names:
            self.__setattr__(option, None)

    def set_defaults(self):
        self.enabled = True
        self.mode = "extend"  # options: extend, overwrite, overwrite_empty
        self.remove_broken = False # todo: not yet implemented
        self.new_first = False

    def check_options(self):
        for option in self.option_names:
            if self.__getattribute__(option) is None:
                raise ValueError
        if self.mode not in ["extend", "overwrite", "overwrite_empty"]:
            raise ValueError

class DownloadMode(object):
    def __init__(self):
        self.option_names = ["enabled", "ignore_blacklist", "ignore_redownload"]
        # set all options to None
        for option in self.option_names:
            self.__setattr__(option, None)

    def set_defaults(self):
        self.enabled = True
        self.ignore_blacklist = False
        self.ignore_redownload = False

    def check_options(self):
        for option in self.option_names:
            if self.__getattribute__(option) is None:
                raise ValueError

class CrawlingMode(object):
    def __init__(self, add_mode=AddMode(), download_mode=DownloadMode()):
        self.add = add_mode
        self.download = download_mode

    def check_options(self):
        self.add.check_options()
        self.download.check_options()