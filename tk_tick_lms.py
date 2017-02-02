#!/usr/bin/env python3

import matplotlib

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import numpy as np
from common_func import *
from qa_tick_lms import load_lms, load_daily_data

import sys

if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

root = Tk.Tk()
root.wm_title(u"对数成交量模型")


def plot_tick_lms_tk(a_fig, stock, type):
    basic_info = BASIC_INFO_DICT[stock]
    lms_list = load_lms(stock)
    closes = []
    opens = []
    highs = []
    lows = []
    volume = []
    buy_large = []
    sell_large = []
    buy_mid = []
    sell_mid = []
    buy_small = []
    sell_small = []
    undirected_trade = []
    date_list = []
    daily_data = load_daily_data(stock)
    for (idx, row) in enumerate(daily_data):
        opens.append(row['open'])
        closes.append(row['close'])
        highs.append(row['high'])
        lows.append(row['low'])
        volume.append(row['volume'])
        buy_large.append(lms_list[idx]['buy_large'])
        sell_large.append(lms_list[idx]['sell_large'])
        buy_mid.append(lms_list[idx]['buy_mid'])
        sell_mid.append(lms_list[idx]['sell_mid'])
        buy_small.append(lms_list[idx]['buy_small'])
        sell_small.append(lms_list[idx]['sell_small'])
        undirected_trade.append(lms_list[idx]['undirected_trade'])
        date_list.append(row['date'])
    fig = a_fig
    ax1 = fig.add_subplot(111)
    matplotlib.rcParams.update({'font.size': 14})
    N = len(date_list)
    ind = np.arange(N)

    def format_date(x, pos=None):
        thisind = np.clip(int(x + 0.5), 0, N - 1)
        return date_list[thisind]

    legend_list = []
    assert (len(ind) == len(closes))
    if type.find('overall') != -1:
        oa, = ax1.plot(ind, log_quantity, '-', label=u'综合')
        plt.setp(oa, linewidth=2)
        legend_list.append(oa)
    if type.find('buy_large') != -1:
        bl, = ax1.plot(ind, log_buy_large, '-', label=u'大买')
        plt.setp(bl, linewidth=2)
        legend_list.append(bl)
    if type.find('sell_large') != -1:
        sl, = ax1.plot(ind, log_sell_large, '-', label=u'大卖')
        plt.setp(sl, linewidth=2)
        legend_list.append(sl)
    if type.find('buy_small') != -1:
        bs, = ax1.plot(ind, log_buy_small, '-', label=u'小买')
        plt.setp(bs, linewidth=2)
        legend_list.append(bs)
    if type.find('sell_small') != -1:
        ss, = ax1.plot(ind, log_sell_small, '-', label=u'小卖')
        plt.setp(ss, linewidth=2)
        legend_list.append(ss)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    if len(legend_list) != 0:
        leg = ax1.legend(handles=legend_list, )
        leg.get_frame().set_alpha(0.5)
    ax1.set_xlabel('%s %s' % (stock, basic_info['name']))
    ax1.xaxis.set_label_position('top')
    if type.find('kline') != -1:
        ax2 = ax1.twinx()
        plfin.candlestick2_ochl(ax2, opens, closes, highs, lows, width=0.75, colorup='r', colordown='g', alpha=1)

    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    fig.autofmt_xdate()
    fig.tight_layout()
    # return date_list, opens, closes, highs, lows


if __name__ == '__main__':
    fig = plt.figure(figsize=(12, 6), dpi=100)
    plt.close(fig)
    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(fig, master=root)

    canvas.show()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)


    def on_key_event(event):
        print('you pressed %s' % event.key)
        key_press_handler(event, canvas, toolbar)


    canvas.mpl_connect('key_press_event', on_key_event)


    def _quit():
        root.quit()  # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def on_draw():
        stock_code = entry_stock.get()
        ax_list = fig.axes
        for ax in ax_list:
            fig.delaxes(ax)
        fig.clf()
        type = ''
        if chk_var_overall.get() == 1:
            type += 'overall'
        if chk_var_bl.get() == 1:
            type += 'buy_large'
        if chk_var_bs.get() == 1:
            type += 'buy_small'
        if chk_var_sl.get() == 1:
            type += 'sell_large'
        if chk_var_ss.get() == 1:
            type += 'sell_small'
        if chk_var_kline.get() == 1:
            type += 'kline'
        try:
            plot_tick_lms_tk(fig, stock_code, .5, type)
        except:
            calculate_detailed_trade_quantity_for_stock(stock_code)
            plot_tick_lms_tk(fig, stock_code, .5, type)
        fig.canvas.draw()


    frame = Tk.Frame(master=root, relief=Tk.RAISED, borderwidth=1)
    frame.pack(fill=Tk.X,side=Tk.BOTTOM, expand=True)
    labelText = Tk.StringVar()
    labelText.set(u"股票代码")
    labelDir = Tk.Label(master=frame, textvariable=labelText, height=4)
    labelDir.pack(side=Tk.LEFT)
    entry_stock = Tk.Entry(master=frame, width=10)
    entry_stock.pack(side=Tk.LEFT)
    chk_var_overall = Tk.IntVar()
    chk_overall = Tk.Checkbutton(master=frame, text=u'综合', variable=chk_var_overall)
    chk_overall.pack(side=Tk.LEFT)
    chk_var_bl = Tk.IntVar()
    chk_bl = Tk.Checkbutton(master=frame, text=u'大买', variable=chk_var_bl)
    chk_bl.pack(side=Tk.LEFT)

    chk_var_sl = Tk.IntVar()
    chk_sl = Tk.Checkbutton(master=frame, text=u'大卖', variable=chk_var_sl)
    chk_sl.pack(side=Tk.LEFT)

    chk_var_bs = Tk.IntVar()
    chk_bs = Tk.Checkbutton(master=frame, text=u'小买', variable=chk_var_bs)
    chk_bs.pack(side=Tk.LEFT)

    chk_var_ss = Tk.IntVar()
    chk_ss = Tk.Checkbutton(master=frame, text=u'小卖', variable=chk_var_ss)
    chk_ss.pack(side=Tk.LEFT)
    chk_var_kline = Tk.IntVar()
    chk_kline = Tk.Checkbutton(master=frame, text=u'k线', variable=chk_var_kline)
    chk_kline.pack(side=Tk.LEFT)

    button_draw = Tk.Button(master=frame, text=u'画图', command=on_draw)
    button_draw.pack(side=Tk.LEFT)
    button = Tk.Button(master=frame, text=u'退出', command=_quit)
    button.pack(side=Tk.RIGHT)

    Tk.mainloop()
    # If you put root.destroy() here, it will cause an error if
    # the window is closed with the window manager.
