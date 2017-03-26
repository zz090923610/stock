#!/usr/bin/env python3
import json
import threading
import time
from threading import Thread

import daemon.pidfile
import paho.mqtt.client as mqtt

from stock.common.common_func import *
from stock.common.time_util import load_last_date
from stock.quantitative_analysis.daily_financial_report import financial_report_main

TODAY = load_last_date()


# noinspection PyMethodMayBeStatic
class QADaemon:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.on_subscribe = self.mqtt_on_subscribe
        self.client.on_publish = self.mqtt_on_publish
        self.client.connect("localhost", 1883, 60)
        self.mqtt_topic_sub = ["time_util_update", "qa_req"]
        self.mqtt_topic_pub = "qa_update"
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
        elif msg.topic == "qa_req":
            payload = msg.payload.decode('utf8')
            if payload == 'is_alive':
                self.publish('alive_%d' % os.getpid())
            elif payload == 'update':
                t = Thread(target=financial_report_main)
                t.start()
            elif payload == 'exit':
                self.publish('qa_hdl exit')
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
            pidfile=daemon.pidfile.PIDLockFile('%s/qa_hdl.pid' % COMMON_VARS_OBJ.DAEMON['news_hdl']['pid_path'])):
        a = QADaemon()
        a.daemon_main()


if __name__ == "__main__":
    main()
