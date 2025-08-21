# %% Operating system

## Dependencies
import pyperclip
import textwrap
import pandas as pd
from pathlib import Path
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
from nbclient import execute
from nbformat import read, write
from nbconvert import HTMLExporter, MarkdownExporter
from nbconvert.writers import FilesWriter
import subprocess as sp
from bs4 import BeautifulSoup
import os
import re
from nbconvert import PythonExporter
import mammoth
import markdownify
import math


def create_bins_categorical(df, column_name=None, nbr_of_bins=5):
    """
    Create bins for a categorical column.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.  The function does **not** modify the original frame.
    column_name : str | None
        Column to bin.  If None, the first non‑numeric column is used.
    nbr_of_bins : int
        Desired number of bins.

    Returns
    -------
    tuple
        (df_copy, column_name, bins)
    """
    # Work on a copy to preserve the original df
    df_copy = df.copy()

    # Infer column if not supplied
    if column_name is None:
        cat_cols = df_copy.select_dtypes(include=["object", "category"]).columns
        if not cat_cols.size:
            raise ValueError(
                "No categorical columns found; please specify `column_name`."
            )
        column_name = cat_cols[0]

    # Ensure the column exists
    if column_name not in df_copy.columns:
        raise KeyError(f"Column '{column_name}' not found in DataFrame.")

    # Get unique values and sort them
    unique_values = sorted(df_copy[column_name].dropna().unique())

    if len(unique_values) < nbr_of_bins:
        raise ValueError(
            f"Not enough unique values ({len(unique_values)}) for {nbr_of_bins} bins."
        )

    # Number of values per bin
    values_per_bin = math.ceil(len(unique_values) / nbr_of_bins)

    # Create the bins (list of lists)
    bins = [
        unique_values[i : i + values_per_bin]
        for i in range(0, len(unique_values), values_per_bin)
    ]

    return df_copy, column_name, bins


def generate_sql_case_statement_categorical(column_name, bins, null_label="00000"):
    """
    Build a SQL CASE statement that maps categorical values to bin labels.

    Parameters
    ----------
    column_name : str
        Name of the column in the SQL table.
    bins : list[list]
        Bins returned by ``create_bins_categorical``.
    null_label : str, optional
        Value returned for NULL entries.

    Returns
    -------
    str
        The CASE statement as a string.
    """
    case_statement_sql = "CASE\n"

    # Construct WHEN/THEN clauses
    for i, bin_values in enumerate(bins):
        # Quote strings, leave numbers as‑is
        bin_vals_sql = ", ".join(
            f"'{v}'" if isinstance(v, str) else str(v) for v in bin_values
        )
        case_statement_sql += (
            f"    WHEN `{column_name}` IN ({bin_vals_sql}) THEN 'Bin_{i + 1}'\n"
        )

    # Optional handling of NULLs
    if null_label is not None:
        case_statement_sql += f"    WHEN `{column_name}` IS NULL THEN '{null_label}'\n"

    case_statement_sql += f"    ELSE '{null_label}'\nEND AS `{column_name}_bins`"

    return case_statement_sql


if __name__ == "__main__":
    df = pd.DataFrame({"bining_column": ["zebra", "bat", "cat", "rat", "mouse", "dog"]})

    df, column_name, bins = create_bins_categorical(df, nbr_of_bins=3)
    case_statement_sql = generate_sql_case_statement_categorical(column_name, bins)

    print(case_statement_sql)


def generate_pandas_case_statement_categorical(df, column_name, bins):
    # Create a dictionary to map each unique value to its corresponding bin label
    bin_dict = {value: f"Bin_{i + 1}" for i, bin in enumerate(bins) for value in bin}

    # Replace the values in the column with their corresponding bin labels
    df[f"{column_name}_bins"] = df[column_name].map(bin_dict).fillna("00000")

    return df


if __name__ == "__main__":
    df = pd.DataFrame({"bining_column": ["zebra", "bat", "cat", "rat", "mouse", "dog"]})

    df, column_name, bins = create_bins_categorical(df, nbr_of_bins=3)
    case_statement_pandas = generate_pandas_case_statement_categorical(
        df, column_name, bins
    )

    print(case_statement_pandas)


