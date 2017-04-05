import json
import threading
import time

import daemon.pidfile
import lxml.html
import tushare as ts
from lxml import etree
from pandas.compat import StringIO

from stock.common.common_func import *
from stock.common.communction import simple_publish
from stock.common.daemon_class import DaemonClass
from stock.common.time_util import load_last_date
from stock.common.variables import *


def calc_rt_tick(stock):
    outstanding = float(BASIC_INFO.outstanding_dict[stock]) * 100000000.
    large_threshold = outstanding / 3600000
    df = ts.get_today_ticks(stock)
    tick_buy = df[df['type'] == '买盘']
    tick_sell = df[df['type'] == '卖盘']
    tick_buy_large = tick_buy[tick_buy['volume'] >= large_threshold]
    tick_sell_large = tick_sell[tick_sell['volume'] >= large_threshold]
    tick_buy_small = tick_buy[tick_buy['volume'] < large_threshold]
    tick_sell_small = tick_sell[tick_sell['volume'] < large_threshold]
    v_buy_large = sum(tick_buy_large['volume'])
    v_sell_large = sum(tick_sell_large['volume'])
    v_buy_small = sum(tick_buy_small['volume'])
    v_sell_small = sum(tick_sell_small['volume'])
    v_large = v_buy_large - v_sell_large
    v_small = v_buy_small - v_sell_small
    try:
        vls_ratio = (v_buy_large + v_sell_large) / (v_buy_small + v_sell_small)
    except ZeroDivisionError:
        vls_ratio = 1
    return {'stock': stock, 'v_buy_large': v_buy_large, 'v_sell_large': v_sell_large, 'v_buy_small': v_buy_small,
            'v_sell_small': v_sell_small, 'v_large': v_large, 'v_small': v_small, 'vls_ratio': vls_ratio}


class RTTick(DaemonClass):
    """
    sub_topic: rtt_req, real_tick_update, real_tick_ctrl
    res_topic: rtt_update
    Requests: add-stock, rm-stock, exit, clear
    """

    def __init__(self):
        super().__init__(topic_sub=['rtt_req'], topic_pub='rtt_update')
        self.last_time_dict = {}
        self.monitoring_list = []
        self.msg_on_exit = 'rtt_exit'
        self.pid_file_name = 'rtt.pid'
        self.broker_pid = 0

    def mqtt_on_message(self, mqttc, obj, msg):

        payload = msg.payload.decode('utf8')
        print(msg.topic, msg.payload)
        if msg.topic == 'rtt_req':
            if payload.split('_')[0] == 'add-stock':
                self.add_stock(payload.split('_')[1])
            elif payload.split('_')[0] == 'rm-stock':
                self.rm_stock(payload.split('_')[1])
            elif payload == 'is_alive':
                self.publish('alive_%d' % os.getpid())
            elif payload == 'clear':
                self.monitoring_list = []
            elif payload == 'exit':
                self.publish(self.msg_on_exit)
                self.cancel_daemon = True
            elif payload == 'start-broker':
                if self.broker_pid == 0:
                    self.start_broker()
                else:
                    self.stop_broker()
                    self.start_broker()
            elif payload == 'stop-broker':
                if self.broker_pid != 0:
                    self.stop_broker()

        elif msg.topic == 'real_tick_ctrl':
            # real_tick_ctrl: auth_failed, closed, started_$PID
            if payload == 'auth_failed':
                self.stop_broker()
                time.sleep(1)
                self.start_broker()
            elif payload.find('started_') != -1:
                self.broker_pid = int(payload.split('_')[1])
            elif payload == 'closed':
                self.broker_pid = 0

    def add_stock(self, stock):
        if stock not in self.monitoring_list:
            if stock in BASIC_INFO.symbol_list:
                self.monitoring_list.append(stock)

    def rm_stock(self, stock):
        if stock in self.monitoring_list:
            self.monitoring_list.remove(stock)

    def stop_broker(self):
        os.system('kill -SIGINT %d' % self.broker_pid)

    def start_broker(self):
        os.system('nohup python3 -m stock.real_time.sina_lv2.broker %s &' % ' '.join(self.monitoring_list))


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/rtt.pid' %
                                                       COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path'])):

        a = RTTick()
        a.MQTT_START()
