# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED
import os
import pickle

from tools.data.path_hdl import path_expand, directory_ensure


# DIRREG( translate )
class TranslateHdl:
    """
    When writting scripts you may define many cols and choose to save them to csv. However these cols only consist
    letters, ditits and _ which may not good enough to present. To solve this problem you can add TRANSLATE commands to
    add proper utf8 output format for col names you defined, and such translate dicts are handled here.
    """
    def __init__(self):
        self.dict = {}
        self.order_list = []
        self.trans_dir = path_expand('translate')
        directory_ensure(self.trans_dir)

    def add_translation(self, line):
        """
        add translation into diction from command string
        :param line:    command string, string
        """
        # parse line, two conditions
        if ':' in line:
            trans_list = line.split(", ")  # FIXME future implementation
            for i in trans_list:
                (k, v) = i.split(":")
                if k not in self.dict.keys():
                    self.dict[k] = v
                    if k not in self.order_list:
                        self.order_list.append(k)
        else:
            trans_list = line.split(" ")
            if len(trans_list) == 2:
                if trans_list[0] not in self.dict.keys():
                    self.dict[trans_list[0]] = trans_list[1]
                    if trans_list[0] not in self.order_list:
                        self.order_list.append(trans_list[0])

    def clear(self):
        """
        clear all translations
        """
        self.dict.clear()

    def load(self):
        try:
            with open('%s' % (os.path.join(self.trans_dir, "translation.pickle")), 'rb') as f:
                self.dict = pickle.load(f)
        except FileNotFoundError:
            self.dict = {}

        try:
            with open('%s' % (os.path.join(self.trans_dir, "key_order.pickle")), 'rb') as f:
                self.order_list = pickle.load(f)
        except FileNotFoundError:
            self.order_list = []

    def save(self):
        with open('%s' % (os.path.join(self.trans_dir, "translation.pickle")), 'wb') as f:
            pickle.dump(self.dict, f, -1)
        with open('%s' % (os.path.join(self.trans_dir, "key_order.pickle")), 'wb') as f:
            pickle.dump(self.order_list, f, -1)