def create_bins_numeric(df, column_name, nbr_of_bins=5, range_min=0, range_max=100):
    # Make a copy to avoid modifying the original dataframe
    df = df.copy()
    df.columns = df.columns.str.lower()

    # Use the lowercased column name
    column_name_lower = column_name.lower()

    # Convert the column to numeric, dropping any non-numeric values
    df[column_name_lower] = pd.to_numeric(df[column_name_lower], errors="coerce")
    df = (
        df.dropna().sort_values(column_name_lower).reset_index(drop=True)
    )  # Sort the data and reset index

    if df[column_name_lower].empty:
        raise ValueError("No numeric data found after conversion.")

    # Calculate bins using the entire data range
    bins_default = pd.cut(df[column_name_lower], bins=nbr_of_bins)  # Default bins

    # Create bins based on manually specified range_min and range_max
    # Use float division to ensure proper bin width calculation
    bin_width = (range_max - range_min) / nbr_of_bins
    bins_rounded = np.arange(range_min, range_max + bin_width, bin_width)
    bins_rounded_cut = pd.cut(
        df[column_name_lower], bins=bins_rounded, include_lowest=True, right=False
    )

    # Add both bins to the dataframe
    df["bins_default"] = bins_default  # Default bins based on data distribution
    df["bins_rounded"] = bins_rounded_cut  # Manually specified range bins

    return df, column_name_lower


def generate_sql_case_statement_numeric(df, column_name):
    unique_bins = df["bins_rounded"].dropna().unique()
    case_statement = "case\n"

    for bin_range in unique_bins:
        lower, upper = bin_range.left, bin_range.right
        # Construct the case statement
        case_statement += f"    when {column_name} >= {lower} and {column_name} < {upper} then '{bin_range}'\n"

    case_statement += f"    else '00000'\nend as {column_name}_bins"

    return case_statement


if __name__ == "__main__":
    df = pd.DataFrame({"bining_column": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]})

    result, column_name = create_bins_numeric(
        df, column_name="bining_column", nbr_of_bins=5, range_min=0, range_max=15
    )
    case_statement_sql = generate_sql_case_statement_numeric(result, column_name)

    print(case_statement_sql)
    print("\nDataFrame with bins:")
    print(result)


def dataframe_to_dict(df, key_col, value_col):
    """
    Converts two columns of a pandas DataFrame into a dictionary.

    Args:
      df: The pandas DataFrame.
      key_col: The name of the column to use as keys.
      value_col: The name of the column to use as values.

    Returns:
      A dictionary where keys are from key_col and values are from value_col.
      Returns an empty dictionary if key_col or value_col are not found in the dataframe.
    """
    if key_col not in df.columns or value_col not in df.columns:
        print(f"Error: Column '{key_col}' or '{value_col}' not found in DataFrame.")
        return {}

    return dict(zip(df[key_col], df[value_col]))


if __name__ == "__main__":
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 28],
        "City": ["New York", "London", "Tokyo"],
    }
    df = pd.DataFrame(data)

    # Convert 'Name' and 'Age' columns to a dictionary
    name_age_dict = dataframe_to_dict(df, "Name", "Age")
    print("Name to Age Dictionary:", name_age_dict)

    # Convert 'City' and 'Name' columns to a dictionary
    city_name_dict = dataframe_to_dict(df, "City", "Name")
    print("City to Name Dictionary:", city_name_dict)

    # Example of error handling:
    invalid_dict = dataframe_to_dict(df, "NotAColumn", "Age")
    print("Invalid Dictionary:", invalid_dict)

    # Example with duplicate keys. Last value will be kept.
    duplicate_data = {"ID": [1, 2, 1, 3], "Value": ["A", "B", "C", "D"]}
    duplicate_df = pd.DataFrame(duplicate_data)
    duplicate_dict = dataframe_to_dict(duplicate_df, "ID", "Value")
    print("Duplicate Key Dictionary:", duplicate_dict)


# %% dataframe_to_dict_list


def dataframe_to_dict_list(df, key_col, value_col):
    """
    Converts two columns of a pandas DataFrame into a dictionary, storing values in lists.

    Args:
        df: The pandas DataFrame.
        key_col: The name of the column to use as keys.
        value_col: The name of the column to use as values.

    Returns:
        A dictionary where keys are from key_col and values are lists of values from value_col.
        Returns an empty dictionary if key_col or value_col are not found in the dataframe.
    """
    if key_col not in df.columns or value_col not in df.columns:
        print(f"Error: Column '{key_col}' or '{value_col}' not found in DataFrame.")
        return {}

    result_dict = {}
    for key, value in zip(df[key_col], df[value_col]):
        if key in result_dict:
            result_dict[key].append(value)
        else:
            result_dict[key] = [value]
    return result_dict


