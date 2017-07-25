import threading

import paho.mqtt.client as mqtt
import paho.mqtt.publish as s_publish

from stock.common.file_operation import logging
from stock.common.variables import *

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 1883


def simple_publish(topic, payload):
    s_publish.single(topic, payload=payload, qos=0, retain=False, hostname=DEFAULT_HOST,
                     port=DEFAULT_PORT, client_id="", keepalive=60, will=None, auth=None,
                     tls=None, protocol=mqtt.MQTTv31)


class MQTTHDl:
    def __init__(self, topic_sub=None, topic_pub='', client_title='Default', hostname='localhost', port=1883):
        if topic_sub is None:
            topic_sub = []
        self.client = mqtt.Client()
        self.host = hostname
        self.port = port
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.on_subscribe = self.mqtt_on_subscribe
        self.client.on_publish = self.mqtt_on_publish
        self.mqtt_topic_sub = topic_sub
        self.mqtt_topic_pub = topic_pub
        self.client_title = client_title
        self.cancel_daemon = False
        self.msg_on_exit = ''
        self.client.connect(self.host, self.port, 60)

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        if type(self.mqtt_topic_sub) == list:
            for t in self.mqtt_topic_sub:
                mqttc.subscribe(t)
        elif type(self.mqtt_topic_sub) == str:
            mqttc.subscribe(self.mqtt_topic_sub)

    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')
        print(payload)
        if payload == 'exit':
            self.publish(self.msg_on_exit)
            self.cancel_daemon = True

    def publish(self, msg, qos=0, topic=''):
        if topic == '':
            topic = self.mqtt_topic_pub
        (result, mid) = self.client.publish(topic, msg, qos)

    def unblock_publish(self, msg, qos=0):
        s_publish.single(self.mqtt_topic_pub, payload=msg,
                         qos=qos, retain=False, hostname=self.host,
                         port=self.port, client_id="", keepalive=60, will=None, auth=None,
                         tls=None, protocol=mqtt.MQTTv31)

    def mqtt_on_publish(self, mqttc, obj, mid):
        pass

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        pass

    # noinspection PyMethodMayBeStatic
    def mqtt_on_log(self, mqttc, obj, level, string):
        if IS_DEBUG:
            logging(string, silence=True)

    def mqtt_sub_thread_cancel(self):
        self.client.loop_stop(force=True)
        if IS_DEBUG:
            logging('%s MQTT Daemon Canceled' % self.client_title, silence=True)

    def mqtt_sub_thread_start(self):
        threading.Thread(target=self.client.loop_start).start()
        if IS_DEBUG:
            logging('%s MQTT Daemon Started' % self.client_title, silence=True)

    def mqtt_disconnect(self):
        self.client.disconnect()

    def mqtt_reconnect(self):
        self.client.connect(self.host, self.port, 60)
