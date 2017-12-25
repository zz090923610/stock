import threading

import paho.mqtt.client as mqtt
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import OptionProperty, ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.actionbar import ActionBar
from kivy.uix.floatlayout import FloatLayout

LabelBase.register(name="msyh",
                   fn_regular="./gui/fonts/msyh.ttf")


# noinspection PyMethodMayBeStatic,PyUnusedLocal,PyCompatibility,PyBroadException
class Controller(FloatLayout):
    current_state = StringProperty()
    display_type = OptionProperty('normal', options=['normal', 'popup'])
    settings_popup = ObjectProperty(None, allownone=True)

    def load_modules(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label_wid = ObjectProperty()
        self.info = StringProperty()
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.connect("localhost", 1883, 60)
        self.mqtt_topic_sub = []
        self.current_state = 'Not connected'
        self.cancel_daemon = False
        self.msg_on_exit = ''
        self.mqtt_start()
        self.module_dict = {}
        self.load_modules()

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        if type(self.mqtt_topic_sub) == list:
            for t in self.mqtt_topic_sub:
                mqttc.subscribe(t)
        elif type(self.mqtt_topic_sub) == str:
            mqttc.subscribe(self.mqtt_topic_sub)

    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')

    def mqtt_on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def mqtt_on_log(self, mqttc, obj, level, string):
        print(string)

    def mqtt_cancel(self):
        self.client.loop_stop(force=True)
        self.change_text('Not connected')

    def mqtt_start(self):
        threading.Thread(target=self.client.loop_start).start()


# noinspection PyUnusedLocal
class ControllerApp(App):
    main_layout = None

    def build(self):
        Builder.load_file('/home/zhangzhao/data/stock/gui/kv/actionbar.kv')
        self.main_layout = Controller()
        layout_bar = ActionBar()
        self.main_layout.add_widget(layout_bar)

        return self.main_layout


if __name__ == '__main__':
    a = ControllerApp()

    a.run()