if __name__ == "__main__":
    data = {
        "parent": [
            "interactive",
            "interactive",
            "interactive",
            "interactive",
            "interactive",
            "interactive",
            "interactive",
        ],
        "parent_1": [
            "change",
            "compare",
            "correlation",
            "flow",
            "gantt",
            "maps",
            "test",
        ],
    }
    df = pd.DataFrame(data)

    result = dataframe_to_dict_list(df, "parent", "parent_1")
    print(result)

    # Example with more than one key
    data2 = {
        "parent": [
            "interactive",
            "interactive",
            "interactive",
            "static",
            "static",
            "static",
        ],
        "parent_1": ["change", "compare", "correlation", "flow", "gantt", "maps"],
    }
    df2 = pd.DataFrame(data2)

    result2 = dataframe_to_dict_list(df2, "parent", "parent_1")
    print(result2)

    # Example of error handling:
    invalid_dict = dataframe_to_dict_list(df, "NotAColumn", "parent_1")
    print("Invalid Dictionary:", invalid_dict)


def docx_to_md(
    source_folder,
    destination_folder,
    file_size_limit_in_mb=None,
    scan_subfolders=1,
    folder_structure=1,
):
    """
    Convert .docx files to .md format while optionally maintaining the folder structure.

    Parameters:
    - source_folder (str): Path to the source directory containing .docx files.
    - destination_folder (str): Path to the destination directory where .md files will be saved.
    - file_size_limit_in_mb (float, optional): Maximum file size in MB for conversion. Files larger than this will be skipped.
    - scan_subfolders (int, 0|1): If 1, scan subfolders recursively; if 0, process only the source folder.
    - folder_structure (int, 0|1): If 1, maintain folder structure in the destination; if 0, place all files in the destination folder.
    """

    # Define the custom style map for Mammoth
    style_map = """
    p[style-name='Contact Info'] => p.contact-info
    p[style-name='Normal1'] => p.normal
    p[style-name='Heading 31'] => h3
    """

    # Define file size limit in bytes, if specified
    file_size_limit_bytes = (
        file_size_limit_in_mb * 1024 * 1024 if file_size_limit_in_mb else None
    )

    for root, dirs, files in os.walk(source_folder):
        if not scan_subfolders and root != source_folder:
            continue

        # Filter `.docx` files in the current directory
        docx_files = [file for file in files if file.lower().endswith(".docx")]
        if not docx_files:
            continue  # Skip creating the destination directory if no .docx files are present

        for file in docx_files:
            source_file = os.path.join(root, file)

            # Determine destination path based on `folder_structure` parameter
            if folder_structure:
                relative_path = os.path.relpath(root, source_folder)
                dest_path = os.path.join(destination_folder, relative_path)
            else:
                dest_path = destination_folder

            os.makedirs(dest_path, exist_ok=True)
            destination_file = os.path.join(
                dest_path, os.path.splitext(file)[0] + ".md"
            )

            # Check file size limit
            if (
                file_size_limit_bytes
                and os.path.getsize(source_file) > file_size_limit_bytes
            ):
                print(f"Skipping {source_file}: File size exceeds the limit.")
                continue

            try:
                # Read and convert .docx to HTML using Mammoth
                with open(source_file, "rb") as docx_file:
                    result = mammoth.convert_to_html(docx_file, style_map=style_map)
                    html = result.value
                    messages = result.messages
                    if messages:
                        print(f"Messages for {source_file}: {messages}")

                # Parse the HTML with BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")

                for strong in soup.find_all("strong"):
                    strong.insert_before(soup.new_tag("br"))

                # Decrease heading levels dynamically
                for heading in soup.find_all(
                    ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9"]
                ):
                    current_level = int(
                        heading.name[1]
                    )  # Extract the current heading level (e.g., 1 for <h1>)
                    if (
                        current_level < 6
                    ):  # Only decrease if the level is less than 6 (since <h6> is the lowest level)
                        new_level = current_level + 1
                        heading.name = (
                            f"h{new_level}"  # Update the tag to the new level
                        )

                # Ensure paragraphs and line breaks are preserved
                for paragraph in soup.find_all("p"):
                    # Replace any `<br>` tags within paragraphs with actual line breaks for Markdown compatibility
                    paragraph_text = paragraph.decode_contents().replace("<br>", "\n")
                    paragraph.string = (
                        paragraph_text.strip()
                    )  # Replace content with line-preserved text

                # Get the modified HTML
                modified_html = str(soup)

                # Convert HTML to Markdown using Markdownify
                try:
                    markdown_content = markdownify.markdownify(
                        modified_html, heading_style="ATX"
                    )
                except Exception as e:
                    print(f"Markdown conversion error: {e}")
                    markdown_content = modified_html

                # Convert modified HTML to Markdown
                markdown_output = markdownify.markdownify(
                    markdown_content, heading_style="ATX"
                )

                # Create H1 heading with hyperlink to the original file
                docx_name = os.path.splitext(file)[0]
                h1_title = re.sub(r"[_-]+", " ", docx_name).strip().title()
                corrected_path = source_file.replace("\\", "/")
                h1_hyperlink = (
                    f'# [{h1_title}](file:///{corrected_path}){{target="_blank"}}\n\n'
                )

                # Save Markdown to destination file
                with open(destination_file, "w", encoding="utf-8") as md_file:
                    md_file.write(h1_hyperlink)
                    md_file.write(markdown_output)

                print(f"Converted {source_file} -> {destination_file}")

            except Exception as e:
                print(f"Error processing {source_file}: {e}")


