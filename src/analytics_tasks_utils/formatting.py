# %% Operating system

## Dependencies
import pyperclip
import textwrap
import pandas as pd
import re
from typing import List, Tuple, Optional, Union
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


## order_lines
def order_lines(sort=1):
    """
    Process the text from clipboard.

    Args:
        sort (int, optional): Sorting order. 1 for ascending, 0 for descending. Defaults to 1.

    Returns:
        str: Processed text.
    """

    # Get text from clipboard
    text = pyperclip.paste()

    # Split text into lines
    lines = text.split("\n")

    # Remove duplicates
    lines = list(set(lines))

    # Sort lines based on length
    if sort == 1:
        lines.sort(key=len)
    elif sort == 0:
        lines.sort(key=len, reverse=True)
    else:
        raise ValueError("Invalid sort order. Use 1 for ascending or 0 for descending.")

    # Join lines back into a string
    processed_text = "\n".join(lines)

    # Copy processed text back to clipboard
    pyperclip.copy(processed_text)

    # Print processed text
    print(processed_text)

    return processed_text


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


# %% sort_py
def sort_py(
    code: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    ascending: bool = True,
    exception: Optional[List[str]] = None,
) -> str:
    """
    Sort Python code blocks hierarchically while respecting exceptions.

    Args:
        code (Union[str, Path]): The Python code string to sort OR path to .py file
        output_file (Union[str, Path], optional): Output file path. If None and input is a file,
                                                overwrites the input file. If specified, saves to new file.
        ascending (bool): True for ascending order, False for descending
        exception (List[str], optional): List of block headers to exclude from sorting.
                                       Format: ["# %% Block Name", "## Sub-block Name"]

    Returns:
        str: Sorted code string (also writes to file if input was a file)
    """
    if exception is None:
        exception = []

    # Handle file input
    input_file_path = None
    if isinstance(code, (str, Path)) and (
        Path(code).exists() if isinstance(code, str) else code.exists()
    ):
        input_file_path = Path(code)
        try:
            with open(input_file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
        except Exception as e:
            raise ValueError(f"Error reading file {input_file_path}: {e}")
    else:
        # Assume it's a code string
        code_content = str(code)

    # Parse exception pairs
    exception_pairs = []
    for i in range(0, len(exception), 2):
        if i + 1 < len(exception):
            main_block = exception[i].strip()
            sub_block = exception[i + 1].strip()
            exception_pairs.append((main_block, sub_block))

    # Split code into lines
    lines = code_content.split("\n")

    # Find all main blocks (# %% or #%%)
    main_blocks = []
    current_block = None
    current_content = []

    for i, line in enumerate(lines):
        # Check if line is a main block header
        if re.match(r"^#\s*%%\s*", line.strip()):
            # Save previous block if exists
            if current_block is not None:
                main_blocks.append(
                    {
                        "header": current_block,
                        "content": current_content,
                        "original_index": len(main_blocks),
                    }
                )

            # Start new block
            current_block = line.strip()
            current_content = []
        else:
            # Add line to current block content
            if current_block is not None:
                current_content.append(line)
            else:
                # Lines before first block
                if not main_blocks:
                    main_blocks.append(
                        {"header": "", "content": [line], "original_index": 0}
                    )
                else:
                    main_blocks[0]["content"].insert(0, line)

    # Add the last block
    if current_block is not None:
        main_blocks.append(
            {
                "header": current_block,
                "content": current_content,
                "original_index": len(main_blocks),
            }
        )

    # Process each main block to sort its sub-blocks
    for block in main_blocks:
        if block["header"]:  # Skip empty header (pre-block content)
            block["content"] = sort_sub_blocks(
                block["content"], block["header"], exception_pairs, ascending
            )

    # Separate exception blocks from sortable blocks
    exception_blocks = []
    sortable_blocks = []

    for block in main_blocks:
        if block["header"]:
            is_exception = any(
                block["header"] == exc_pair[0] for exc_pair in exception_pairs
            )
            if is_exception:
                exception_blocks.append(block)
            else:
                sortable_blocks.append(block)
        else:
            # Pre-block content stays at the beginning
            exception_blocks.append(block)

    # Sort the sortable blocks
    if sortable_blocks:
        sortable_blocks.sort(key=lambda x: x["header"].lower(), reverse=not ascending)

    # Combine blocks: exceptions first (in original order), then sorted blocks
    final_blocks = []

    # Add exception blocks in their original positions relative to each other
    exception_blocks.sort(key=lambda x: x["original_index"])
    final_blocks.extend(exception_blocks)
    final_blocks.extend(sortable_blocks)

    # Reconstruct the code with proper spacing
    result_lines = []

    for i, block in enumerate(final_blocks):
        # Add spacing before main blocks (except the first one)
        if block["header"] and i > 0:
            # Add 3 blank lines before each main block
            result_lines.extend(["", "", ""])

        # Add the main block header
        if block["header"]:
            result_lines.append(block["header"])

        # Process block content with proper spacing for sub-blocks
        formatted_content = format_block_content(block["content"])
        result_lines.extend(formatted_content)

    sorted_code = "\n".join(result_lines)

    # Handle file output
    if input_file_path is not None:
        # Determine output file path
        if output_file is None:
            # Overwrite the input file
            output_path = input_file_path
        else:
            # Save to specified output file
            output_path = Path(output_file)

        # Write sorted code to file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(sorted_code)
            print(f"Sorted code written to: {output_path}")
        except Exception as e:
            print(f"Error writing to file {output_path}: {e}")

    return sorted_code


def is_inside_code_block(lines: List[str], target_index: int) -> bool:
    """
    Check if a line at target_index is inside a Python code block (function, class, etc.)
    by analyzing indentation levels and Python syntax.
    """
    if target_index >= len(lines):
        return False

    # Get the indentation of the target line
    target_line = lines[target_index]
    target_stripped = target_line.strip()

    # If the line is not indented or only has comment indentation, it's likely a true header
    if not target_line.startswith("    ") and not target_line.startswith("\t"):
        # Check if it's only indented for comment formatting (e.g., "    ## comment")
        if (
            target_stripped.startswith("##")
            and len(target_line) - len(target_line.lstrip()) <= 4
        ):
            return False

    # Look backwards to find the context
    for i in range(target_index - 1, -1, -1):
        line = lines[i].strip()

        # Skip empty lines and pure comments
        if not line or line.startswith("#"):
            continue

        # Check for function/class/method definitions
        if (
            line.startswith("def ")
            or line.startswith("class ")
            or line.startswith("async def ")
            or ":" in line
        ):
            # If we find a function/class definition, check if our target is indented relative to it
            definition_indent = len(lines[i]) - len(lines[i].lstrip())
            target_indent = len(lines[target_index]) - len(lines[target_index].lstrip())

            # If target is indented more than the definition, it's inside the code block
            if target_indent > definition_indent:
                return True

        # If we hit a line that's not indented and not a comment, we're likely at module level
        if len(lines[i]) - len(lines[i].lstrip()) == 0 and line:
            break

    # Additional check: look for patterns that suggest we're inside a function
    # Check if there are indented lines before this that suggest we're in a code block
    indent_levels = []
    for i in range(max(0, target_index - 10), target_index):
        line = lines[i]
        if line.strip() and not line.strip().startswith("#"):
            indent_level = len(line) - len(line.lstrip())
            indent_levels.append(indent_level)

    # If we have consistent indentation before this line, we're likely inside a code block
    if indent_levels:
        target_indent = len(lines[target_index]) - len(lines[target_index].lstrip())
        # If most recent non-comment lines are indented and our target is also indented
        recent_indented = [level for level in indent_levels[-5:] if level > 0]
        if len(recent_indented) >= 2 and target_indent > 0:
            return True

    return False


def format_block_content(content: List[str]) -> List[str]:
    """
    Format block content with proper spacing before sub-blocks (##).
    """
    if not content:
        return content

    formatted_content = []

    for i, line in enumerate(content):
        # Check if this line is a sub-block header (and not inside a code block)
        if re.match(r"^##\s*", line.strip()) and not is_inside_code_block(content, i):
            # Add 2 blank lines before sub-block (except if it's the first line)
            if i > 0 and formatted_content:
                # Check if we already have blank lines
                blank_lines_count = 0
                for j in range(len(formatted_content) - 1, -1, -1):
                    if formatted_content[j].strip() == "":
                        blank_lines_count += 1
                    else:
                        break

                # Add blank lines to make total of 2
                lines_to_add = max(0, 2 - blank_lines_count)
                formatted_content.extend([""] * lines_to_add)

        formatted_content.append(line)

    return formatted_content


def sort_sub_blocks(
    content: List[str],
    main_header: str,
    exception_pairs: List[Tuple[str, str]],
    ascending: bool,
) -> List[str]:
    """
    Sort sub-blocks (##) within a main block's content, ignoring ## comments inside code blocks.
    """
    if not content:
        return content

    # Find sub-blocks (only those not inside code blocks)
    sub_blocks = []
    current_sub_block = None
    current_sub_content = []
    pre_sub_content = []

    for i, line in enumerate(content):
        # Check if line is a sub-block header (and not inside a code block)
        if re.match(r"^##\s*", line.strip()) and not is_inside_code_block(content, i):
            # Save previous sub-block if exists
            if current_sub_block is not None:
                sub_blocks.append(
                    {
                        "header": current_sub_block,
                        "content": current_sub_content,
                        "original_index": len(sub_blocks),
                    }
                )
            elif not sub_blocks and current_sub_content:
                # Content before first sub-block
                pre_sub_content.extend(current_sub_content)

            # Start new sub-block
            current_sub_block = line.strip()
            current_sub_content = []
        else:
            # Add line to current sub-block content
            if current_sub_block is not None:
                current_sub_content.append(line)
            else:
                # Lines before first sub-block
                pre_sub_content.append(line)

    # Add the last sub-block
    if current_sub_block is not None:
        sub_blocks.append(
            {
                "header": current_sub_block,
                "content": current_sub_content,
                "original_index": len(sub_blocks),
            }
        )

    # If no sub-blocks found, return original content
    if not sub_blocks:
        return content

    # Separate exception sub-blocks from sortable ones
    exception_sub_blocks = []
    sortable_sub_blocks = []

    for sub_block in sub_blocks:
        is_exception = any(
            main_header == exc_pair[0] and sub_block["header"] == exc_pair[1]
            for exc_pair in exception_pairs
        )
        if is_exception:
            exception_sub_blocks.append(sub_block)
        else:
            sortable_sub_blocks.append(sub_block)

    # Sort the sortable sub-blocks
    if sortable_sub_blocks:
        sortable_sub_blocks.sort(
            key=lambda x: x["header"].lower(), reverse=not ascending
        )

    # Combine sub-blocks: exceptions first (in original order), then sorted ones
    final_sub_blocks = []
    exception_sub_blocks.sort(key=lambda x: x["original_index"])
    final_sub_blocks.extend(exception_sub_blocks)
    final_sub_blocks.extend(sortable_sub_blocks)

    # Reconstruct content
    result_content = pre_sub_content.copy()

    for sub_block in final_sub_blocks:
        result_content.append(sub_block["header"])
        result_content.extend(sub_block["content"])

    return result_content


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

