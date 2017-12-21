# DEPENDENCY ( pandas )

import pandas as pd


class SelectHdl:
    def __init__(self, csv_path):
        self.full_data = pd.read_csv(csv_path)

        
a=SelectHdl("F:/1220.csv")
