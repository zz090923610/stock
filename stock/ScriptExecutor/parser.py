import pandas as pd
import os
import math
import re
import multiprocessing as mp
from stock.common.variables import COMMON_VARS_OBJ


def load_data(input_data):
#    print('func load_data(input_data)\n'
#          '%s %s' % (type(input_data), input_data))
    if type(input_data) == pd.core.frame.DataFrame:
        data = input_data
    elif type(input_data) == str:
        try:
            data = pd.read_csv(determine_input_path(input_data))
        except FileNotFoundError:
#            print('Load data file failed: %s' % input_data)
            data = None
    else:
        data = None
    return data


def determine_input_path(input_path):
    if os.path.isfile(input_path):
        return input_path
    elif input_path.split('/')[0] in os.listdir(COMMON_VARS_OBJ.QA_DIR):
        if os.path.exists(COMMON_VARS_OBJ.QA_DIR + '/' + input_path):
            return COMMON_VARS_OBJ.QA_DIR + '/' + input_path
    else:
        return input_path


def determine_output_path(output_path):
    if os.path.isfile(output_path):
        return output_path
    elif output_path.split('/')[0] in os.listdir(COMMON_VARS_OBJ.QA_DIR):
        return COMMON_VARS_OBJ.QA_DIR + '/' + output_path
    else:
        return COMMON_VARS_OBJ.QA_DIR + '/' + output_path


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
            input_dir_file =determine_input_path( line[1])
        elif line[0] == 'PLFDOUT':
            output_dir_file = determine_output_path(line[1])
        elif line[0] == 'SGFLOUT':
            output_dir_file = determine_output_path(line[1])
        elif line[0] == 'OUTCOLS':
            output_cols = re.split(r',', line[1])
    print(23333, input_dir_file)

    print("Parallel level: %s\nInput path: %s\n Output path: %s\n Output cols: %r" %
          (parallel_level, input_dir_file, output_dir_file, output_cols))
    return script, parallel_level, input_dir_file, output_dir_file, output_cols


def engine(script_path):
    script, parallel_level, input_dir_file, output_dir_file, output_cols = parse_script_head(script_path)
    if parallel_level == 'FOLDER':
        dir_list = os.listdir(input_dir_file)
        input_dir = input_dir_file.rstrip('/')
        print(input_dir)
        output_dir = output_dir_file.rstrip('/')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        pool = mp.Pool()
        for i in dir_list:
            pool.apply_async(execute_script, args=(input_dir + '/' + i, script, output_dir + '/' + i, output_cols))
        pool.close()
        pool.join()
    elif parallel_level == 'SINGLE':
        execute_script(input_dir_file, script, output_dir_file, output_cols)


class ScriptVariable:
    def __init__(self, v_type, v_name, v_val=None, series=None):
        """
        :param v_type: vars,imms,series,cols
        """
        if series is None:
            series = []
        self.v_type = v_type
        self.v_val = v_val
        self.v_name = v_name
        self.mutable = True
        self.series = series

    def gen_sub_series_list(self, series_str):
        series_list = []
        splited_str = series_str.split('_')
        name = splited_str[0]
        if len(splited_str) == 2:
            start = 0
            end = int(splited_str[1])
        elif len(splited_str) == 3:
            start = int(splited_str[1])
            end = int(splited_str[2])
        else:
            start = 0
            end = len(self.series)
        for i in range(start, end):
            series_list.append('%s_SERIES_%d' % (name, i))
        return series_list

    def respond(self, pass_in=''):
        if self.v_type == 'var':
            return [self.v_val]
        elif self.v_type == 'imm':
            return [self.v_val]
        elif self.v_type == 'col':
            return [self.v_name]
        elif self.v_type == 'series':
            if pass_in != self.v_name:
                return self.gen_sub_series_list(pass_in)
            else:
                return self.gen_sub_series_list(self.v_name)
    def print_self(self):
        print(self.v_name,self.v_type,self.v_val,self.series)


class VariableHdl:
    def __init__(self):
        self.vdict = {}

    def get_var_by_name(self, v_name):
        if v_name in self.vdict.keys():
            return self.vdict[v_name]
        else:
            return None

    def add_var(self, v_name, v_type, v_val=None, series=None):
        self.vdict[v_name] = ScriptVariable(v_type, v_name, v_val=v_val, series=series)

    def respond_var(self, v_name):
        if v_name.split('_')[0] in self.vdict.keys():
            return self.vdict[v_name.split('_')[0]].respond(pass_in=v_name)
        elif is_num(v_name):
            return [float(v_name)]
        else:
            return []