def round_columns(df, columns, digits=2):
    """
    Rounds specified columns of a Pandas DataFrame to a given number of decimal places.

    Args:
        df: The Pandas DataFrame.
        columns: A list of column names to round.
        digits: The number of decimal places to round to.  Defaults to 2.

    Returns:
        A new Pandas DataFrame with the specified columns rounded, or the original
        DataFrame if no columns are provided or if the specified columns are not found.
        Prints a warning if some columns are not found.
    """

    if not columns:  # Handle empty column list
        return df

    df_copy = (
        df.copy()
    )  # Important: Create a copy to avoid modifying the original DataFrame

    not_found_cols = []
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].round(digits)
        else:
            not_found_cols.append(col)

    if not_found_cols:
        print(f"Warning: Columns not found: {', '.join(not_found_cols)}")

    return df_copy


def limit_text(max_length=50, border=None, prefix="", suffix=""):
    """
    Copies text from clipboard, splits it into fixed-length lines,
    adds prefix and suffix to each line if provided, pads each line
    to ensure it reaches max_length, copies the result back to clipboard,
    and prints it.

    Args:
        max_length (int, optional): Maximum length of each line. Defaults to 50.
        prefix (str, optional): Prefix to add to each line. Defaults to ''.
        suffix (str, optional): Suffix to add to each line. Defaults to ''.
    """

    # Get the text from clipboard
    text = pyperclip.paste()

    # Replace all occurrences of \r\n with \n
    text = text.replace("\r\n", "\n")

    # Split the text into paragraphs
    paragraphs = text.split("\n\n")

    # Initialize the result text
    result_text = ""

    # Calculate available width after adding prefix and suffix
    available_width = max_length - len(prefix) - len(suffix)

    # Process each paragraph
    for i, paragraph in enumerate(paragraphs):
        # Remove leading and trailing whitespace from the paragraph
        paragraph = paragraph.strip()

        # If the paragraph is not empty, wrap it into fixed-length lines
        if paragraph:
            wrapped_lines = textwrap.wrap(paragraph, width=available_width)

            # Add prefix, suffix, and pad each line to the exact max_length
            formatted_lines = [
                f"{prefix}{line.ljust(available_width)}{suffix}"
                for line in wrapped_lines
            ]

            # Join the formatted lines back into a paragraph
            formatted_paragraph = "\n".join(formatted_lines)

            # Add the formatted paragraph to the result text
            result_text += formatted_paragraph

            # Add an extra newline character between paragraphs
            if i < len(paragraphs) - 1:
                result_text += "\n\n"

    # Enclose with proper border
    if border:
        border = "#" + "-" * (max_length - 1)
        result_text = f"{border}\n{result_text}\n{border}"

        # Ensure UTF-8 encoding
        result_text = result_text.encode("utf-8").decode("utf-8")

        # Copy the result text back to clipboard
        pyperclip.copy(result_text)

        # Print the result text
        print(result_text)
    else:
        # Ensure UTF-8 encoding
        result_text = result_text.encode("utf-8").decode("utf-8")

        # Copy the result text back to clipboard
        pyperclip.copy(result_text)

        # Print the result text
        print(result_text)


if __name__ == "__main__":
    limit_text(max_length=50, prefix=">> ", suffix=" <<")


