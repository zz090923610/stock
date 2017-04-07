import json
import time
import numpy as np
import _thread
import daemon.pidfile
import matplotlib.pyplot as plt

from stock.common.common_func import *
from stock.common.daemon_class import DaemonClass
from stock.common.variables import COMMON_VARS_OBJ


class NSQPlot:
    def __init__(self, stock):
        self.stock = stock
        self.stop = False
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        # some X and Y data
        self.x = [i for i in range(120)]
        self.y = [0 for _ in range(120)]

        self.li, = self.ax.plot(self.x, self.y)

        # draw and show it
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        self.fig.canvas.draw()
        plt.show(block=False)
        self.plot()

    def update_data(self, data):
        self.y[:-1] = self.y[1:]
        self.y[-1:] = data['quant_n_seconds']
        print(self.y)
        self.li.set_ydata(self.y)

    def stop(self):
        self.stop = True

    def plot(self):
        # loop to update the data
        while not self.stop:
            try:
                self.fig.canvas.draw()

                time.sleep(0.1)
            except KeyboardInterrupt:
                break


class NSQPlotDaemon(DaemonClass):
    def __init__(self):
        super().__init__(topic_sub=['nsq_plot_req', 'n_seconds_quant_update'], topic_pub='nsq_plot_update')
        self.msg_on_exit = 'nsq_plot_exit'
        self.pid_file_name = 'nsq_plot.pid'
        self.monitoring_dict = {}

    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')
        if msg.topic == 'nsq_plot_req':
            if payload == 'is_alive':
                self.publish('alive_%d' % os.getpid())
            elif payload == 'exit':
                self.publish(self.msg_on_exit)
                for k in self.monitoring_dict.keys():
                    self.monitoring_dict[k].stop()
                self.cancel_daemon = True
        elif msg.topic == 'n_seconds_quant_update':
            print(payload)
            data = json.loads(payload)
            if data['stock'] not in self.monitoring_dict.keys():
                self.monitoring_dict[data['stock']] = NSQPlot(data['stock'])
            self.monitoring_dict[data['stock']].update_data(data)


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/n_seconds_quant.pid' %
                                                       COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path'])):
        a = NSQPlotDaemon()
        a.daemon_main()
