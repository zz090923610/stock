#!/usr/bin/env python3
import json
import multiprocessing
import subprocess
import threading
from multiprocessing import Pool
from threading import Thread

import progressbar
import sys
import daemon.pidfile
import time

from stock.common.common_func import *
from stock.common.communction import simple_publish
from stock.common.time_util import load_last_date
from stock.data.data_rt_sina import get_rt_data_dict, get_pd_from_rt_data_dict_of_stock
import tushare as ts
import paho.mqtt.client as mqtt
from stock.data.new_get_tick_data import download_tick
TODAY = load_last_date()


# noinspection PyShadowingNames
class DailyDataFetcher:
    def __init__(self, fetch_type='all', show_bar=False):
        self.RT_DICT = {}
        self.fetch_type = fetch_type
        self.show_bar = show_bar
        if self.show_bar:
            self.bar = progressbar.ProgressBar(max_value=len(BASIC_INFO.symbol_list), redirect_stdout=True)
            self.bar_cnt_lock = multiprocessing.Lock()

    def adding_bar_cnt(self, bar_cnt_path):
        self.bar_cnt_lock.acquire()
        # noinspection PyBroadException
        try:
            with open(bar_cnt_path, 'rb') as f:

                cnt = int(pickle.load(f)['cnt'])
        except:
            cnt = 0
        cnt += 1
        with open(bar_cnt_path, 'wb') as f:
            pickle.dump({'cnt': cnt}, f)
        self.bar.update(cnt)
        self.bar_cnt_lock.release()

    def _get_all_data_for_one_stock(self, stock):
        start = max(BASIC_INFO.time_to_market_dict[stock], COMMON_VARS_OBJ.START_DATE)
        df = ts.get_k_data(stock, autype='qfq', start=start, end=TODAY)
        if df is None:
            raise EOFError
        if TODAY not in df.date.tolist():
            rt_today = get_pd_from_rt_data_dict_of_stock(self.RT_DICT, stock)
            if rt_today is not None:
                if int(rt_today['volume'][0]) > 0:
                    df = df.append(rt_today, ignore_index=True)
        df = df.drop_duplicates('date', keep='last')
        df = df.sort_values(by='date', ascending=True)
        df = df.reset_index()
        df = df.drop(df[df['date'] == '2016-11-25'].index)
        df = df.round({'open': 3, 'high': 3, 'close': 3, 'low': 3})
        df.volume = df.volume.astype(int)
        cols = ['date', 'open', 'high', 'close', 'low', 'volume']
        df[cols].to_csv('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock), index=False)
        if self.show_bar:
            self.adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')
        simple_publish('daily_data_update', '%s_all' % stock)
        return stock

    def get_all_data_for_all_stock(self):
        simple_publish('daily_data_update', 'start_%s' % self.fetch_type)
        self.RT_DICT = get_rt_data_dict()
        if self.show_bar:
            subprocess.call('rm /tmp/stock_daily_bar_cnt.pickle 2>/dev/null', shell=True)
            with open('/tmp/stock_daily_bar_cnt.pickle', 'wb') as f:
                pickle.dump({'cnt': 0}, f)
            subprocess.call('mkdir -p %s/data' % COMMON_VARS_OBJ.stock_data_root, shell=True)
        finished_stock_list = []
        pool = mp.Pool(16)
        if self.fetch_type == 'all':
            print("Getting Daily Data")
            for i in BASIC_INFO.symbol_list:
                pool.apply_async(self._get_all_data_for_one_stock, args=(i,), callback=finished_stock_list.append)
        else:
            print("Updating Daily Data %s" % TODAY)
            for i in BASIC_INFO.symbol_list:
                pool.apply_async(self._get_update_for_one_stock, args=(i,), callback=finished_stock_list.append)
        pool.close()
        pool.join()
        subprocess.call('rm /tmp/stock_daily_bar_cnt.pickle 2>/dev/null', shell=True)
        simple_publish('daily_data_update', 'finished_%s' % self.fetch_type)

    def _get_update_for_one_stock(self, stock):
        try:
            df = pd.read_csv('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock))
        except FileNotFoundError:
            self._get_all_data_for_one_stock(stock)
            return
        if TODAY in df.date.tolist():
            if self.show_bar:
                self.adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')
            simple_publish('daily_data_update', '%s_update' % stock)
            return
        rt_today = get_pd_from_rt_data_dict_of_stock(self.RT_DICT, stock)
        if rt_today is not None:
            if rt_today is not None:
                if int(rt_today['volume'][0]) > 0:
                    df = df.append(rt_today, ignore_index=True)
        df = df.sort_values(by='date', ascending=True)
        df = df.reset_index()
        cols = ['date', 'open', 'high', 'close', 'low', 'volume']
        df = df.drop_duplicates('date', keep='last')
        df = df.drop(df[df['date'] == '2016-11-25'].index)
        df = df.round({'open': 3, 'high': 3, 'close': 3, 'low': 3})
        df.volume = df.volume.astype(int)
        df[cols].to_csv('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock), index=False)
        if self.show_bar:
            self.adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')
        simple_publish('daily_data_update', '%s_update' % stock)


def get_daily_data_signal_daemon_callable(fetch_type='update'):
    if not os.path.isdir('%s/data' % COMMON_VARS_OBJ.stock_data_root):
        os.makedirs('%s/data' % COMMON_VARS_OBJ.stock_data_root)
    b = DailyDataFetcher(fetch_type=fetch_type, show_bar=False)
    b.get_all_data_for_all_stock()


# noinspection PyMethodMayBeStatic
class DataDaemon:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.on_subscribe = self.mqtt_on_subscribe
        self.client.on_publish = self.mqtt_on_publish
        self.client.connect("localhost", 1883, 60)
        self.mqtt_topic_sub = ["time_util_update", "data_req"]
        self.mqtt_topic_pub = "data_update"
        self.cancel_daemon = False
        self.dates = {'last_trade_day_cn': load_last_date('last_trade_day_cn'),
                      'last_day_cn': load_last_date('last_day_cn')}
        print(self.dates)

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        for t in self.mqtt_topic_sub:
            mqttc.subscribe(t)
        self.publish('alive_%d' % os.getpid())

    def mqtt_on_message(self, mqttc, obj, msg):
        if msg.topic == "time_util_update":
            payload = json.loads(msg.payload.decode('utf8'))
        elif msg.topic == "data_req":
            payload = msg.payload.decode('utf8')
            if payload == 'is_alive':
                self.publish('alive_%d' % os.getpid())
            elif payload == 'daily_update_all':

                t = Thread(target=get_daily_data_signal_daemon_callable, kwargs={'fetch_type': 'all'})
                t.start()
            elif payload == 'daily_update':
                t = Thread(target=get_daily_data_signal_daemon_callable, kwargs={'fetch_type': 'update'})
                t.start()
            elif payload == 'tick_update':
                t = Thread(target=download_tick)
                t.start()
            elif payload == 'exit':
                self.publish('data_hdl exit')
                self.cancel_daemon = True

    def publish(self, msg, qos=1):
        (result, mid) = self.client.publish(self.mqtt_topic_pub, msg, qos)

    def mqtt_on_publish(self, mqttc, obj, mid):
        pass

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        pass

    def mqtt_on_log(self, mqttc, obj, level, string):
        pass

    def MQTT_CANCEL(self):
        self.client.loop_stop(force=True)

    def MQTT_START(self):
        threading.Thread(target=self.client.loop_start).start()

    def daemon_main(self):
        self.MQTT_START()
        while not self.cancel_daemon:
            pid_dir = COMMON_VARS_OBJ.DAEMON['news_hdl']['pid_path']
            if not os.path.isdir(pid_dir):
                os.makedirs(pid_dir)
            time.sleep(2)
        self.MQTT_CANCEL()


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['news_hdl']['pid_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/data_hdl.pid' % COMMON_VARS_OBJ.DAEMON['news_hdl']['pid_path'])):
        a = DataDaemon()
        a.daemon_main()


if __name__ == "__main__":
    fetch_type = 'update'
    if len(sys.argv) == 0:
        a = DailyDataFetcher(fetch_type=fetch_type, show_bar=True)
        a.get_all_data_for_all_stock()
    for loop in range(1, len(sys.argv)):
        if sys.argv[loop] == '--all':
            fetch_type = 'all'
        elif sys.argv[loop] == '--update':
            fetch_type = 'update'
        a = DailyDataFetcher(fetch_type=fetch_type, show_bar=True)
        a.get_all_data_for_all_stock()
