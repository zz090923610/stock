# -*- coding: utf-8 -*-
# DEPENDENCY( pandas )
# WINDOWS_GUARANTEED


import multiprocessing as mp
import os

import pandas as pd

from tools.data.path_hdl import path_expand, directory_ensure, directory_exists
from tools.io import logging


# USEDIR( $USER_SPECIFIED )
# REGDIR( $USER_SPECIFIED )


class DataMerger:
    """
    Merge data vertically, i.e.,
    if we set path_from='quotes1&quotes2', path_to='quotes', index='date'
    by merging:
        quotes1/0000001.csv:
            date            open    high
            2017-01-01      10      11

        quotes2/000001.csv:
            date            close    low
            2017-01-01      10.5      9
    we get:
        quotes/0000001.csv:
            date            open    high    close   low
            2017-01-01      10      11      10.5     9


    """
    def __init__(self, path_from, path_to, index):
        """
        This class is the handle to merge multiple same-shaped csv(s) together.
        :param path_from: specify multiple input directories, will apply merge to every file in directories.
        :param path_to: new directory to store merged files.
        :param index: rows among different csv(s) with same index value will be merged to same row in merged files.
        """
        self.msg_from = 'DATA_MERGER'
        self.directory_list = None
        self.index = index
        self.to = path_expand(path_to)
        directory_ensure(self.to)
        os.makedirs(self.to, exist_ok=True)
        self.expand_path_list(path_from)
        self.symbol_filename_list = None  # [000001.csv, 000155.csv]
        self.collect_symbols()

    def expand_path_list(self, input_path):
        """
        generate a list of full paths from input_path string
        :param input_path:  path1&path2&path3
        """
        input_path = input_path.split("&")
        self.directory_list = [path_expand(i) for i in input_path]
        for p in self.directory_list:
            if not directory_exists(p):
                logging(self.msg_from, "[ ERROR ] Specified input directory doesn't exist %s" % p)

    def collect_symbols(self):
        """
        generate a list of symbol file members in input directories.
        IMPORTANT: I assume all other input dirs to merge have same files as the first
        """
        path = self.directory_list[0]
        self.symbol_filename_list = os.listdir(path)

    def merge_all(self):
        """
        do the merge, parallelly.
        """
        pool = mp.Pool()
        for symbol_filename in self.symbol_filename_list:
            pool.apply_async(merge, args=(self.directory_list, symbol_filename, self.to, self.index, self.msg_from))
        pool.close()
        pool.join()


def merge(path_list, symbol_filename, output_path, index, msg_from):
    """
    apply single operation of merge, for one file identifier in all input directories.
    :param path_list:           input path list, [] of string
    :param symbol_filename:     file identifier, string
    :param output_path:         output path,    string
    :param index:               based on which column, string
    :param msg_from:            msg source for logging
    :return:
    """
    full_path = [os.path.join(i, symbol_filename) for i in path_list]
    result = None
    try:
        for p in full_path:
            if result is None:
                result = pd.read_csv(p)
                if index is not None:
                    result = result.set_index(index)
            else:
                new_data = pd.read_csv(p)
                new_data = new_data.set_index(index)
                new_column = []
                for k in new_data.columns.values:
                    if k not in list(result.columns.values):
                        new_column.append(k)
                new_data = new_data[new_column]
                result = pd.concat([result, new_data], axis=1, sort=False)
                result = result.drop_duplicates(keep='last')
        result.to_csv(os.path.join(output_path, symbol_filename))
        result.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
        result.index.names = ['date']
        result.to_csv(os.path.join(output_path, symbol_filename))
        logging(msg_from, "[ INFO ] %s merged" % symbol_filename)
    except AssertionError as e:
        logging(msg_from, "[ ERROR ] merge failed %s %s" % (symbol_filename, e))


# CMDEXPORT ( MERGE {path_from} {path_to} {index} ) cmd_merge
def cmd_merge(path_from, path_to, index):
    """
    Export this function to Control Framework, a control command like:
        MERGE day_quotes/china&qa/ma&qa/candle_stick_shape_analysis&qa/inflow summary date
    can be added to .ctrl batch file to save some work.

    :param path_from: specify multiple input directories, will apply merge to every file in directories.
    :param path_to: new directory to store merged files.
    :param index: rows among different csv(s) with same index value will be merged to same row in merged files.
    """
    a = DataMerger(path_from, path_to, index)
    a.collect_symbols()
    a.merge_all()
