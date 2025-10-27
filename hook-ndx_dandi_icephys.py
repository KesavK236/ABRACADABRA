# hook-ndx_dandi_icephys.py
from PyInstaller.utils.hooks import collect_data_files

# include the entire spec folder with YAMLs
datas = collect_data_files(
    'ndx_dandi_icephys',
    includes=['spec/*.yaml', 'spec/*.yml']
)