def spacing_tables_for_txt_files(*, _df=pd.DataFrame({})):
    global clip_df

    if pd.read_clipboard().shape[0] == 0:
        clip_dfx = _df.copy()
    else:
        clip_dfx = pd.read_clipboard()
        clip_dfx = clip_dfx.astype(str)

    # format all fields to string
    clip_dfx = clip_dfx.astype(str)

    clip_df = pd.DataFrame()
    for cl in clip_dfx.columns:
        # cl_len = clip_dfx[cl].str.len().max()
        if (len(cl) - clip_dfx[cl].str.len().max()) > 0:
            cl_len = len(cl)
        else:
            cl_len = clip_dfx[cl].str.len().max()
        cln = cl + " " * (cl_len - len(cl))
        for i in range(0, len(clip_dfx)):
            clip_df.loc[i, cln] = clip_dfx.loc[i, cl] + " " * (
                cl_len - len(clip_dfx.loc[i, cl])
            )

    clip_df.to_clipboard(index=False)


def spacing_tables_for_txt_filesx(*, _df=pd.DataFrame({}), sep_fixed_width=" ", sep=""):
    """
    Formats a DataFrame for fixed-width output to the clipboard.

    Args:
        _df (pd.DataFrame, optional): DataFrame to format. Defaults to an empty DataFrame.
        sep_fixed_width (str, optional): Separator to use between values with fixed-width spacing. Defaults to a space.
        sep (str, optional): Separator to use between values without fixed-width spacing. Defaults to an empty string.
    """

    global clip_df

    if pd.read_clipboard().shape[0] == 0:
        clip_dfx = _df.copy()
    else:
        clip_dfx = pd.read_clipboard()
        clip_dfx = clip_dfx.astype(str)

    # format all fields to string
    clip_dfx = clip_dfx.astype(str)

    if sep:
        # join values without fixed-width spacing
        output = []
        for index, row in clip_dfx.iterrows():
            output.append(sep.join(map(str, row)))

        # write the output to the clipboard
        pd.DataFrame(output, columns=["Output"]).to_clipboard(index=False)
    else:
        clip_df = pd.DataFrame()
        for cl in clip_dfx.columns:
            # cl_len = clip_dfx[cl].str.len().max()
            if (len(cl) - clip_dfx[cl].str.len().max()) > 0:
                cl_len = len(cl)
            else:
                cl_len = clip_dfx[cl].str.len().max()
            cln = cl + " " * (cl_len - len(cl))
            for i in range(0, len(clip_dfx)):
                clip_df.loc[i, cln] = clip_dfx.loc[i, cl] + " " * (
                    cl_len - len(clip_dfx.loc[i, cl])
                )

        # join values with fixed-width spacing
        output = []
        for index, row in clip_df.iterrows():
            output.append(sep_fixed_width.join(map(str, row)))

        # write the output to the clipboard
        pd.DataFrame(output, columns=["Output"]).to_clipboard(index=False)


def concatenate_column_values(delimiter=",", sort=False, case_transform=None):
    """
    Concatenate column values from clipboard with specified options.

    Parameters:
    - delimiter (str, optional): Delimiter between quoted values. Defaults to ','.
    - sort (bool, optional): Whether to sort the values. Defaults to False.
    - case_transform (str, optional): Transform case of values.
      Options: 'upper', 'lower', or None. Defaults to None.

    Returns and copies concatenated string of quoted values to clipboard
    """
    # Get data from clipboard
    try:
        clipboard_data = pyperclip.paste()
        print(f"REPORT: Length of copied string {len(clipboard_data)}.")
    except Exception:
        print(
            "Warning: Unable to read from clipboard. Please copy a column from Excel."
        )
        return

    # Split the clipboard data into lines and remove the header
    lines = clipboard_data.strip().split("\n")
    values = lines[1:]  # Skip the first line (header)

    # Optional sorting
    if sort:
        values.sort()

    # Optional case transformation
    if case_transform == "upper":
        values = [val.upper() for val in values]
    elif case_transform == "lower":
        values = [val.lower() for val in values]

    # Enclose each value in quotes
    quoted_values = [f"'{val.strip()}'" for val in values]

    # Concatenate with specified delimiter
    result = delimiter.join(quoted_values)

    # Copy result to clipboard
    pyperclip.copy(result)

    return result


if __name__ == "__main__":
    concatenate_column_values()  # Uses defaults
    concatenate_column_values(sort=True, case_transform="upper")


