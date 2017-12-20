import os
# COMPATIBLE( linux )
# TODO: add windows support

# noinspection PyDictCreation
DIRs = {}
DIRs['DATA_ROOT'] = os.path.expanduser("~/data/stockdata")
DIRs['SYMBOL_LIST_ROOT_CHINA'] = os.path.join(DIRs.get('DATA_ROOT'), "symbol_list/china")
DIRs['DAY_LEVEL_QUOTES_CHINA'] = os.path.join(DIRs.get('DATA_ROOT'), "day_quotes/china")
DIRs['TICK_QUOTES_CHINA'] = os.path.join(DIRs.get('DATA_ROOT'), "tick_quotes_quotes/china")
DIRs['LOG'] = os.path.join(DIRs.get('DATA_ROOT'), "log")