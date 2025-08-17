# %% Import functions

## Dependencies
import zipfile
import pandas as pd
import json


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


## import_json_within_zip
def import_json_within_zip(
    zip_filename,
    filename,
    encoding=None,
    orient=None,
    typ="frame",
    dtype=None,
    convert_axes=None,
    convert_dates=True,
    keep_default_dates=True,
    precise_float=False,
    date_unit=None,
    lines=False,
):
    """
    Import a JSON file within a zip archive with flexible options.

    Parameters:
    - zip_filename (str): Path to the zip file.
    - filename (str): Name of the JSON file within the zip archive.
    - encoding (str or None, optional): Encoding to use. Default is None.
    - orient (str or None, optional): Indication of expected JSON string format.
    - typ (str, optional): Type of object to recover ('frame' or 'series'). Default is 'frame'.
    - dtype (bool or None, optional): If True, infer dtypes; if False, don't; if None, use inference. Default is None.
    - convert_axes (bool or None, optional): Try to convert the axes. Default is None.
    - convert_dates (bool, optional): If True, convert date-like columns. Default is True.
    - keep_default_dates (bool, optional): If True, parse default date-like columns. Default is True.
    - precise_float (bool, optional): If True, use precise float parsing. Default is False.
    - date_unit (str or None, optional): The timestamp unit. Default is None.
    - lines (bool, optional): If True, read the file as a JSON lines format. Default is False.

    Returns:
    - pd.DataFrame or pd.Series: Data from the JSON file.
    """
    with zipfile.ZipFile(zip_filename) as zf:
        with zf.open(filename) as file:
            if lines:
                # For JSON lines format
                data = []
                for line in file:
                    if encoding:
                        line = line.decode(encoding)
                    data.append(json.loads(line))
                df = pd.json_normalize(data)
            else:
                # For regular JSON
                if encoding:
                    content = file.read().decode(encoding)
                else:
                    content = file.read().decode("utf-8")
                df = pd.read_json(
                    content,
                    orient=orient,
                    typ=typ,
                    dtype=dtype,
                    convert_axes=convert_axes,
                    convert_dates=convert_dates,
                    keep_default_dates=keep_default_dates,
                    precise_float=precise_float,
                    date_unit=date_unit,
                )
    return df

## import_parquet_within_zip
def import_parquet_within_zip(
    zip_filename,
    filename,
    columns=None,
    **kwargs
):
    """
    Import a Parquet file within a zip archive.

    Parameters:
    - zip_filename (str): Path to the zip file.
    - filename (str): Name of the Parquet file within the zip archive.
    - columns (list or None, optional): List of columns to read. Default is None.
    - **kwargs: Additional keyword arguments for pd.read_parquet.

    Returns:
    - pd.DataFrame: DataFrame containing the Parquet data.
    """
    with zipfile.ZipFile(zip_filename) as zf:
        with zf.open(filename) as file:
            df = pd.read_parquet(
                file,
                columns=columns,
                **kwargs
            )
    return df


