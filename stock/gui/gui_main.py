import threading

import paho.mqtt.client as mqtt
from kivy import Config

from stock.real_time.trade_detail import HistoryTradeDetail

Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', '1920')  # FIXME monitor workaround
from kivy.app import App
from kivy.properties import OptionProperty, ObjectProperty, NumericProperty
from kivy.properties import StringProperty
from kivy.uix.actionbar import ActionBar
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.settings import SettingsWithSidebar
from kivy.core.text import LabelBase
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from stock.common.common_func import BASIC_INFO
from stock.common.communction import simple_publish
from stock.common.variables import COMMON_VARS_OBJ

from stock.trade_api.trade_api import TradeAPI

LabelBase.register(name="msyh",
                   fn_regular="./stock/gui/fonts/msyh.ttf")


# noinspection PyCompatibility
class StockBrokerLoginPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.trade_api = TradeAPI('gtja')
        self.captcha_md5 = ''

    def open(self, *largs):
        super().open(*largs)

    def update_captcha(self):
        self.ids['captcha_img'].source = ''
        simple_publish('trade_api_req', 'captcha_req')


class ImageButton(ButtonBehavior, AsyncImage):
    pass


class CustomDropDown(DropDown):
    pass


# noinspection PyCompatibility
class Sticker(ScatterLayout):
    title = StringProperty()
    sticker_id = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# noinspection PyCompatibility,PyShadowingBuiltins
class ProgressBarSticker(Sticker):
    progress_hint = StringProperty('')
    progress = NumericProperty(0)
    title = StringProperty('')

    def __init__(self, sid='', max=100, title='', **kwargs):
        super().__init__(**kwargs)
        self.ids['Progress_bar'].max = max
        self.title = title

        if sid != '':
            self.sticker_id = sid

    def update_progress(self):
        if self.progress < self.ids['Progress_bar'].max:
            self.progress += 1

    def update_info(self, info):
        self.progress_hint = info


# noinspection PyCompatibility
class BrokerLoginSticker(Sticker):
    def __init__(self, sid='', **kwargs):
        super().__init__(**kwargs)
        self.trade_api = TradeAPI('gtja')
        self.captcha_md5 = ''
        if sid != '':
            self.sticker_id = sid

    def update_captcha(self):
        self.ids['captcha_img'].source = ''
        simple_publish('trade_api_req', 'captcha_req')


