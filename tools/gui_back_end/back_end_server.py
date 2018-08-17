from tools.communication.mqtt import *


class BEServer(MQTTHdl):
    def __init__(self, mqtt_on_connect, mqtt_on_message, host, port):
        super().__init__(mqtt_on_connect, mqtt_on_message, topic_sub="anomaly_be_server_req", topic_pub='',
                         client_title='BEServer',
                         hostname=host, port=port)
        self.services = {}

    def __del__(self):
        pass

    def parse_req(self, req):
        pass
