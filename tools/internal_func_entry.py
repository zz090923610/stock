from tools.fetch_symbol_list_china_a import SymbolListUpdater
from configs.path import DIRs
import configs.path as path
import os

# DELETE_FUTURE


def init_data_root():
    for p in DIRs.keys():
        if not os.path.isdir(DIRs.get(p)):
            os.makedirs(DIRs.get(p), exist_ok=True)


def update_symbol_list():
    a = SymbolListUpdater(path.DIRs.get("SYMBOL_LIST_ROOT_CHINA"))
    a.update()


if __name__ == '__main__':
    init_data_root()
    update_symbol_list()
