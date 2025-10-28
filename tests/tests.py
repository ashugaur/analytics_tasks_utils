# %% Test functions

## Dependencies
import pandas as pd
from pathlib import Path

from analytics_tasks_utils.controlling import log_start, log_end, timer_start, timer_end
from analytics_tasks_utils.exporting import dataframe_to_data_table, dataframe_to_excel
from analytics_tasks_utils.formatting import round_columns
from analytics_tasks_utils.os_functions import open_file_folder
from analytics_tasks_utils.reporting import eda_snapshot


# %% Control

## Logging
_tmp = Path("C:/my_disk/____tmp")
log_start(_tmp)
log_end()

## Timer
timer_start()
timer_end()


# %% Exporting

## dataframe_to_data_table
df = pd.DataFrame({'A': [1,2,3,4]})
dataframe_to_data_table(df)
dataframe_to_data_table(df, out_file='x.html')
dataframe_to_data_table(df, func='generate_data_table_from_dataframe_internet', out_file='x.html')


## dataframe_to_excel
df = pd.DataFrame({'A': [1,2,3,4]})
dataframe_to_excel(df)
dataframe_to_excel(df, sheet_name='df')
dataframe_to_excel(df, out_file=Path("C:/my_disk/____tmp/qc.xlsx"), sheet_name='df')


# %% Formatting

## round_columns
round_columns(pd.DataFrame({"a": [1.4343, 2.4564]}), "a", 2)


# %% OS

## open_file_folder
open_file_folder(Path("C:/my_disk/____tmp"))


# %% Reporting
## eda_snapshot
eda_snapshot(pd.DataFrame({"a": [1, 2, 3]}))
