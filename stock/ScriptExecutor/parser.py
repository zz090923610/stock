import pandas as pd
import os
import math
import re
import multiprocessing as mp
from stock.common.variables import COMMON_VARS_OBJ



def load_data(input_data):
    print('func load_data(input_data)\n'
          '%s %s' %(type(input_data), input_data))
    if type(input_data) == pd.core.frame.DataFrame:
        data = input_data
    elif type(input_data) == str:
        if os.path.isfile(input_data):
            print('External path')
            data = pd.read_csv(input_data)
        elif input_data.split('/')[0] in os.listdir(COMMON_VARS_OBJ.QA_DIR):
            print('Internal path, absolute path: %s' % COMMON_VARS_OBJ.QA_DIR + '/' + input_data)
            if os.path.isfile(COMMON_VARS_OBJ.QA_DIR + '/' + input_data):
                data = pd.read_csv(COMMON_VARS_OBJ.QA_DIR + '/' + input_data)
            else:
                data = None
        else:
            data = None
    else:
        data = None
    return data


def determine_output_path(output_path):
    if os.path.isfile(output_path):
        print('External path')
        return output_path
    elif output_path.split('/')[0] in os.listdir(COMMON_VARS_OBJ.QA_DIR):
        print('Internal path, absolute path: %s' % COMMON_VARS_OBJ.QA_DIR + '/' + output_path)
        return COMMON_VARS_OBJ.QA_DIR + '/' + output_path
    else:
        return output_path


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


def parse_script_head(script_path):
    script = load_script(script_path)
    parallel_level = ''  # FOLDER/SINGLE
    input_dir_file = ''
    output_dir_file = ''
    output_cols = []
    for line in script:
        if line[0] == 'PLEV':
            parallel_level = line[1]
        elif line[0] == 'FIN':
            input_dir_file = line[1]
        elif line[0] == 'PLFDOUT':
            output_dir_file = line[1]
        elif line[0] == 'SGFLOUT':
            output_dir_file = line[1]
        elif line[0] == 'OUTCOLS':
            output_cols = re.split(r',', line[1])
    print("Parallel level: %s\nInput path: %s\n Output path: %s\n Output cols: %r" %
          (parallel_level, input_dir_file, output_dir_file, output_cols))
    return script, parallel_level, input_dir_file, output_dir_file, output_cols


def engine(script_path):
    script, parallel_level, input_dir_file, output_dir_file, output_cols = parse_script_head(script_path)
    if parallel_level == 'FOLDER':
        dir_list = os.listdir(input_dir_file)
        input_dir = input_dir_file.rstrip('/')
        output_dir = output_dir_file.rstrip('/')
        os.makedirs(output_dir)
        pool = mp.Pool()
        for i in dir_list:
            pool.apply_async(execute_script, args=(i, input_dir + '/' + i, output_dir + '/' + i, output_cols))
        pool.close()
        pool.join()
    elif parallel_level == 'SINGLE':
        execute_script(input_dir_file, script, output_dir_file, output_cols)


# noinspection PyShadowingBuiltins
def execute_script(input_data, script, output_path, output_cols):
    data = load_data(input_data)
    data_cols = data.columns.tolist()
    vars = {}
    imms = {}
    shift_series = {}
    for line in script:
        if line[0] == 'ADDC':
            result_col = line[1]
            data[result_col] = 0
            for op_source in line[2:]:
                if op_source.split('_')[0] in shift_series.keys():
                    for i in range(int(op_source.split('_')[1]),int(op_source.split('_')[2])):
                       data[result_col] += data[op_source.split('_')[0]+'_sft_%d' % i]
                elif op_source in data_cols:
                    data[result_col] += data[op_source]
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
                series_member = []
                for i in range(bit_start, bit_end):
                    data['%s_sft_%d' % (result_col, i)] = data[line[2]].shift(i)
                    series_member.append('%s_SFT_%d' % (result_col, i))
                shift_series[result_col] = series_member

    data[output_cols].to_csv(determine_output_path(output_path), index=False)
    # return data,shift_series