def limit_text_df(prefix="", suffix="", triple_quotes=False, df=None):
    """
    Formats a DataFrame with even spacing for each column, adds prefix and suffix to each row
    if provided, or encloses the entire output within triple quotes if specified.
    The DataFrame can be provided directly or read from clipboard.

    Args:
        prefix (str, optional): Prefix to add to each row. Defaults to ''.
        suffix (str, optional): Suffix to add to each row. Defaults to ''.
        triple_quotes (bool, optional): If True, encloses the output in triple quotes
                                        and ignores prefix/suffix. Defaults to False.
        df (pandas.DataFrame, optional): DataFrame to format. If None, reads from clipboard.
                                         Defaults to None.
    """
    # Get the DataFrame from parameter or clipboard
    if df is None:
        try:
            df = pd.read_clipboard()
        except Exception:
            print("No valid DataFrame found in clipboard.")
            return

    # Convert all columns to string type
    df = df.astype(str)

    # Create a new DataFrame to store formatted data
    formatted_df = pd.DataFrame()

    # Format each column with even spacing
    for col in df.columns:
        # Determine max length needed (either column name or longest value)
        col_len = max(len(col), df[col].str.len().max())

        # Create column name with padding
        padded_col = col + " " * (col_len - len(col))

        # Add padded values to the formatted DataFrame
        for i in range(len(df)):
            value = df.loc[i, col]
            formatted_df.loc[i, padded_col] = value + " " * (col_len - len(value))

    # Convert DataFrame to string with even spacing
    formatted_text = formatted_df.to_string(index=False)

    if triple_quotes:
        # Enclose in triple quotes, ignoring prefix and suffix
        result_text = f'"""\n{formatted_text}\n"""'
    else:
        # Apply prefix and suffix to each line
        lines = formatted_text.split("\n")
        result_text = "\n".join([f"{prefix}{line}{suffix}" for line in lines])

    # Copy the result text back to clipboard
    pyperclip.copy(result_text)

    # Print the result text
    print(result_text)
    return result_text


# %% convert_py_file_to__ipynb_html_md


def export_notebook(notebook_path, exporter_cls, extension, output_folder):
    """
    Export the notebook to the specified format and save it in the given output folder.
    """
    notebook_path = Path(notebook_path)
    with open(notebook_path, "r", encoding="utf-8") as file:
        notebook = nbformat.read(file, as_version=4)

    exporter = exporter_cls()
    output, _ = exporter.from_notebook_node(notebook)

    output_file_path = output_folder / notebook_path.with_suffix(extension).name
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(output)
    print(f"Exported to {output_file_path}")


def convert_py_file(
    py_file_path,
    output_format=[".ipynb"],
    run_ipynb=False,
    output_folder=None,
    md_output_folder=None,
    md_img_folder=None,
    file_prefix=None,
    file_suffix=None,
):
    """
    Convert a .py file to various formats with optional execution, destination folders, and filtering options.

    Parameters:
        py_file_path (str): Path to the .py file or directory containing .py files.
        output_format (list): List of formats to export (e.g., ['.ipynb', '.html', '.md']).
        run_ipynb (bool): Whether to execute the notebook before exporting.
        output_folder (str): Custom folder for all output files.
        md_output_folder (str): Custom folder for Markdown files and images.
        md_img_folder (str): Custom subfolder for Markdown images.
        file_prefix (str): Process only files starting with this prefix.
        file_suffix (str): If specified, disables notebook execution for files with this suffix.
    """
    if file_prefix:
        dir_path = (
            Path(py_file_path).parent
            if Path(py_file_path).is_file()
            else Path(py_file_path)
        )
        matching_files = list(dir_path.glob(f"{file_prefix}*.py"))

        if not matching_files:
            print(f"No files found with prefix '{file_prefix}' in {dir_path}")
            return

        for file_path in matching_files:
            print(f"\nProcessing {file_path.name}...")
            convert_py_file(
                file_path,
                output_format,
                run_ipynb,
                output_folder,
                md_output_folder,
                md_img_folder,
                file_prefix=None,
                file_suffix=file_suffix,
            )
        return

    py_file_path = Path(py_file_path)
    base_output_folder = output_folder or py_file_path.parent
    base_output_folder = Path(base_output_folder)
    base_output_folder.mkdir(parents=True, exist_ok=True)

    # Check if file_suffix matches
    if file_suffix and py_file_path.name.endswith(file_suffix):
        run_ipynb = False  # Disable execution for matching files
        print(
            f"Execution disabled for file: {py_file_path.name} (matches suffix '{file_suffix}')"
        )

    notebook_file_path = base_output_folder / py_file_path.with_suffix(".ipynb").name

    if not run_ipynb and notebook_file_path.exists():
        # If run_ipynb is False and notebook exists, use the existing notebook
        print(f"Using existing notebook: {notebook_file_path}")
        with open(notebook_file_path, "r", encoding="utf-8") as file:
            notebook = read(file, as_version=4)
    else:
        # Create new notebook from .py file
        with open(py_file_path, "r", encoding="utf-8") as f:
            code = f.read()

        notebook = new_notebook()
        blocks = code.split("\n# %% ")

        if blocks[0].strip().startswith("# %% "):
            blocks[0] = "##" + blocks[0][4:]

        for i, block in enumerate(blocks):
            parts = block.split("\n##")
            if i == 0 and parts[0].strip():
                notebook.cells.append(new_markdown_cell(parts[0].strip()))
            elif i > 0 and parts[0].strip():
                heading = parts[0].strip()
                notebook.cells.append(new_markdown_cell("## " + heading))
            for part in parts[1:]:
                markdown_heading = part.split("\n", 1)[0].strip()
                code_content = part.split("\n", 1)[1].strip() if "\n" in part else ""
                if markdown_heading:
                    notebook.cells.append(new_markdown_cell("### " + markdown_heading))
                if code_content:
                    notebook.cells.append(new_code_cell(code_content))

        # Write the notebook
        nbformat.write(notebook, notebook_file_path)

        # Execute if requested
        if run_ipynb:
            with open(notebook_file_path, "r", encoding="utf-8") as file:
                notebook = read(file, as_version=4)
            executed_notebook = execute(notebook, output_path=str(notebook_file_path))
            with open(notebook_file_path, "w", encoding="utf-8") as file:
                write(executed_notebook, file)
            notebook = executed_notebook

    try:
        # Convert to other formats
        for fmt in output_format:
            if fmt == ".html":
                export_notebook(
                    notebook_file_path, HTMLExporter, fmt, base_output_folder
                )
            elif fmt == ".md":
                export_notebook_with_images_and_clean_tables(
                    notebook_file_path,
                    fmt,
                    base_output_folder,
                    md_output_folder=md_output_folder,
                    md_img_folder=md_img_folder,
                )
    finally:
        # Clean up .ipynb file only if it's not in output_format AND we ran the notebook
        if ".ipynb" not in output_format and run_ipynb:
            notebook_file_path.unlink(missing_ok=True)

    # Open the generated file only if .ipynb was requested
    if ".ipynb" in output_format:
        sp.Popen(str(notebook_file_path), shell=True)


