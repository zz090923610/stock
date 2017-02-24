import csv
import pickle
import subprocess
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from matplotlib import ticker
from mpl_finance import *
from common_func import BASIC_INFO, logging
from qa_linear_fit import get_fitted_data
from variables import *
from intraday_plot import intraday_plot
def k_plot(stock, days):
	df=get_fitted_data(stock, days, 15, 2)
	df_atpdr=load_atpdr_for_plot(stock, days)
	df_ma3=load_ma_for_stock_for_plot(stock, 'atpd_3', days)
	df_ma10=load_ma_for_stock_for_plot(stock, 'atpd_10', days)
	df_ma20=load_ma_for_stock_for_plot(stock, 'atpd_20', days)
	df_ma40=load_ma_for_stock_for_plot(stock, 'atpd_40', days)
	df_tmi_accu=calc_tmi_series_for_stock(stock, days)
	
	s_full_name = BASIC_INFO.get_market_code_of_stock(stock)
	fig = plt.figure(figsize=(16, 9), dpi=100)
	fonts = [14, 16]
	N = len(df.date)
	ind = np.arange(N)
	date_list = df['date'].tolist()
	def format_date(x, pos=None):
		thisind = np.clip(int(x + 0.5), 0, N - 1)
		return date_list[thisind]
		
	matplotlib.rcParams.update({'font.size': fonts[0]})
	ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=3)
	ax2 = plt.subplot2grid((6, 1), (3, 0), rowspan=1)
	ax3 = plt.subplot2grid((6, 1), (4, 0), rowspan=1)
	ax4 = plt.subplot2grid((6, 1), (5, 0), rowspan=1)
	fig.suptitle('%s %s 日线图 %s 开:%.02f 收:%.02f 高:%.02f 低:%.02f' % (stock, BASIC_INFO.name_dict[stock],df.iloc[-1]['date'],df.iloc[-1]['open'], df.iloc[-1]['close'],df.iloc[-1]['high'], df.iloc[-1]['low']))
	ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
	legend_list0 = []
	legend_list1 = []
	legend_list2 = []
	p_upper_trend, = ax1.plot(ind, df.upper_trend, 'k-')
	plt.setp(p_upper_trend, linewidth=.5)
	p_bottom_trend, = ax1.plot(ind, df.bottom_trend, 'k-')
	plt.setp(p_bottom_trend, linewidth=.5)
	p_cost_per_vol_1, = ax1.plot(ind, df_atpdr.cost_per_vol_1, 'k-')
	plt.setp(p_cost_per_vol_1, linewidth=.5)
	legend_list0.append(p_cost_per_vol_1)
	p_cost_per_vol_3, = ax1.plot(ind, df_atpdr.cost_per_vol_3, 'k-')
	plt.setp(p_cost_per_vol_3, linewidth=.5)
	legend_list0.append(p_cost_per_vol_3)
	p_vol_per_tick_1, = ax3.plot(ind, df_atpdr.vol_per_tick_1, 'k-')
	plt.setp(p_vol_per_tick_1, linewidth=.5)
	legend_list1.append(p_vol_per_tick_1)
	p_vol_per_tick_3, = ax3.plot(ind, df_atpdr.vol_per_tick_3, 'k-')
	plt.setp(p_vol_per_tick_3, linewidth=.5)
	legend_list1.append(p_vol_per_tick_3)
	p_ma20, = ax1.plot(ind, df_ma20.ma20, 'k-')
	plt.setp(p_ma20, linewidth=.5)
	legend_list0.append(p_ma20)
	p_ma40, = ax1.plot(ind, df_ma40.ma40, 'k-')
	plt.setp(p_ma40, linewidth=.5)
	legend_list0.append(p_ma40)
	p_tmi_accu, = ax4.plot(ind, df_tmi_accu.tmi_accu, 'k-')
	plt.setp(p_tmi_accu, linewidth=.5)
	legend_list2.append(p_tmi_accu)
	p_tmi_large_accu, = ax4.plot(ind, df_tmi_accu.tmi_large_accu, 'k-')
	plt.setp(p_tmi_large_accu, linewidth=.5)
	legend_list2.append(p_tmi_large_accu)
	
