# -*- coding: utf-8 -*-
# DEPENDENCY( pandas )
# WINDOWS_GUARANTEED


import os

import pandas as pd

from tools.data.path_hdl import path_expand, directory_ensure
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import logging

calendar = MktCalendar()


# USEDIR( $USER_SPECIFIED )
# REGDIR( $USER_SPECIFIED )


class SingleDataMerger:
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

    def __init__(self, files_input, files_output, index, outcols, sortby):
        """
        This class is the handle to merge multiple same-shaped csv(s) together.
        :param files_input: specify multiple input files.
        :param files_output: new directory to store merged files.
        :param index: rows among different csv(s) with same index value will be merged to same row in merged files.
        :outcols index: columns should be outputed
        """
        self.msg_from = 'SINGLE_DATA_MERGER'
        self.directory_list = None
        self.index = index
        self.to = path_expand(files_output)
        directory_ensure(os.path.dirname(self.to))
        self.files_input = files_input.split("&")
        self.files_input = [path_expand(i) for i in self.files_input]
        if sortby == "None":
            self.sortby = None
        else:
            self.sortby = sortby
        if outcols == "ALL":
            self.outcols = None
        else:
            self.outcols = outcols.split("&")

    def merge(self):
        result = None
        try:
            for p in self.files_input:
                if result is None:
                    result = pd.read_csv(p)
                    if self.index is not None:
                        result = result.set_index(self.index)
                else:
                    new_data = pd.read_csv(p)
                    new_data = new_data.set_index(self.index)
                    new_column = []
                    for k in new_data.columns.values:
                        if k not in list(result.columns.values):
                            new_column.append(k)
                    new_data = new_data[new_column]
                    result = pd.concat([result, new_data], axis=1)
                    result = result.drop_duplicates(keep='last')
            result['symbol'] = result.index
            if self.sortby is not None:
                column = self.sortby.split("&")[0]
                order = True if self.sortby.split("&")[1] == "True" else False
                print(column, order)
                result.sort_values(by=column, ascending=order, inplace=True)
            if self.outcols is None:
                result.to_csv(self.to, index=False)
            else:
                result[self.outcols].to_csv(self.to, index=False)
            logging(self.msg_from, "[ INFO ] %s merged" % self.to)
        except AssertionError as e:
            logging(self.msg_from, "[ ERROR ] merge failed %s %s" % (self.to, e))


# CMDEXPORT ( SINGLEMERGE {files_input} {files_output} {index} {outcols} {sortby} ) cmd_single_merge
def cmd_single_merge(files_input, files_output, index, outcols, sortby):
    a = SingleDataMerger(calendar.expand_date_in_str(files_input), calendar.expand_date_in_str(files_output), index, outcols, sortby)
    a.merge()
