#!/usr/bin/python3
import json
import os
import re
import threading
import time

import daemon.pidfile
import requests
from pandas import DataFrame

from stock.common.common_func import *
from stock.common.daemon_class import DaemonClass
from stock.common.time_util import load_last_date
from stock.common.variables import *

TODAY = load_last_date()


class RTTickGTJA(DaemonClass):
    """
    sub_topic: rtp_req
    res_topic: rtp_update
    Requests: add-stock, rm-stock, exit, clear
    Responds:{'stock':'002263','ask_5_size': 4616.0, 'ask_3_size': 1964.0, 'bid_2_price': 3.69, 'ask_4_size': 2599.86, 
    'volume': 106213.75, 'bid_1_size': 1311.0, 'code': '002263', 'bid_4_size': 2834.0, 'date': '2017-03-28', 
    'high': 3.72, 'bid_5_size': 2090.0, 'ask_5_price': 3.75, 'close': 3.7, 'bid_3_price': 3.68, 'ask_2_size': 6374.0, 
    'ask_3_price': 3.73, 'time': '15:20:03', 'total_ask_size': 18313.36, 'bid_5_price': 3.66, 'bid_4_price': 3.67, 
    'ask_1_size': 2759.5, 'bid_1_price': 3.7, 'ask_2_price': 3.72, 'money_volume': 3936.0, 'bid_2_size': 10598.0, 
    'ask_4_price': 3.74, 'low': 3.69, 'total_bid_size': 24691.0, 'ask_1_price': 3.71, 'open': 3.7, 'bid_3_size': 7858.0}
    """

    def __init__(self):
        super().__init__(topic_sub=['rtt_req'], topic_pub='rtt_update')
        self.s = requests.session()
        self.monitoring_list = []
        self.msg_on_exit = 'rtt_exit'
        self.pid_file_name = 'rtt.pid'

    def start(self):
        threading.Thread(target=self.monitor_main_loop).start()
        self.daemon_main()

    def mqtt_on_message(self, mqttc, obj, msg):

        payload = msg.payload.decode('utf8')
        print(msg.topic, msg.payload)
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

    def add_stock(self, stock):
        if stock not in self.monitoring_list:
            if stock in BASIC_INFO.symbol_list:
                self.monitoring_list.append(stock)

    def rm_stock(self, stock):
        if stock in self.monitoring_list:
            self.monitoring_list.remove(stock)

    def monitor_main_loop(self):
        print('starting main loop')
        while not self.cancel_daemon:
            try:
                # for stock in self.monitoring_list:
                # self.get_stock_rtp(stock)
                #    time.sleep(.5)  # FIXME temporary workaround
                self.get_stock_rtp_batch()
            except IndexError:
                self.unblock_publish('error_index')

    def get_stock_rtp(self, stock):
        tmp_str = '%s%s' % ('sh' if BASIC_INFO.market_dict[stock] == 'sse' else 'sz', stock)
        req_url = 'http://hq.sinajs.cn/list=' + tmp_str
        get_headers = {'User-Agent': COMMON_VARS_OBJ.AGENT_LIST['User-Agent']}
        result = self.s.get(req_url, headers=get_headers, verify=False)
        if result.status_code != 200:
            print('Exception %d' % result.status_code)
        tmp_result = result.text
        result = re.sub(r'[\n\"]', '', tmp_result)
        result_line = result.split(";")[0]
        parsed_line = parse_one_line(result_line)
        self.unblock_publish(json.dumps(parsed_line))
        # return parsed_line

    def get_stock_rtp_batch(self):
        stock_list = []
        tmp_str = ''
        monitoring_list = self.monitoring_list.copy()
        for stock in monitoring_list:
            tmp_str += '%s%s,' % ('sh' if BASIC_INFO.market_dict[stock] == 'sse' else 'sz', stock)
            stock_list.append(tmp_str)
            tmp_str = ''
        tmp_result = ''
        for line in stock_list:
            req_url = 'http://hq.sinajs.cn/list=' + line
            get_headers = {'User-Agent': COMMON_VARS_OBJ.AGENT_LIST['User-Agent']}
            result = self.s.get(req_url, headers=get_headers, verify=False)
            if result.status_code != 200:
                print('Exception %d' % result.status_code)
            tmp_result += result.text
        result = re.sub(r'[\n\"]', '', tmp_result)
        result_list = result.split(";")
        for line in result_list:
            parsed_line = parse_one_line(line)
            if parsed_line is not None:
                self.unblock_publish(json.dumps(parsed_line))


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/rtp.pid' %
                                                       COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path'])):

        a = RTPrice()
        a.start()
