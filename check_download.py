#!/usr/bin/env python3
import pickle

import sys

import time


def load_finished_stock_list(group):
    try:
        with open('../stock_data/finished_group_%s.pickle' % group, 'rb') as f:
            return pickle.load(f)
    except:
        return []

while True:
    a = []
    for grp in range(0, 32):
        a += load_finished_stock_list(grp)
    sys.stdout.write('%d %.3f\r' % (len(a), len(a) / float(3003)))
    sys.stdout.flush()
    time.sleep(1)