class NotificationSticker(Sticker):
    msg = StringProperty('')
    title = StringProperty('')

    def __init__(self, sid='', title='', msg='', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.msg = msg
        if sid != '':
            self.sticker_id = sid

    def update_msg(self, msg):
        self.msg = msg


# noinspection PyMethodMayBeStatic,PyUnusedLocal,PyCompatibility
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
        self.mqtt_topic_sub = ['trade_api_update', 'ui_update', 'daily_data_update', 'tick_update', 'tick_detail',
                               'basic_info_update', 'news_hdl_update', 'trade_detail_update']
        self.current_state = 'Not connected'
        self.popup = StockBrokerLoginPopup()
        self.cancel_daemon = False
        self.msg_on_exit = ''
        self.MQTT_START()
        self.widget_cnt = 0
        self.widget_dict = {}
        self.trade_detail_hdl = HistoryTradeDetail()

    def show_popup(self):
        self.popup.open()

    def change_text(self, stri):
        self.current_state = stri

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        if type(self.mqtt_topic_sub) == list:
            for t in self.mqtt_topic_sub:
                mqttc.subscribe(t)
        elif type(self.mqtt_topic_sub) == str:
            mqttc.subscribe(self.mqtt_topic_sub)

    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')
        if msg.topic == 'daily_data_update':
            if payload.split('_')[0] == 'start':
                if 'daily_data_update_progress_bar_sticker' in self.widget_dict.keys():
                    self.remove_widget(self.widget_dict['daily_data_update_progress_bar_sticker'])
                    del self.widget_dict['daily_data_update_progress_bar_sticker']
                new_sticker = ProgressBarSticker(do_rotation=False, sid='daily_data_update_progress_bar_sticker',
                                                 max=len(BASIC_INFO.symbol_list), title='日线信息更新')
                self.add_widget(new_sticker)
                self.widget_dict['daily_data_update_progress_bar_sticker'] = new_sticker
                self.widget_cnt += 1
            else:
                try:
                    self.widget_dict['daily_data_update_progress_bar_sticker'].update_info(payload)
                    self.widget_dict['daily_data_update_progress_bar_sticker'].update_progress()
                except:
                    pass
        elif msg.topic == 'tick_update':
            if payload.rsplit('_', 1)[0] == 'analysis_finished':
                if 'tick_progress_bar_sticker' in self.widget_dict.keys():
                    self.remove_widget(self.widget_dict['tick_progress_bar_sticker'])
                    del self.widget_dict['tick_progress_bar_sticker']
                new_sticker = ProgressBarSticker(do_rotation=False, sid='tick_progress_bar_sticker',
                                                 max=int(payload.rsplit('_', 1)[1]), title='分笔信息更新')
                self.add_widget(new_sticker)
                self.widget_dict['tick_progress_bar_sticker'] = new_sticker
                self.widget_cnt += 1
            elif payload != 'analysis_start':
                try:
                    self.widget_dict['tick_progress_bar_sticker'].update_info(payload)
                except:
                    pass
        elif msg.topic == 'tick_detail':
            try:
                self.widget_dict['tick_progress_bar_sticker'].update_progress()
                self.widget_dict['tick_progress_bar_sticker'].update_info(payload)
            except:
                pass
        elif msg.topic == 'basic_info_update':
            if payload.find('alive') != -1:
                pass
            elif payload.find('start_updating_basic_info') != -1:
                if 'basic_info_update_progress_bar_sticker' in self.widget_dict.keys():
                    self.remove_widget(self.widget_dict['basic_info_update_progress_bar_sticker'])
                    del self.widget_dict['basic_info_update_progress_bar_sticker']
                new_sticker = ProgressBarSticker(do_rotation=False, sid='basic_info_update_progress_bar_sticker',
                                                 max=100, title='基本信息更新')
                self.add_widget(new_sticker)
                self.widget_dict['basic_info_update_progress_bar_sticker'] = new_sticker
                self.widget_cnt += 1
            else:
                try:
                    self.widget_dict['basic_info_update_progress_bar_sticker'].update_info(payload)
                    self.widget_dict['basic_info_update_progress_bar_sticker'].update_progress()
                except:
                    pass

        elif msg.topic == 'news_hdl_update':
            new_sticker = NotificationSticker(do_rotation=False, sid='news_notification_sticker_%d' % self.widget_cnt,
                                              title='时政新闻更新', msg=payload)
            self.add_widget(new_sticker)
            self.widget_dict['news_notification_sticker_%d' % self.widget_cnt] = new_sticker
            print(self.widget_dict)
            self.widget_cnt += 1
        elif msg.topic == 'trade_detail_update':
            new_sticker = NotificationSticker(do_rotation=False,
                                              sid='trade_detail_notification_sticker_%d' % self.widget_cnt,
                                              title='交割信息', msg=payload)
            self.add_widget(new_sticker)
            self.widget_dict['trade_detail_notification_sticker_%d' % self.widget_cnt] = new_sticker
            print(self.widget_dict)
            self.widget_cnt += 1

        if payload == 'exit':
            self.publish(self.msg_on_exit)
            self.cancel_daemon = True
        elif payload.find('md5_fetched') != -1:
            md5 = payload.split('_')[2]
            print('md5', md5)
            for w in self.widget_dict.values():
                try:
                    w.ids['captcha_img'].source = '%s/trade_api/Captcha_%s/%s.jpg' % (
                        COMMON_VARS_OBJ.stock_data_root, self.trade_api.broker, md5)
                except KeyError:
                    pass
        elif payload.find('add_sticker_login') != -1:
            new_sticker = BrokerLoginSticker(do_rotation=False, sid='broker_login_sticker')
            self.trade_api.pre_login()
            self.add_widget(new_sticker)
            if 'broker_login_sticker' in self.widget_dict:
                self.remove_widget(self.widget_dict['broker_login_sticker'])
                del self.widget_dict['broker_login_sticker']
                self.widget_cnt -= 1
            self.widget_dict['broker_login_sticker'] = new_sticker
            print(self.widget_dict)
            self.widget_cnt += 1
        elif payload.find('try_login') != -1:
            self.trade_api.user = self.widget_dict['broker_login_sticker'].ids['Account'].text
            self.trade_api.passwd = self.widget_dict['broker_login_sticker'].ids['Passwd'].text
            self.trade_api.v_code = self.widget_dict['broker_login_sticker'].ids['Captcha'].text
            print(self.trade_api.user, self.trade_api.passwd, self.trade_api.v_code)
            self.trade_api.login()
        elif payload.find('login_success') != -1:
            if 'broker_login_sticker' in self.widget_dict:
                self.remove_widget(self.widget_dict['broker_login_sticker'])
                del self.widget_dict['broker_login_sticker']
                self.widget_cnt -= 1

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

    def add_login_sticker(self):
        simple_publish('ui_update', 'add_sticker_login')

    def try_login(self):
        simple_publish('ui_update', 'try_login')

    def update_daily_all(self):
        simple_publish('data_req', 'daily_update_all')

    def update_daily(self):
        simple_publish('data_req', 'daily_update')

    def update_tick(self):
        simple_publish('data_req', 'tick_update')

    def remove_login_sticker(self, sticker_id):
        self.remove_widget(self.widget_dict[sticker_id])
        del self.widget_dict[sticker_id]


class ControllerApp(App):
    display_type = OptionProperty('normal', options=['normal', 'popup'])
    settings_popup = ObjectProperty(None, allownone=True)
    main_layout = None

    def build(self):

        self.display_type = 'normal'
        self.main_layout = Controller()
        layout_bar = ActionBar()
        self.main_layout.add_widget(layout_bar)
        self.set_settings_cls(SettingsWithSidebar)

        return self.main_layout

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


if __name__ == '__main__':
    Window.maximize()
    a = ControllerApp()

    a.run()
