import threading

import paho.mqtt.client as mqtt
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import OptionProperty, ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.actionbar import ActionBar
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.base import runTouchApp
from kivy.uix.settings import SettingsWithSidebar
from kivy.core.text import LabelBase

from stock.common.variables import stock_data_root

LabelBase.register(name="msyh",
                   fn_regular="./fonts/msyh.ttf")


class StockBrokerLoginPopup(Popup):
    def __init__(self, trade_api, **kwargs):
        super.__init__(**kwargs)
        md5 = trade_api.get_captcha()
        self.ids['captcha_img'].source = '%s/trade_api/Captcha_%s/%s.jpg' % (stock_data_root, trade_api.broker, md5)


class CustomDropDown(DropDown):
    pass


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Controller(FloatLayout):
    current_state = StringProperty()
    display_type = OptionProperty('normal', options=['normal', 'popup'])

    settings_popup = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label_wid = ObjectProperty()
        self.info = StringProperty()
        self.client = mqtt.Client()
        self.trade_api = TradeAPI('gtja')
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.connect("localhost", 1883, 60)
        self.mqtt_topic = "mqtt"
        self.current_state = 'Not connected'
        self.popup = StockBrokerLoginPopup()

    def show_popup(self):
        self.popup.open()

    def change_text(self, stri):
        self.current_state = stri

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        print("rc: " + str(rc))
        self.change_text('connected')
        mqttc.subscribe(self.mqtt_topic)

    def mqtt_on_message(self, mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self.change_text(str(msg.payload))

    def mqtt_on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def mqtt_on_log(self, mqttc, obj, level, string):
        print(string)

    def MQTT_CANCEL(self):
        self.client.loop_stop(force=True)
        self.change_text('Not connected')

    def MQTT_START(self):
        threading.Thread(target=self.client.loop_start).start()


class ControllerApp(App):
    display_type = OptionProperty('normal', options=['normal', 'popup'])
    settings_popup = ObjectProperty(None, allownone=True)

    def build(self):
        self.display_type = 'popup'
        layout = Controller()
        layout_bar = ActionBar()
        layout.add_widget(layout_bar)
        self.set_settings_cls(SettingsWithSidebar)
        return layout

    def on_settings_cls(self, *args):
        self.destroy_settings()

    def set_settings_cls(self, panel_type):
        self.settings_cls = panel_type

    def set_display_type(self, display_type):
        self.destroy_settings()
        self.display_type = display_type

    def display_settings(self, settings):
        if self.display_type == 'popup':
            p = self.settings_popup
            if p is None:
                self.settings_popup = p = Popup(content=settings,
                                                title='Settings',
                                                size_hint=(0.8, 0.8))
            if p.content is not settings:
                p.content = settings
            p.open()
        else:
            super(ControllerApp, self).display_settings(settings)

    def close_settings(self, *args):
        if self.display_type == 'popup':
            p = self.settings_popup
            if p is not None:
                p.dismiss()
        else:
            super(ControllerApp, self).close_settings()



            # class CustomBtn(Widget):
            #    pressed = ListProperty([0, 0])

            #    def on_touch_down(self, touch):
            #        if isinstance(touch.shape, ShapeRect):
            #            print('Touch has shape', (touch.shape.width, touch.shape.height))
            #        touch.push()
            #        touch.apply_transform_2d(self.to_local)
            #        ret = super(CustomBtn, self).on_touch_down(touch)

            #        touch.pop()
            #        return ret

            #    def on_pressed(self, instance, pos):
            #        print('pressed at{pos}'.format(pos=pos))

            #    def on_touch_move(self, touch):
            #        if isinstance(touch.shape, ShapeRect):
            #            print('Touch has shape', (touch.shape.width, touch.shape.height))
            #        print('touching pos', touch.pos)
            #       if 'angle' in touch.profile:
            #           print('touch angle is', touch.a)


            # class RootWidget(BoxLayout):
            #    def __init__(self, **kwargs):
            #        super(RootWidget, self).__init__(**kwargs)
            #        self.add_widget(Button(text='Button 1'))
            #        cb = CustomBtn()
            #        cb.bind(pressed=self.btn_pressed)
            #        self.add_widget(cb)
            #        self.add_widget(Button(text='Button 2'))
            # for c in self.children[:]:
            #  print(c)


# def btn_pressed(self, instance, pos):
#        print('POS: printed from widget:{pos}'.format(pos=pos))


# class TestApp(App):
#    def build(self):
#        return RootWidget()


if __name__ == '__main__':
    a = ControllerApp()
    a.run()
