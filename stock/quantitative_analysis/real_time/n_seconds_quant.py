import datetime
import json
import time

import daemon.pidfile
import daemon.pidfile

from stock.common.common_func import *
from stock.common.communction import simple_publish
from stock.common.daemon_class import DaemonClass
from stock.common.time_util import load_last_date
from stock.common.variables import COMMON_VARS_OBJ


class NSecondsQuant:
    def __init__(self, stock, seconds):
        self.stock = stock
        self.sum = 0
        self.current_timestamp = 0
        self.current_time = ''
        self.out_date_timestamp = 0
        self.n = seconds
        self.data_queue = []
        self.today = load_last_date('current_day_cn')
        self.save_list = []

    def add_data(self, data_dict):
        """
        :param data_dict:
         {
            "stock": "000725", 
            "tick": [
                        {"time": "09:34:29.820", "price": 3.57, "hands": 30.0, "sort_id": "777574", "type": "B"}
                    ]
        }
        :return: 
        """
        for tick in data_dict['tick']:
            self.current_timestamp = self.cvt2timestamp(tick['time'])
            self.current_time = tick['time']
            self.data_queue.append([self.current_timestamp, tick['hands'], tick['type'], self.current_time])
            self.out_date_timestamp = self.current_timestamp - self.n
            self.sum += tick['hands']

        for (idx, line) in enumerate(self.data_queue):
            if line[0] > self.out_date_timestamp:
                self.data_queue = self.data_queue[idx:]
                break
            else:
                self.sum -= line[1]

        self.save_list.append({'stock': self.stock, 'quant_n_seconds': self.sum, 'time': self.current_time})
        simple_publish('n_seconds_quant_update',
                       json.dumps({'stock': self.stock, 'quant_n_seconds': self.sum, 'time': self.current_time}))
        print(self.stock, self.sum, self.current_time)
        self.dump_data()

    def cvt2timestamp(self, time_str):
        return time.mktime(
            datetime.datetime.strptime('%s %s' % (self.today, time_str), "%Y-%m-%d %H:%M:%S.%f").timetuple())

    def dump_data(self):
        pd.DataFrame(self.save_list) \
            .to_csv(
            '%s/quantitative_analysis/real_time/n_seconds_quant/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, self.stock))


class NSecondsQuantDaemon(DaemonClass):
    if not os.path.isdir('%s/quantitative_analysis/real_time/n_seconds_quant' % COMMON_VARS_OBJ.stock_data_root):
        os.makedirs('%s/quantitative_analysis/real_time/n_seconds_quant' % COMMON_VARS_OBJ.stock_data_root)

    def __init__(self, n=30):
        super().__init__(topic_sub=['n_seconds_quant_req', 'real_tick_update'], topic_pub='n_seconds_quant_update')
        self.msg_on_exit = 'n_seconds_quant_exit'
        self.pid_file_name = 'n_seconds_quant.pid'
        self.monitoring_dict = {}
        self.n = n

    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')
        if msg.topic == 'n_seconds_quant_req':
            if payload == 'is_alive':
                self.publish('alive_%d' % os.getpid())
            elif payload == 'exit':
                self.publish(self.msg_on_exit)
                self.cancel_daemon = True
        elif msg.topic == 'real_tick_update':
            print(payload)
            data = json.loads(payload)
            if data['stock'] not in self.monitoring_dict.keys():
                self.monitoring_dict[data['stock']] = NSecondsQuant(data['stock'], self.n)
            self.monitoring_dict[data['stock']].add_data(data)


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/n_seconds_quant.pid' %
                                                       COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path'])):
        a = NSecondsQuantDaemon()
        a.daemon_main()
