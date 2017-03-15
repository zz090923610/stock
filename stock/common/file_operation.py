import csv
import os
import pickle
import resource
import subprocess
import sys
import threading
import pandas as pd
from stock.common.variables import COMMON_VARS_OBJ

max_rec = 0x100000
resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
sys.setrecursionlimit(max_rec)

lock = threading.Lock()


def logging(msg, timestamp='', silence=False):
    if not silence:
        print(msg, file=sys.stderr)
    lock.acquire()
    fo = open('%s/log.txt' % COMMON_VARS_OBJ.stock_data_root, "a")
    if timestamp == '':
        print('%s' % msg, file=fo)
    else:
        print('[%s] %s' % (timestamp, msg), file=fo)
    fo.close()
    lock.release()


def load_pickle(path):
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError as e:
        logging('load_pickle: File not found %s' % path)
        return None


def save_pickle(path, obj):
    try:
        target_dir, file_name = os.path.split(path)
    except AttributeError:
        logging(path)
        raise
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    try:
        with open(path, 'wb') as f:
            pickle.dump(obj, f, -1)
    except Exception as e:
        logging(e, silence=True)


def load_csv(path, col_type=None):
    if col_type is None:
        col_type = {}
    final_list = []
    try:
        with open(path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # noinspection PyTypeChecker
                if len(col_type.keys()) > 0:
                    try:
                        for key in col_type.keys():
                            if col_type[key] == 'float':
                                row[key] = float(row[key])
                            elif col_type[key] == 'int':
                                row[key] = int(row[key])
                        final_list.append(row)
                    except ValueError as e:
                        logging('Loading csv error: %s %s' % (e, '%s %r' % (path, row)))
                else:
                    final_list.append(row)
            for row in reader:
                final_list.append(row)
        return final_list
    except FileNotFoundError:
        return None


def mkdirs(symbol_list):
    for a_dir in COMMON_VARS_OBJ.DIR_LIST:
        subprocess.call('mkdir -p %s' % a_dir, shell=True)
    if symbol_list is not None:
        for s_code in symbol_list:
            subprocess.call('mkdir -p %s/tick_data/%s' % (COMMON_VARS_OBJ.stock_data_root, s_code), shell=True)


def list2csv(data_list, out_file, col_order=None, add_index=False):
    if col_order is None:
        col_order = []
    b = pd.DataFrame(data_list)
    if len(col_order) == 0:
        b.to_csv(out_file, index=add_index)
    else:
        b[col_order].to_csv(out_file, index=add_index)
