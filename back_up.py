#!/usr/bin/python3
import os
import tarfile
import pylzma
import re
from multiprocessing.pool import Pool

import sys

import shutil

from common_func import *


def create_tar_file_of(folder):
    folder = os.path.abspath(folder)
    folder = re.sub('/*$', '', folder)
    cwd = os.getcwd()
    basename_of_dir = os.path.basename(folder)
    os.chdir("%s/.." % folder)
    file_list = os.listdir(folder)
    tar = tarfile.open("%s.tar" % basename_of_dir, "w")
    os.chdir(folder)
    for name in file_list:
        tar.add('%s' % name)
    tar.close()
    os.chdir(cwd)


def extract_directory_from_tar(f, out_dir):
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir, mode=0o777)
    os.chdir(out_dir)
    tar = tarfile.open(f, "r")
    tar.extractall()


def create_pylzma_file(i_file):
    with open(i_file, 'rb') as iFile:
        iData = iFile.read()
    oData = pylzma.compress(iData, algorithm=0)
    with open('%s.pylzma' % i_file, 'wb') as oFile:
        oFile.write(oData)


def uncompress_pylzma_file(i_file):
    with open(i_file, 'rb') as iFile:
        iData = iFile.read()
    oData = pylzma.decompress(iData)
    o_file = re.sub('\.pylzma$', '', i_file)
    with open('%s' % o_file, 'wb') as oFile:
        oFile.write(oData)


def backup_tick_data_for_stock(stock):
    create_tar_file_of('../stock_data/tick_data/%s' % stock)
    create_pylzma_file('../stock_data/tick_data/%s.tar' % stock)
    os.rename('../stock_data/tick_data/%s.tar.pylzma' % stock, '../stock_data/back_up/tick_data/%s.tar.pylzma' % stock)
    os.remove('../stock_data/tick_data/%s.tar' % stock)


def backup_tick_data():
    p = Pool(8)
    rs = p.imap_unordered(backup_tick_data_for_stock, BASIC_INFO.symbol_list)
    p.close()  # No more work
    list_len = len(BASIC_INFO.symbol_list)
    while True:
        completed = rs._index
        if completed == list_len:
            break
        sys.stdout.write('%d/%d\r' % (completed, list_len))
        sys.stdout.flush()
        time.sleep(2)
    sys.stdout.write('%d/%d\r' % (completed, list_len))
    sys.stdout.flush()


def _restore_tick_data_for_stock(stock):
    shutil.copy2('../stock_data/back_up/tick_data/%s.tar.pylzma' % stock,
                 '../stock_data/tick_data/%s.tar.pylzma' % stock)
    uncompress_pylzma_file('../stock_data/tick_data/%s.tar.pylzma' % stock)
    os.remove('../stock_data/tick_data/%s.tar.pylzma')
    extract_directory_from_tar('../stock_data/tick_data/%s.tar' % stock, '../stock_data/tick_data/%s' % stock)
    os.remove('../stock_data/tick_data/%s.tar' % stock)


def restore_tick_data():
    mkdirs(BASIC_INFO.symbol_list)
    p = Pool(POOL_SIZE)
    rs = p.imap_unordered(_restore_tick_data_for_stock, BASIC_INFO.symbol_list)
    p.close()  # No more work
    list_len = len(BASIC_INFO.symbol_list)
    while True:
        completed = rs._index
        if completed == list_len:
            break
        sys.stdout.write('Getting %.3f\n' % (completed / list_len))
        sys.stdout.flush()
        time.sleep(2)
    sys.stdout.write('Getting 1.000\n')
    sys.stdout.flush()


def back_up_daily_data():
    print('backup daily data')
    create_tar_file_of('../stock_data/data')
    print('compressing')
    create_pylzma_file('../stock_data/data.tar')
    os.rename('../stock_data/data.tar.pylzma', '../stock_data/back_up/data.tar.pylzma')
    os.remove('../stock_data/data.tar')


def restore_daily_data():
    shutil.copy2('../stock_data/back_up/data.tar.pylzma', '../stock_data/data.tar.pylzma')
    uncompress_pylzma_file('../stock_data/back_up/data.tar.pylzma')
    os.remove('../stock_data/data.tar.pylzma')
    extract_directory_from_tar('../stock_data/back_up/data.tar', '../stock_data/data')
    os.remove('../stock_data/back_up/data.tar')


if __name__ == '__main__':
    if sys.argv[1] == '-b':
        back_up_daily_data()
        backup_tick_data()
    elif sys.argv[1] == '-r':
        restore_daily_data()
        restore_tick_data()
