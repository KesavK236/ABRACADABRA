import os
import sys
import numpy as np 
import pandas as pd 
from logic.rheo_1s import rheo_1s
from logic.short_rheo_1s import short_rheo_1s
from datetime import datetime

metadata_filepath = "C://Users//kesav//Box//PL_Data_Zheng-Liu_Project-20250821T155717Z-1-004//PL_Data_Zheng-Liu_Project//MetaData.xlsx"
df = pd.read_excel(metadata_filepath)

df['Folder Name'] = df['Abf File Name'].astype(str).str[:5]
df['Full File Name'] = df['Abf File Name'].astype(str) + ".abf"

file_names = df['Abf File Name'].astype(str).tolist()
root_dir = r"C:\Users\kesav\Box\PL_Data_Zheng-Liu_Project-20250821T155717Z-1-004\PL_Data_Zheng-Liu_Project\compiled abfs"

file_paths = []
count = 0
for dirpath, dirnames, filenames in os.walk(root_dir):
    for f in filenames:
        name_only, ext = os.path.splitext(f)
        count += 1
        if name_only in file_names:
            
            file_paths.append(os.path.join(dirpath, f))


testfile = file_paths[8]
current_dir = os.getcwd()
os.makedirs("testfeeder4", exist_ok=True)
os.chdir("testfeeder4")
testname= os.path.basename(testfile)
testdf = pd.DataFrame(index=[testname])


testdf, pp_1s, erm = short_rheo_1s(testfile, testdf, dvdt=20, check_threshold=False, output_dir=os.getcwd())
timesstamps = []
timesstamps.append({"Start:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
print(timesstamps)
error_list_rheo1 = []
error_list_single = []
for i in range(len(file_paths)):
    file = file_paths[i]
    filename= os.path.basename(file)
    filedf = pd.DataFrame(index=[filename])
    try:
        filedf, pp_1s, erm = short_rheo_1s(file, filedf, dvdt=20, check_threshold=False, output_dir=os.getcwd())
    except:
        error_list_single.append(os.path.basename(file))
    testdf = pd.concat([testdf, filedf], ignore_index=False, sort=False)

timesstamps.append({"End:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
testdf.to_csv("testoutput.csv")
print(error_list_rheo1)
print(error_list_single)
print(timesstamps)
    