def export_notebook_with_images_and_clean_tables(
    notebook_path, extension, output_folder, md_output_folder=None, md_img_folder=None
):
    """
    Export the notebook to Markdown with optional custom output locations.

    Parameters:
    -----------
    notebook_path : str or Path
        Path to the notebook file
    extension : str
        File extension (e.g., '.md')
    output_folder : Path
        Default output folder
    md_output_folder : Path or str, optional
        Custom output folder for markdown files
    md_img_folder : Path or str, optional
        Custom folder for markdown images
    """
    with open(notebook_path, "r", encoding="utf-8") as file:
        notebook = nbformat.read(file, as_version=4)

    markdown_exporter = MarkdownExporter()
    markdown_exporter.output_files_dir = "img"
    markdown_exporter.files_writer = FilesWriter()

    output, resources = markdown_exporter.from_notebook_node(notebook)

    # Clean up HTML in the Markdown content
    output = clean_html_tables_and_styles(output)

    # Determine output locations
    final_md_folder = Path(md_output_folder) if md_output_folder else output_folder
    final_img_folder = Path(md_img_folder) if md_img_folder else final_md_folder / "img"

    # Create output directories
    final_md_folder.mkdir(parents=True, exist_ok=True)
    final_img_folder.mkdir(parents=True, exist_ok=True)

    # Save images
    for idx, (filename, content) in enumerate(
        resources.get("outputs", {}).items(), start=1
    ):
        img_file_path = (
            final_img_folder
            / f"{Path(notebook_path).stem}_{idx}{Path(filename).suffix}"
        )
        with open(img_file_path, "wb") as img_file:
            img_file.write(content)

    # Adjust image references in markdown
    rel_img_path = os.path.relpath(final_img_folder, final_md_folder)
    for idx, filename in enumerate(resources.get("outputs", {}).keys(), start=1):
        old_ref = filename
        new_ref = (
            f"{rel_img_path}/{Path(notebook_path).stem}_{idx}{Path(filename).suffix}"
        )
        output = output.replace(old_ref, new_ref)

    # Save the markdown file
    md_file_path = final_md_folder / Path(notebook_path).with_suffix(extension).name
    with open(md_file_path, "w", encoding="utf-8") as file:
        file.write(output)
    print(f"Exported to {md_file_path}")


