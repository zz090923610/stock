import pandas as pd
import os


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


def parse_script(input_data, script_path, output_method):
    data = load_data(input_data)




