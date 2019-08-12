# -*- coding: utf-8 -*-
import os
import json

user_defined_data_root = "/home/zhangzhao/stock_data"
PROGRAM_DATA_ROOT = None
MODEL_BASE_DIR = os.path.join(os.getcwd(), 'models')
try:
    with open(os.path.join(user_defined_data_root, "config.json")) as f:
        CONFIGS = json.load(f)
        TUSHARE_PRO_TOKEN = CONFIGS["tushare_pro_token"]
except Exception as e:  # default values
    raise
if user_defined_data_root is not None:
    PROGRAM_DATA_ROOT = user_defined_data_root
else:  # default data root dir( $user/Documents/stock_data for win and ~/data/stock_data for linux )
    import platform
    from pathlib import Path

    HOST_OS = platform.system()
    PROGRAM_DATA_ROOT = os.path.join(Path.home(), "Documents", 'stock_data') if HOST_OS == "Windows" else \
        os.path.join(Path.home(), 'data', 'stock_data')

