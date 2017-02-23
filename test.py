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
