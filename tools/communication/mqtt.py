# -*- coding: utf-8 -*-
# Version 0.2.1
# Created 2017-07-28
# Author Zhao Zhang<zz156@georgetown.edu>

# Communication module, based on MQTT protocol, since different module instance may be deployed to different server.

# Every client keeps a keep-alive connection to MQTT Core, which may be a mosquitto-mqtt core.

# New class with MQTT comm. ability may extend this class. If the main purpose for the client is to subscribe topics
# and receive msgs, it should implement callback methods on_subscribe, on_message then subscribe topics.

# If the main purpose is only to send out some logs, go checkout tools.io.logging, which uses simple_publish method here
# simple_publish only needs minimal configuration params, doesn't create any instance.

# MQTT Proto defines connect, subscribe operations,
#   connect operation would be done within __init__() automatically.
#   subscribe should be called manually.
#   mqtt_sub_thread_cancel should be called to clean after yourself


# DEPENDENCY( paho-mqtt )
import threading

import paho.mqtt.client as mqtt
import paho.mqtt.publish as s_publish


def simple_publish(topic, payload, auth=None, host='localhost', port=1883):
    s_publish.single(topic, payload=payload, qos=0, retain=False, hostname=host,
                     port=port, client_id="", keepalive=60, will=None, auth=auth,
                     tls=None, protocol=mqtt.MQTTv31)


# noinspection PyUnusedLocal
class MQTTHdl:
    def __init__(self, mqtt_on_connect, mqtt_on_message, topic_sub=None, topic_pub='', client_title='Default',
                 hostname='localhost', port=1883):
        if topic_sub is None:
            topic_sub = []
        self.client = mqtt.Client()
        self.host = hostname
        self.port = port
        self.client.on_connect = mqtt_on_connect
        self.client.on_message = mqtt_on_message
        self.client.on_subscribe = self.mqtt_on_subscribe
        self.client.on_publish = self.mqtt_on_publish
        self.mqtt_topic_sub = topic_sub
        self.mqtt_topic_pub = topic_pub
        self.client_title = client_title
        self.msg_on_exit = ''
        self.client.connect(self.host, self.port, 60)

    # example of on_connect / on_message callback:
    # def mqtt_on_connect(self, mqttc, obj, flags, rc):
    #    if type(self.mqtt_topic_sub) == list:
    #        for t in self.mqtt_topic_sub:
    #            mqttc.subscribe(t)
    #    elif type(self.mqtt_topic_sub) == str:
    #        mqttc.subscribe(self.mqtt_topic_sub)

    # def mqtt_on_message(self, mqttc, obj, msg):
    #    # this function should be overloaded.
    #    payload = msg.payload.decode('utf8')
    #    print(payload)

    # noinspection PyBroadException
    def __del__(self):
        if self.client is not None:
            try:
                self.client.disconnect()
            except Exception as e:
                return

    def publish(self, msg, qos=0, topic=''):
        if topic == '':
            topic = self.mqtt_topic_pub
        (result, mid) = self.client.publish(topic, msg, qos)

    def mqtt_on_publish(self, mqttc, obj, mid):
        pass

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        pass

    # noinspection PyMethodMayBeStatic
    def mqtt_on_log(self, mqttc, obj, level, string):
        # this function should be overloaded.
        pass

    def mqtt_sub_thread_cancel(self):
        self.client.loop_stop(force=True)

    def mqtt_sub_thread_start(self):
        threading.Thread(target=self.client.loop_start).start()

    def mqtt_disconnect(self):
        self.client.disconnect()

    def mqtt_reconnect(self):
        self.client.connect(self.host, self.port, 60)
