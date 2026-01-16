import os
import sys
import numpy as np 
import pandas as pd 
from logic.rmp import rmp
from logic.rheo_1s import rheo_1s
from logic.rheo_4x import rheo_4x
from logic.ramp_1s import ramp_1s
from logic.ramp_4x import ramp_4x
from logic.short_rheo_5ms import short_rheo_5ms
from logic.short_rheo_1s import short_rheo_1s
from datetime import datetime

current_dir = os.getcwd()
os.makedirs("testfeeder4", exist_ok=True)
os.chdir("testfeeder4")

files = r"C:\Users\kesav\OneDrive\WashU\Copits Lab\ABRACADABRA Bulk\AD_hdrg_filepaths.xlsx"
files_df = pd.read_excel(files)
files_df
e1 = []
e2 = []
e3 = []
e4 = []
e5 = []
e6 = []
testdf = pd.DataFrame()
for idx, row in files_df.iterrows():
    # row is a Series, so you can access each feature by column name
    f1 = row["RMP file"]
    f2 = row["1s rheo file"]
    f3 = row["4x rheo file"]
    f4 = row["1s ramp file"]
    f5 = row["4x ramp file"]
    f6 = row["short rheo file"]
    try:
        filename= os.path.basename(f1)
        filedf = pd.DataFrame(index=[filename])
    except:
        filename= os.path.basename(f2)
        filedf = pd.DataFrame(index=[filename])
    # if pd.notna(f1):
    #     try:
    #         filedf["RMP"] = None
    #         filedf, erm1 = rmp(f1, filedf, output_dir=os.getcwd())
    #         if erm1 != "":
    #             filedf["Errors in F1"] = erm1
    #     except:
    #         e1.append(f1)
    if pd.notna(f2):
        try:
            filedf["Rheo 1s"] = None
            filedf, pp1s, erm2 = short_rheo_1s(f2, filedf, dvdt=10, output_dir=os.getcwd())
            if erm2 != "":
                filedf["Errors in F2"] = erm2
        except:
            e2.append(f2)
    # if pd.notna(f3):
    #     try:
    #         filedf["Rheo 4x"] = None
    #         filedf, erm3 = rheo_4x(f3, filedf, dvdt=10, output_dir=os.getcwd(), check_ap_counts=True)
    #         if erm3 != "":
    #             filedf["Errors in F3"] = erm3
    #     except:
    #         e3.append(f3)
    if pd.notna(f4):
        try:
            filedf["Ramp 1s"] = None
            filedf, erm4 = ramp_1s(f4, filedf, dvdt=10, output_dir=os.getcwd())
            if erm4 != "":
                filedf["Errors in F4"] = erm4
        except:
            e4.append(f4)
    # if pd.notna(f5):
    #     try:
    #         filedf["Ramp 4x"] = None
    #         filedf, erm5 = ramp_4x(f5, filedf, dvdt=10, output_dir=os.getcwd(), check_ap_counts=True)
    #         if erm5 != "":
    #             filedf["Errors in F5"] = erm5
    #     except:
    #         e5.append(f5)
    if pd.notna(f6):
        try:
            filedf["Short Rheo 5ms"] = None
            filedf, pp5ms, erm6 = short_rheo_5ms(f6, filedf, dvdt=10, output_dir=os.getcwd())
            if erm6 != "":
                filedf["Errors in F6"] = erm6
        except:
            e6.append(f6)
    
    testdf = pd.concat([testdf, filedf], ignore_index=False, sort=False)
testdf = testdf.transpose()
testdf.to_csv(r"C:\Users\kesav\OneDrive\WashU\Copits Lab\ABRACADABRA Bulk\AD_hdrg_results101.csv")
print(e1)
print(e2)
print(e3)
print(e4)
print(e5)
print(e6)