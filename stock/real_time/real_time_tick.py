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
    sub_topic: rtt_req
    res_topic: rtt_update
    Requests: add-stock, rm-stock, exit, clear
    """

    def __init__(self):
        super().__init__(topic_sub=['rtt_req'], topic_pub='rtt_update')
        self.last_time_dict = {}
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
                self.last_time_dict[stock] = '09:15:00'

    def rm_stock(self, stock):
        if stock in self.monitoring_list:
            self.monitoring_list.remove(stock)

    def monitor_main_loop(self):
        print('starting main loop')
        self.get_rt_tick()

    def get_rt_tick(self):
        today = load_last_date(date_type='current_day_cn')
        while not self.cancel_daemon:
            if len(self.monitoring_list) == 0:
                time.sleep(1)
            for stock in self.monitoring_list:
                try:
                    html = lxml.html.parse(
                        'http://vip.stock.finance.sina.com.cn/quotes_service/view/vMS_tradedetail.php?'
                        'symbol=%s'
                        '&date=%s'
                        '&page=1' % (BASIC_INFO.market_code_of_stock(stock), today))
                    res = html.xpath('//table[@id=\"datatbl\"]/tbody/tr')
                    str_array = [etree.tostring(node).decode('utf-8') for node in res]
                    str_array = ''.join(str_array)
                    str_array = '<table>%s</table>' % str_array
                    str_array = str_array.replace('--', '0')

                    df = pd.read_html(StringIO(str_array), parse_dates=False)[0]
                    df.columns = ['time', 'price', 'pchange', 'change', 'volume', 'amount', 'type']
                    df['pchange'] = df['pchange'].map(lambda x: x.replace('%', ''))
                    df = df[df['time'] > self.last_time_dict[stock]]
                    if len(df) > 0:
                        self.last_time_dict[stock] = max(df['time'])
                        df_list = list(df.T.to_dict().values())
                        for i in df_list:
                            i['stock'] = stock
                            self.unblock_publish(json.dumps(i))

                except Exception as e:
                    print(e)
                time.sleep(.5)
        time.sleep(.5)


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
        a.start()
