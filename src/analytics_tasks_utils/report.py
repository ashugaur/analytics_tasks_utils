# %% Report

## Dependencies
import numpy as np
import pandas as pd


# %% eda_snapshot


def print_section_header(title):
    """Prints a section header with a title and a line of equals signs or hyphens."""
    print(f"\n{title}")
    print("-" * len(title))


def count_unique_records_in_each_field(df):
    """Prints the count of unique records in each field of the DataFrame."""
    unique_counts = df.nunique()
    print(unique_counts)


def eda_snapshot(df, df_name="DataFrame"):
    """
    Performs exploratory data analysis on the given DataFrame and prints the results.

    Parameters:
    df (pd.DataFrame): The DataFrame to analyze.
    df_name (str): The name of the DataFrame (default is "DataFrame").
    """
    print_section_header(f"eda.snapshot: {df_name}")

    print_section_header(f"Info: {df_name}")
    print(df.info())

    print_section_header(f"Random two rows: {df_name}")
    print(df.head(2).T)

    print_section_header(
        f"Count of unique records in each field: #{len(df)} rows in {df_name}"
    )
    count_unique_records_in_each_field(df)

    print_section_header(f"Describe all fields: {df_name}")
    print(df.describe(include="all").T)

    print_section_header(
        f"Describe all numeric fields broken by percentiles: {df_name}"
    )
    print(
        round(
            df.describe(
                include=[np.number],
                percentiles=[0.01, 0.05, 0.10, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99],
            ).T,
            2,
        )
    )

    print_section_header(f"Count of missing rows: {df_name}")
    df_s4 = pd.DataFrame(
        {
            "count_null": df.isnull().sum(),
            "% null": round(df.isnull().sum() / len(df) * 100, 2),
        }
    )
    print(df_s4)
