import paho.mqtt.client as mqtt
import paho.mqtt.publish as s_publish

def simple_publish(topic, payload):
    s_publish.single(topic, payload=payload, qos=0, retain=False, hostname="localhost",
                     port=1883, client_id="", keepalive=60, will=None, auth=None,
                     tls=None, protocol=mqtt.MQTTv31)