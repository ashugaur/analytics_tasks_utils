# %% Import functions

## Dependencies
import pandas as pd
import zipfile


## import_csv_within_zip
def import_csv_within_zip(
    zip_filename,
    filename,
    sep=",",
    header=0,
    parse_dates=None,
    encoding=None,
    na_values=None,
    skiprows=0,
    index_col=0,
    skipfooter=0,
    names=None,
):
    """
    Import a CSV file within a zip archive with flexible options.

    Parameters:
    - zip_filename (str): Path to the zip file.
    - filename (str): Name of the CSV file within the zip archive.
    - sep (str, optional): Delimiter to use. Default is ','.
    - header (int, optional): Row number to use as column names. Default is 0.
    - parse_dates (list or None, optional): Columns to parse as dates. Default is None.
    - encoding (str or None, optional): Encoding to use. Default is None.
    - na_values (list or None, optional): Additional strings to recognize as NA/NaN. Default is None.

    Returns:
    - pd.DataFrame: DataFrame containing the CSV data.
    """
    with zipfile.ZipFile(zip_filename) as zf:
        with zf.open(filename) as file:
            df = pd.read_csv(
                file,
                sep=sep,
                header=header,
                parse_dates=parse_dates,
                encoding=encoding,
                na_values=na_values,
                skiprows=skiprows,
                index_col=index_col,
                skipfooter=skipfooter,
                names=names,
            )
    return df


## import_excel_within_zip
def import_excel_within_zip(
    zip_filename,
    filename,
    sheet_name=0,
    header=0,
    usecols=None,
    parse_dates=None,
    encoding=None,
    na_values=None,
    skiprows=0,
    index_col=0,
):
    """
    Import an Excel file within a zip archive with flexible options.

    Parameters:
    - zip_filename (str): Path to the zip file.
    - filename (str): Name of the Excel file within the zip archive.
    - sheet_name (str, int, or None, optional): The sheet name or index to read. Default is 0 (first sheet).
    - header (int, optional): Row number to use as column names. Default is 0.
    - usecols (str, list, or None, optional): Which columns to read. Default is None (all columns).
    - parse_dates (list or None, optional): Columns to parse as dates. Default is None.
    - encoding (str or None, optional): Encoding to use. Default is None.
    - na_values (list or None, optional): Additional strings to recognize as NA/NaN. Default is None.
    - skiprows (int or list, optional): Number of rows to skip or a list of row indices to skip. Default is 0.
    - index_col (int, str, or None, optional): Column(s) to set as the index. Default is 0.

    Returns:
    - pd.DataFrame: DataFrame containing the Excel data.
    """
    import pandas as pd
    import zipfile

    with zipfile.ZipFile(zip_filename) as zf:
        with zf.open(filename) as file:
            df = pd.read_excel(
                file,
                sheet_name=sheet_name,
                header=header,
                usecols=usecols,
                parse_dates=parse_dates,
                # encoding=encoding,
                na_values=na_values,
                skiprows=skiprows,
                index_col=index_col,
            )
    return df


## import_txt_within_zip
def import_txt_within_zip(
    zip_filename,
    filename,
    sep="\t",
    header=None,
    parse_dates=None,
    encoding=None,
    na_values=None,
    skiprows=0,
    index_col=None,
    skipfooter=0,
    names=None,
):
    """
    Import a TXT file within a zip archive with flexible options.

    Parameters:
    - zip_filename (str): Path to the zip file.
    - filename (str): Name of the TXT file within the zip archive.
    - sep (str, optional): Delimiter to use. Default is '\t' (tab).
    - header (int or None, optional): Row number to use as column names. Default is None.
    - parse_dates (list or None, optional): Columns to parse as dates. Default is None.
    - encoding (str or None, optional): Encoding to use. Default is None.
    - na_values (list or None, optional): Additional strings to recognize as NA/NaN. Default is None.

    Returns:
    - pd.DataFrame: DataFrame containing the TXT data.
    """
    import pandas as pd
    import zipfile

    with zipfile.ZipFile(zip_filename) as zf:
        with zf.open(filename) as file:
            df = pd.read_csv(
                file,
                sep=sep,
                header=header,
                parse_dates=parse_dates,
                encoding=encoding,
                na_values=na_values,
                skiprows=skiprows,
                index_col=index_col,
                skipfooter=skipfooter,
                names=names,
            )
    return df
