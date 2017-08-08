import re

import os


def load_cfg(cfg_path):
    if os.path.isfile(cfg_path):
        with open(cfg_path) as f:
            raw_cfg = f.readlines()
    else:
        raw_cfg = ''
    cfg = []
    for line in raw_cfg:
        if len(line.lstrip().rstrip()) > 0:
            tmp_line = line.split('#')[0].lstrip().rstrip()
            split_line = re.split(r'[ \t]+', tmp_line)
            if (split_line[0] != '') & (split_line[0] != '#'):
                cfg.append(split_line)
    return cfg
