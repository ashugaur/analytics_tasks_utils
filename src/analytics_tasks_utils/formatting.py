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


## round_columns
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


## limit_text
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


## spacing_tables_for_txt_files
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


## spacing_tables_for_txt_filesx
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


## concatenate_column_values
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


## limit_text_df
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

## convert_ipynb_to_py
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