# noinspection PyShadowingBuiltins
def execute_script(input_data, script, output_path, output_cols):
    data = load_data(input_data)
    data_cols = data.columns.tolist()
    var_hdl = VariableHdl()
    for i in data_cols:
        var_hdl.add_var(i, 'col')

    for line in script:
        if line[0] == 'ADDC':
            opts_cols = []
            for op_source in line[2:]:
                opts_cols += var_hdl.respond_var(op_source)
            result_col_name = line[1]
            data[result_col_name] = 0
            for col in opts_cols:
                if is_num(col):
                    data[result_col_name] += col
                else:
                    data[result_col_name] += data[col]
            var_hdl.add_var(result_col_name, 'col')
        elif line[0] == 'SUBC':
            opts_cols = []
            for op_source in line[2:]:
                opts_cols += var_hdl.respond_var(op_source)
            result_col_name = line[1]
            data[result_col_name] =data[opts_cols[0]]
            for col in opts_cols[1:]:
                if is_num(col):
                    data[result_col_name] -= col
                else:
                    data[result_col_name] -= data[col]
            var_hdl.add_var(result_col_name, 'col')
        elif line[0] == 'MULC':
            opts_cols = []
            for op_source in line[2:]:
                opts_cols += var_hdl.respond_var(op_source)
            result_col_name = line[1]
            data[result_col_name] = data[opts_cols[0]]
            for col in opts_cols[1:]:
                if is_num(col):
                    data[result_col_name] *= col
                else:
                    data[result_col_name] *= data[col]
            var_hdl.add_var(result_col_name, 'col')
        elif line[0] == 'DIVC':
            opts_cols = []
            for op_source in line[2:]:
                opts_cols += var_hdl.respond_var(op_source)
            result_col_name = line[1]
            data[result_col_name] = data[opts_cols[0]]
            for col in opts_cols[1:]:
                if is_num(col):
                    data[result_col_name] /= col
                else:
                    data[result_col_name] /= data[col]
            var_hdl.add_var(result_col_name, 'col')
        elif line[0] == 'MODC':
            opts_cols = []
            for op_source in line[2:]:
                opts_cols += var_hdl.respond_var(op_source)
            result_col_name = line[1]
            data[result_col_name] = data[opts_cols[0]]
            for col in opts_cols[1:]:
                if is_num(col):
                    data[result_col_name] %= col
                else:
                    data[result_col_name] %= data[col]
            var_hdl.add_var(result_col_name, 'col')
        elif line[0] == 'SQRTC':
            result_col_name = line[1]
            data[result_col_name] = data[line[2]]
            data[result_col_name] = data[result_col_name].apply(math.sqrt)
            var_hdl.add_var(result_col_name, 'col')
        elif line[0] == 'EXPC':
            result_col_name = line[1]
            data[result_col_name] = data[line[2]]
            data[result_col_name] = data[result_col_name].apply(math.exp)
            var_hdl.add_var(result_col_name, 'col')
        elif line[0] == 'SHIFT':
            result_col_name = line[1]
            if len(line) == 4:
                data[result_col_name] = data[line[2]].shift(int(line[3]))
                var_hdl.add_var(result_col_name, 'col')
            elif len(line) == 5:
                bit_start = int(line[3])
                bit_end = int(line[4])
                series_member = []
                for i in range(bit_start, bit_end):
                    data['%s_SERIES_%d' % (result_col_name, i)] = data[line[2]].shift(i)
                    series_member.append('%s_SERIES_%d' % (result_col_name, i))
                    var_hdl.add_var('%s_SERIES_%d' % (result_col_name, i), 'col')
                var_hdl.add_var(result_col_name,'series',series=series_member)
        elif line[0] == 'VAR':
            val = float(line[2])
            result_col_name = line[1]
            var_hdl.add_var(result_col_name, 'var', v_val=val)
        elif line[0] == 'IMM':
            val = float(line[2])
            result_col_name = line[1]
            var_hdl.add_var(result_col_name, 'imm', v_val=val)

    data[output_cols].to_csv(output_path, index=False)
    # return data,shift_series
