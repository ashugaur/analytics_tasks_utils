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
df = pd.DataFrame({"A": [1, 2, 3, 4]})
dataframe_to_data_table(df)
dataframe_to_data_table(df, out_file="x.html")
dataframe_to_data_table(
    df, func="generate_data_table_from_dataframe_internet", out_file="x.html"
)


## dataframe_to_excel
df = pd.DataFrame({"Column A": [1, 2, 3, 4]})
# df = pd.read_clipboard()
dataframe_to_excel(
    df,
    out_file=Path("C:/my_disk/____tmp/qc.xlsx"),
    sheet_name="df",
    start_row=10,
    report_headers=[
        {
            "cell": "A1",
            "value": "Report name",
            "bold": True,
            "font_size": 11,
            "color": "#004992",
        },
        {"cell": "B1", "value": "First report"},
        {
            "cell": "A2",
            "value": "Date",
            "bold": True,
            "font_size": 11,
            "color": "#004992",
        },
        {"cell": "B2", "value": "15-11-2025"},
        {
            "cell": "A3",
            "value": "Filter",
            "bold": True,
            "font_size": 11,
            "color": "#004992",
        },
        {"cell": "B3", "value": "Paid claims"},
        {
            "cell": "A4",
            "value": "Note",
            "bold": True,
            "font_size": 11,
            "color": "#004992",
        },
        {"cell": "B4", "value": "No notes as of now", "bg_color": "#FFFFCC"},
    ],
    page_bg_color="#FFFFFF",
    header_bg_color="#FAF4F4",
    data_bg_color="#FFFFFF",
    border_color="#EBEBEDFF",
    column_formats={
        "sum_A": "#,##0",
        "Support": "0.0%",
        "Confidence": "0.0%",
    },
    data_bars={"Support": "#5F799A", "Confidence": "#FFC000"},
    open_file=1,
)


# %% Formatting

## round_columns
round_columns(pd.DataFrame({"a": [1.4343, 2.4564]}), "a", 2)


# %% OS

## open_file_folder
open_file_folder(Path("C:/my_disk/____tmp"))


# %% Reporting
## eda_snapshot
eda_snapshot(pd.DataFrame({"a": [1, 2, 3]}))
