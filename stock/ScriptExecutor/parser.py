import pandas as pd
import os
import math
import re


def load_data(input_data):
    if type(input_data) == pd.core.frame.DataFrame:
        data = input_data
    elif type(input_data) == str:
        if os.path.isfile(input_data):
            data = pd.read_csv(input_data)
        else:
            data = None
    else:
        data = None
    return data


def load_script(script_path):
    if os.path.isfile(script_path):
        with open(script_path) as f:
            raw_script = f.readlines()
    else:
        raw_script = ''
    script = []
    for line in raw_script:
        if len(line.lstrip().rstrip()) > 0:
            tmp_line = line.split('#')[0].lstrip().rstrip()
            split_line = re.split(r'[ \t]+', tmp_line)
            if (split_line[0] != '') & (split_line[0] != '#'):
                script.append(split_line)
    for line in script:
        print(line)
    return script

def is_num(target):
    try:
        float(target)
        return True
    except ValueError:
        return False

def parse_script(input_data, script_path, output_method):
    data = load_data(input_data)
    data_cols = data.columns.tolist()
    vars = {}
    imms = {}
    shift_series = {}
    script = load_script(script_path)
    for line in script:
        if line[0] == 'ADDC':
            result_col = line[1]
            data[result_col] = data[line[2]]
            for op_source in line[3:]:
                if op_source in data_cols:
                    data[result_col] += data[op_source]
                elif op_source in shift_series:
                    for s in shift_series[op_source]:
                        data[result_col] += data[s]
                elif op_source in vars.keys():
                    data[result_col] += vars[op_source]
                elif op_source in imms.keys():
                    data[result_col] += imms[op_source]
                elif is_num(op_source):
                    data[result_col] += float(op_source)
        elif line[0] == 'SUBC':
            result_col = line[1]
            data[result_col] = data[line[2]]
            for op_source in line[3:]:
                if op_source in data_cols:
                    data[result_col] -= data[op_source]
                elif op_source in vars.keys():
                    data[result_col] -= vars[op_source]
                elif op_source in imms.keys():
                    data[result_col] -= imms[op_source]
                elif is_num(op_source):
                    data[result_col] -= float(op_source)
        elif line[0] == 'MULC':
            result_col = line[1]
            data[result_col] = data[line[2]]
            for op_source in line[3:]:
                if op_source in data_cols:
                    data[result_col] *= data[op_source]
                elif op_source in vars.keys():
                    data[result_col] *= vars[op_source]
                elif op_source in imms.keys():
                    data[result_col] *= imms[op_source]
                elif is_num(op_source):
                    data[result_col] *= float(op_source)
        elif line[0] == 'DIVC':
            result_col = line[1]
            data[result_col] = data[line[2]]
            for op_source in line[3:]:
                if op_source in data_cols:
                    data[result_col] /= data[op_source]
                elif op_source in vars.keys():
                    data[result_col] /= vars[op_source]
                elif op_source in imms.keys():
                    data[result_col] /= imms[op_source]
                elif is_num(op_source):
                    data[result_col] /= float(op_source)
        elif line[0] == 'MODC':
            result_col = line[1]
            data[result_col] = data[line[2]]
            for op_source in line[3:]:
                if op_source in data_cols:
                    data[result_col] %= data[op_source]
                elif op_source in vars.keys():
                    data[result_col] %= vars[op_source]
                elif op_source in imms.keys():
                    data[result_col] %= imms[op_source]
                elif is_num(op_source):
                    data[result_col] %= float(op_source)
        elif line[0] == 'SQRTC':
            result_col = line[1]
            data[result_col] = data[line[2]]
            data[result_col] = data[result_col].apply(math.sqrt)
        elif line[0] == 'EXPC':
            result_col = line[1]
            data[result_col] = data[line[2]]
            data[result_col] = data[result_col].apply(math.exp)
        elif line[0] == 'SHIFT':
            result_col = line[1]
            if len(line) == 4:
                data[result_col] = data[line[2]].shift(int(line[3]))
            elif len(line) == 5:
                bit_start = int(line[3])
                bit_end = int(line[4])
                series = []
                for i in range(bit_start, bit_end + 1):
                    data['%s_sft_%d' % (result_col, i)] = data[line[2]].shift(i)
                    series.append('%s_sft_%d' % (result_col, i))
                shift_series[result_col] = series
    return data
