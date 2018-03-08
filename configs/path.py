import os
# DELETE_FUTURE
# COMPATIBLE( linux )

# noinspection PyDictCreation
DIRs = {}
DIRs['DATA_ROOT'] = os.path.expanduser("~/data/stock_data")
DIRs['SYMBOL_LIST_ROOT_CHINA'] = os.path.join(DIRs.get('DATA_ROOT'), "symbol_list/china")
DIRs['DAY_LEVEL_QUOTES_CHINA'] = os.path.join(DIRs.get('DATA_ROOT'), "day_quotes/china")
DIRs['TICK_QUOTES_CHINA'] = os.path.join(DIRs.get('DATA_ROOT'), "tick_quotes/china")
DIRs['LOG'] = os.path.join(DIRs.get('DATA_ROOT'), "log")
DIRs['QA'] = os.path.join(DIRs.get('DATA_ROOT'), "qa")
DIRs["TRANSLATE"] = os.path.join(DIRs.get('DATA_ROOT'), "translate")
DIRs['MODEL'] = os.path.join(DIRs.get('DATA_ROOT'), "model")
DIRs['CALENDAR'] = os.path.join(DIRs.get('DATA_ROOT'), "calendar")
DIRs['SLICE'] = os.path.join(DIRs.get('DATA_ROOT'), "slice")