def clean_html_tables_and_styles(md_content):
    """
    Remove <style> tags, clean up <table> elements (remove borders and classes).
    """
    soup = BeautifulSoup(md_content, "html.parser")
    # Remove <style> tags
    for style in soup.find_all("style"):
        style.decompose()
    # Remove 'border' attribute and 'class="dataframe"' from <table> tags
    for table in soup.find_all("table"):
        if "border" in table.attrs:
            del table.attrs["border"]
        if "class" in table.attrs and "dataframe" in table.attrs["class"]:
            table.attrs["class"].remove("dataframe")
            # Remove the 'class' attribute entirely if it's now empty
            if not table.attrs["class"]:
                del table.attrs["class"]
    return str(soup)


# %% convert_ipynb_to_py


def convert_ipynb_to_py(ipynb_file, *, file_open=None):
    with open(ipynb_file, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    exporter = PythonExporter()
    source, _ = exporter.from_notebook_node(nb)
    source_cleaned = re.sub(r"# In\[\d*\]:\n\n\n|# In\[\s*\]:\n\n\n", "", source)

    py_file = str(ipynb_file)[:-5] + "py"

    with open(py_file, "w", encoding="utf-8") as f:
        f.write(source_cleaned)

    if file_open:
        sp.Popen(py_file, shell=True)


# %% HTML to .md


def html_to_markdown(html_path, output_md_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    markdown = []

    # Convert headings
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        if heading:  # Ensure the heading exists
            level = int(heading.name[1])
            markdown.append(f"{'#' * level} {heading.get_text(strip=True)}")

    # Convert paragraphs
    for p in soup.find_all("p"):
        if p:
            markdown.append(p.get_text(strip=True))

    # Convert admonitions (example for "note" type)
    for admonition in soup.find_all(class_="admonition"):
        title_tag = admonition.find(class_="admonition-title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            content = admonition.get_text(strip=True).replace(title, "").strip()
            markdown.append(f"!!! {title.lower()}\n    {content}")

    # Convert links
    for a in soup.find_all("a", href=True):
        link_text = a.get_text(strip=True)
        href = a["href"]
        if link_text and href:
            markdown.append(f"[{link_text}]({href})")

    # Convert tables
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        rows = [
            [td.get_text(strip=True) for td in tr.find_all("td")]
            for tr in table.find_all("tr")
            if tr.find_all("td")
        ]
        if headers:
            markdown.append("| " + " | ".join(headers) + " |")
            markdown.append("|" + " --- |" * len(headers))
        for row in rows:
            markdown.append("| " + " | ".join(row) + " |")

    # Convert images
    for img in soup.find_all("img"):
        alt_text = img.get("alt", "Image")
        src = img.get("src", "")
        if src:
            markdown.append(f"![{alt_text}]({src})")

    # Convert code blocks
    for pre in soup.find_all("pre"):
        code = pre.get_text()
        if code:
            markdown.append(f"```\n{code}\n```")

    # Save to Markdown file
    with open(output_md_path, "w", encoding="utf-8") as md_file:
        md_file.write("\n\n".join(markdown))

    print(f"Markdown file saved to {output_md_path}")


if __name__ == "__main__":
    html_path = (
        r"C:/my_disk/edupunk/all_docs/site/settings/template/crisp_dm_template.html"
    )
    output_md_path = r"C:\Users\Ashut\Downloads\output.md"
    html_to_markdown(html_path, output_md_path)


# %% Color


def hex_to_rgb(hex_color):
    """
    Converts a hexadecimal color code to an RGB tuple.

    Args:
      hex_color: The hexadecimal color code (e.g., '#FF0000').

    Returns:
      A tuple containing the RGB values (red, green, blue), each in the range 0-255.
    """
    hex_color = hex_color.lstrip("#")  # Remove the leading '#' if present
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def create_rgb_column(df, hex_column_name):
    """
    Creates a new column in the given DataFrame containing RGB tuples
    from a column of hexadecimal color codes.

    Args:
      df: The pandas DataFrame.
      hex_column_name: The name of the column containing hexadecimal colors.

    Returns:
      The DataFrame with the new 'rgb_color' column.
    """
    df["RGB color"] = df[hex_column_name].apply(hex_to_rgb)
    return df


if __name__ == "__main__":
    data = {"hex_color": ["#FF0000", "#00FF00", "#0000FF"]}
    df = pd.DataFrame(data)

    df = create_rgb_column(df, "hex_color")
    print(df)
