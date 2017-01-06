#!/usr/bin/env python3
import os
import pickle
import subprocess
from pathlib import Path
from time import sleep
import time
from datetime import datetime
from termcolor import colored
import pytz  # $ pip install pytz
import sys
import tushare as ts
import signal
from tzlocal import get_localzone  # $ pip install tzlocal
import os.path
import csv
from multiprocessing import Pool

# get local timezone
local_tz = get_localzone()
china_tz = pytz.timezone('Asia/Shanghai')


def get_one(stock):
    print('getting %s' %stock)
    my_file = Path('../stock_data/data/%s.csv' % stock)
    if my_file.is_file():
        return
    data = ts.get_h_data(stock)
    data.to_csv('../stock_data/data/%s.csv' % stock)

#print("Fetching Basic Info")
#df = ts.get_stock_basics()
#df.to_csv('../stock_data/basic_info.csv')
#symbol_list = df.index.values
#
symbol_list = []
with open('../stock_data/basic_info.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        symbol_list.append(row['code'])

symbol_len = len(symbol_list)



p = Pool()
rs = p.imap_unordered(get_one, symbol_list)
p.close()  # No more work
list_len = len(symbol_list)
while True:
    completed = rs._index
    if completed == list_len:
        break
    sys.stdout.write('Getting %.3f\n' % (completed / list_len))
    sys.stdout.flush()
    sleep(2)
sys.stdout.write('Getting 1.000\n')
sys.stdout.flush()



