import os,sys
import numpy as np
import pandas as pd

class PuckConfig():
    def __init__(self, configfile):
        self.configfile=configfile
        self.isRead=False

    def readConfig(self):
        # Pandas read csv
        self.df = pd.read_csv(self.configfile)
        print(self.df)
        self.df.head()

        def reprep(row_data):
            print(row_data)
            if row_data.rfind("h")!=-1:
                value=float(row_data.replace("h",""))
                print(value)
            elif row_data.rfind("H")!=-1:
                value=float(row_data.replace("h",""))
                print(value)
            elif row_data.rfind("s")!=-1:
                value=float(row_data.replace("s",""))
                print(value)
            elif row_data.rfind("S")!=-1:
                value=float(row_data.replace("S",""))
                print(value)
            elif row_data.rfind("m")!=-1 or row_data.rfind("M")!=-1:
                print("minutes!")
            return 1.0

        # Condition 
        self.df['result'] = self.df['time'].apply(reprep)
        print(self.df['result'])
        # Remove space from the line string
        self.isRead=True
    
if __name__ == "__main__":
    pc=PuckConfig(sys.argv[1])
    pc.readConfig()