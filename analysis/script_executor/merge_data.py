# DEPENDENCY( pandas )
import multiprocessing as mp
import os
import sys

import pandas as pd

from tools.data.path_hdl import path_expand, directory_ensure, directory_exists
from tools.io import logging

msg_topic = 'data_merger'


# TODO efficient improvement

class DataMerger:
    def __init__(self, path_from, path_to, index):
        self.path_list = None
        self.index = index
        self.to = path_expand(path_to)
        directory_ensure(self.to)
        os.makedirs(self.to, exist_ok=True)
        self.validate_input_path(path_from)
        self.symbol_list = None
        self.collect_symbols()

    def validate_input_path(self, input_path):
        input_path = input_path.split("&")
        self.path_list = [path_expand(i) for i in input_path]
        for p in self.path_list:
            if not directory_exists(p):
                logging('ERROR', "path doesn't exist %s" % p)

    def collect_symbols(self):
        # TODO this function is here to get a file list in first dir of path_from, and I assume all other dirs have
        # TODO same files as the first
        path = self.path_list[0]
        self.symbol_list = os.listdir(path)

    def merge_all(self):
        pool = mp.Pool()
        for s in self.symbol_list:
            pool.apply_async(merge, args=(self.path_list, s, self.to, self.index))
        pool.close()
        pool.join()


def merge(path_list, s, to, index):
    full_path = [os.path.join(i, s) for i in path_list]
    logging(msg_topic, "MERGEING/%s" % s)
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
                result = pd.concat([result, new_data], axis=1)
                result = result.drop_duplicates(keep='last')
        result.to_csv(os.path.join(to, s))
        result = pd.read_csv(os.path.join(to, s))
        result.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
        result.to_csv(os.path.join(to, s), index=False)
    except AssertionError as e:
        logging('WARNING', "merge failed %s %s" % (s, e))


def script_exec(line):
    try:
        (path_from, path_to, index) = line.split(" ")
    except Exception as e:
        logging("ERROR", "data_merger: %s" % e)
        return
    a = DataMerger(path_from, path_to, index)
    a.collect_symbols()
    a.merge_all()


if __name__ == '__main__':
    a = DataMerger(sys.argv[1], sys.argv[2], sys.argv[3])
    a.collect_symbols()
    a.merge_all()
