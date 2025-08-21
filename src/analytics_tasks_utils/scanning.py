# %% Export functions

## Dependencies
import pandas as pd
import numpy as np
import pathlib
from pathlib import Path
import os
import glob
import shutil
import ast
import os.path
from datetime import datetime
import subprocess
from os.path import isfile
import re


def combine_multiple_text_files_in_a_folder(folder_path):
    """
    Combines multiple text files from a folder into an Excel file.

    Args:
        folder_path (str): Path to the folder containing text files
    """

    now = datetime.now()
    file_dt = (
        "{:02d}".format(now.year)
        + "{:02d}".format(now.month)
        + "{:02d}".format(now.day)
        + "_"
        + "{:02d}".format(now.hour)
        + "{:02d}".format(now.minute)
    )

    # Scan folder for files
    scan = []
    with os.scandir(folder_path) as it:
        for entry in it:
            if entry.is_file():
                filepath = entry.path  # absolute path
                scan.append(filepath)

    if not scan:
        print("No files found in the specified folder.")
        return

    scan = pd.DataFrame(scan).rename(columns={0: "unc"})

    # Get filename
    scan["filename"] = scan["unc"].apply(lambda row: Path(row).name)

    # Get extension
    scan["ext"] = scan["unc"].apply(
        lambda row: os.path.splitext(os.path.basename(row))[1]
    )

    # Filter for specific file types
    scan = scan[
        scan["ext"].isin([".R", ".sas", ".bat", ".sql", ".py", ".md", ".txt", ""])
    ]

    if scan.empty:
        print("No files with supported extensions found.")
        return

    # Import & clean text files
    lines_ = {}
    scanl = len(scan)

    print(f"Processing {scanl} files...")

    # Process files with simple progress tracking
    for i, (unc, filename, ext) in enumerate(scan.itertuples(index=False), 1):
        print(f"\n{i} of {scanl}")
        print("READING: " + unc)

        if os.path.exists(unc):
            try:
                # Try UTF-8 first
                with open(unc, encoding="utf-8", errors="ignore") as f:
                    listx = f.readlines()
            except UnicodeDecodeError:
                try:
                    print("Error reading file with UTF-8, trying UTF-16")
                    with open(unc, encoding="utf-16", errors="ignore") as f:
                        listx = f.readlines()  # Fixed typo: was "readliness()"
                except Exception as e:
                    print(f"Error reading file {unc}: {e}")
                    continue
            except Exception as e:
                print(f"Error reading file {unc}: {e}")
                continue

            lines_[unc] = listx
        else:
            print(f"File does not exist: {unc}")
            continue

    if not lines_:
        print("No files were successfully read.")
        return

    # Convert dictionary of lists to dataframe
    lines = []
    for k, v in lines_.items():
        if k != "":
            # Add header row for each file
            lines.append([k, None])  # File header
            for i, val in enumerate(v, 1):
                lines.append([k, val])
        else:
            continue

    # Convert to dataframe
    lines = pd.DataFrame(lines, columns=["unc", "lines"])

    # Clean newlines
    lines["lines"] = lines["lines"].astype(str).str.replace("\n", "", regex=True)

    lines = lines.reset_index().rename(columns={"index": "sn_"})
    lines["sn"] = lines.groupby("unc")["sn_"].rank("first", ascending=True)
    lines["filename"] = lines["unc"].apply(lambda row: Path(row).name)  # filename
    lines["ext"] = lines["unc"].apply(
        lambda row: os.path.splitext(os.path.basename(row))[1]
    )  # extension
    lines = lines[["unc", "filename", "ext", "sn", "lines"]]

    # Export to Excel
    xlf = "combined_txt_files" + "_" + file_dt + ".xlsx"  # export file name
    xlf_open = "explorer " + '"' + xlf + '"'

    try:
        writer = pd.ExcelWriter(xlf, engine="xlsxwriter")

        workbook = writer.book
        worksheet = workbook.add_worksheet("readme")  # new sheet

        worksheet.set_zoom(90)
        worksheet.set_column("A:A", 7)
        worksheet.set_column("B:B", 50)

        worksheet.write(0, 0, "Tab")  # (row, column)
        worksheet.write(0, 1, "Comments")
        worksheet.write(1, 0, "lines")
        worksheet.write(1, 1, "Table of all lines imported by filename")

        # Write main data
        lines.to_excel(writer, "lines", index=False, freeze_panes=(1, 0))
        workbook = writer.book
        worksheet = writer.sheets["lines"]
        worksheet.set_zoom(90)
        worksheet.set_column("A:A", 10)
        worksheet.set_column("B:B", 28)
        worksheet.set_column("C:C", 10)
        worksheet.set_column("D:D", 7)
        worksheet.set_column("E:E", 100)
        worksheet.autofilter("A1:E1")

        writer.close()  # Use close() instead of _save()

        print(f"Successfully created: {xlf}")

        # Try to open the file (Windows specific)
        try:
            subprocess.Popen(xlf_open, shell=True)
        except Exception as e:
            print(f"Could not auto-open file: {e}")
            print(f"Please manually open: {xlf}")

    except Exception as e:
        print(f"Error creating Excel file: {e}")


def scan_dir_to_markdown(_source, _destination):
    """
    Parse a folder containing files and convert them to markdown documents.

    Parameters:
    _source (str): Source directory path
    _destination (str): Destination directory path for markdown output
    """
    global scan, scan_md

    os.chdir(_destination)

    _relevant_file_type = [".R", ".bat", ".txt", ".sql", ".Rmd", ".py", ".ps1"]

    # remove folder
    os.system('rmdir /S /Q "{}"'.format(_destination / str(_source).split("\\")[-1]))

    # create folder
    pathlib.Path(str(_source).split("/")[-1]).mkdir(parents=True, exist_ok=True)

    # scan folder
    def scan_dir(location_to_scan):
        global scan
        scan = []
        for i in glob.iglob(rf"{location_to_scan}\**\*", recursive=True):
            scan.append(i)
        if len(scan) > 0:
            scan = pd.DataFrame(scan).rename(columns={0: "unc"})
            scan["filename"] = scan["unc"].apply(lambda row: Path(row).name)
            scan["ext"] = scan["unc"].apply(
                lambda row: os.path.splitext(os.path.basename(row))[1]
            )
        else:
            scan = pd.DataFrame({"filename": ""}, index=([0]))

    scan_dir(_source)

    # Filter rows with extensions .ipynb and .py
    relevant_files = scan[scan["ext"].isin([".ipynb", ".py"])].copy()

    # Extract the base filenames (without extensions)
    relevant_files["base_filename"] = relevant_files["filename"].str.replace(
        r"\.ipynb|\.py", "", regex=True
    )

    # Identify base filenames that have both .ipynb and .py extensions
    duplicate_bases = (
        relevant_files.groupby("base_filename")["ext"]
        .apply(lambda x: set(x))
        .reset_index()
    )

    # Filter for base filenames with both .ipynb and .py extensions
    duplicate_bases = duplicate_bases[
        duplicate_bases["ext"].apply(lambda x: {".ipynb", ".py"}.issubset(x))
    ]["base_filename"]
    print(
        f"REPORT: Count of duplicate .py and .ipynb files ignored...{len(duplicate_bases)}"
    )

    # Remove .py files for these duplicate base filenames
    scan = scan[
        ~(
            (scan["ext"] == ".py")
            & (
                scan["filename"]
                .str.replace(r"\.py", "", regex=True)
                .isin(duplicate_bases)
            )
        )
    ]
    scan = scan.reset_index(drop=True)

    # flag files and folders
    scan["dir_flag"] = False
    scan["file_flag"] = False

    for i in range(0, len(scan)):
        _unc = scan.loc[i, "unc"]
        if os.path.exists(_unc):
            scan.loc[i, "dir_flag"] = os.path.isdir(_unc)
            scan.loc[i, "file_flag"] = os.path.isfile(_unc)

    # dir depth
    scan["unc"] = scan["unc"].str.replace("\\", "/")
    scan["depth"] = scan["unc"].str.count("/") - str(_source).count("\\") - 1

    # Extract folder structure information
    scan["folder_path"] = scan["unc"].str.rsplit("/", expand=True, n=1)[0]

    # Create a dictionary to track which folders have files and which have subfolders
    folder_contains = {}

    # Initialize with empty sets
    for folder in scan["folder_path"].unique():
        folder_contains[folder] = {"files": False, "folders": False}

    # Mark folders that contain direct files
    for i, row in scan[scan["file_flag"]].iterrows():
        folder_contains[row["folder_path"]]["files"] = True

    # Mark folders that contain subfolders
    for folder in folder_contains:
        parent_folders = [
            p
            for p in folder_contains.keys()
            if folder.startswith(p + "/") and p != folder
        ]
        for parent in parent_folders:
            folder_contains[parent]["folders"] = True

    # Find folders that have both files and subfolders
    mixed_folders = [
        folder
        for folder, content in folder_contains.items()
        if content["files"] and content["folders"]
    ]

    print(f"REPORT: Folders with both files and subfolders: {len(mixed_folders)}")

    # Flag files that should be converted to index.md
    scan["in_mixed_folder"] = scan["folder_path"].isin(mixed_folders)

    # Create a helper column to indicate if a file is in a mixed folder
    scan["make_index"] = scan["in_mixed_folder"] & scan["file_flag"]

    # Calculate destination markdown path
    scan["_unc_md"] = np.where(
        scan["make_index"],  # Files in mixed folders become index.md
        scan["folder_path"].str.replace(
            "/".join(str(_source).split("\\")[:-1]),
            str(_destination).replace("\\", "/"),
        )
        + "/index.md",
        np.where(
            (scan["depth"] == 2),  # Top-level files become index.md
            scan["unc"]
            .str.rsplit("/", expand=True, n=1)[0]
            .str.replace(
                "/".join(str(_source).split("\\")[:-1]),
                str(_destination).replace("\\", "/"),
            )
            + "/index.md",
            # Other files get their own markdown
            scan["unc"]
            .str.rsplit("/", expand=True, n=1)[0]
            .str.replace(
                "/".join(str(_source).split("\\")[:-1]),
                str(_destination).replace("\\", "/"),
            )
            + ".md",
        ),
    )

    scan["unc_l1"] = np.where(
        (scan["depth"] == 2),
        scan["unc"]
        .str.rsplit("/", expand=True, n=1)[0]
        .str.replace(
            "/".join(str(_source).split("\\")[:-1]),
            str(_destination).replace("\\", "/"),
        ),
        scan["unc"]
        .str.rsplit("/", expand=True, n=2)[0]
        .str.replace(
            "/".join(str(_source).split("\\")[:-1]),
            str(_destination).replace("\\", "/"),
        ),
    )

    scan["_unc_img"] = scan["unc"].str.replace(
        "/".join(str(_source).split("\\")[:-1]), str(_destination).replace("\\", "/")
    )

    # Create all necessary directories first
    all_dirs = set()

    # Add all folder paths that need to be created
    for md_path in scan["_unc_md"].unique():
        dir_path = os.path.dirname(md_path)
        all_dirs.add(dir_path)

    # Create directories
    for dir_path in all_dirs:
        os.makedirs(dir_path, exist_ok=True)

    # copy markdowns
    scan_md = scan[scan["ext"] == ".md"]
    scan_md = scan_md[
        ~scan_md["unc"].str.contains("projects", case=False, na=False, regex=True)
    ].reset_index(drop=True)

    # copy .ipynb
    scan_ipynb = scan[scan["ext"] == ".ipynb"]

    # identify image folders
    scan_img = scan[
        (scan["dir_flag"]) & (scan["unc"].str.rsplit("/", expand=True, n=1)[1] == "img")
    ].reset_index(drop=True)

    # exceptions
    scan = scan[
        ~scan["unc"].str.contains("visual_library", case=False, na=False, regex=True)
    ].reset_index(drop=True)
    scan = scan[
        ~scan["unc"].str.contains(
            "edupunk_open_internet", case=False, na=False, regex=True
        )
    ]
    scan = scan[~scan["unc"].str.contains("projects", case=False, na=False, regex=True)]
    scan = scan[~scan["unc"].str.contains("python", case=False, na=False, regex=True)]

    # filter relevant unc
    scan = scan[scan["file_flag"]]
    scan = scan[scan["ext"].isin(_relevant_file_type)].reset_index(drop=True)

    # write markdown
    select = (
        scan[["unc", "_unc_md", "filename", "ext"]]
        .sort_values(["_unc_md", "filename"])
        .reset_index(drop=True)
    )
    select["_filename"] = select["filename"].str.rsplit(".", expand=True, n=1)[0]

    for _topic in select["_unc_md"].unique().tolist():
        _td = select[select["_unc_md"] == _topic].reset_index(drop=True)
        _file = _td["_unc_md"].unique()[0]
        _filemd = os.path.basename(_file).rsplit(".")[0]

        # Get the directory name (for index files)
        _dir_path = os.path.dirname(_file)

        # Ensure directory exists before writing to file
        os.makedirs(_dir_path, exist_ok=True)

        _filemd1 = os.path.basename(_dir_path)

        with open(_file, "w", encoding="utf-8") as f:
            if "index" == _filemd:
                f.write("# " + _filemd1.lower() + "\n\n")
            else:
                f.write("# " + _filemd.lower() + "\n\n")

            for unc, _unc_md, filename, ext, _filename in _td.itertuples(index=False):
                _ext = ext.split(".")[1]

                if "automated_function_scan" in unc.lower():
                    filename_mdx = str(
                        filename.split("__")[1] if "__" in filename else filename
                    )
                    f.write("??? " + "null" + ' "' + filename_mdx + '"\n\n')
                    f.write("\t```" + ext + ' linenums="1"' + "\n")
                else:
                    # Handle file names that don't have '__' in them
                    if "__" in filename:
                        filename_mdx = str(filename.split("__")[0])
                    else:
                        filename_mdx = filename
                    f.write("??? " + "null" + ' "' + filename_mdx + '"\n\n')
                    f.write("\t```" + ext + ' linenums="1"' + "\n")

                _sql_str = ""
                try:
                    with open(unc, "r", encoding="utf-8", errors="replace") as j:
                        content = j.readlines()
                        for _sql_substrx in content:
                            _sql_str = _sql_str + "\t" + _sql_substrx
                except Exception as e:
                    print(f"Error reading file {unc}: {e}")
                    _sql_str = f"\tError reading file: {e}"

                f.write(_sql_str + "\n")
                f.write("\t```" + "\n\n")

    # copy .md files as is
    scan_md = scan_md.reset_index(drop=True)
    scan_md["copy_md"] = (
        (scan_md["unc"].str.rsplit("/", expand=True, n=1)[0]).str.replace(
            "/".join(str(_source).split("\\")[:-1]),
            str(_destination).replace("\\", "/"),
        )
        + "/"
        + scan_md["filename"]
    )

    for i in range(0, len(scan_md)):
        __source = scan_md.loc[i, "unc"]
        __destination = scan_md.loc[i, "copy_md"]

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(__destination), exist_ok=True)

        try:
            shutil.copy(__source, __destination)
        except Exception as e:
            print(f"Error copying markdown file {__source} to {__destination}: {e}")

    # copy img folder as is
    for i in range(0, len(scan_img)):
        __source = scan_img.loc[i, "unc"]
        __destination = scan_img.loc[i, "_unc_img"]
        try:
            backup_folder_force_md(__source, __destination)
        except Exception as e:
            print(f"Error copying folder {__source} to {__destination}: {e}")


def backup_folder_force_md(source_folder, destination_folder):
    """Copy contents of source folder to destination folder"""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for item in os.listdir(source_folder):
        s = os.path.join(source_folder, item)
        d = os.path.join(destination_folder, item)
        if os.path.isdir(s):
            backup_folder_force_md(s, d)
        else:
            shutil.copy2(s, d)


# %% scan_python_functions_from_file_s
# objective: parse functions from all .py files from folders
# source: https://stackoverflow.com/questions/58935006/iterate-over-directory-and-get-function-names-from-found-py-files, chatgpt (openai)


def find_methods_in_python_file(file_path):
    """finds functions with python files"""

    methods = []
    o = open(file_path, "r", encoding="utf-8")
    text = o.read()
    # p = ast.parse(repr(text))
    p = ast.parse(text)
    for node in ast.walk(p):
        if isinstance(node, ast.FunctionDef):
            methods.append(node.name)
    return methods


def scan_python_functions_from_file_s(
    _source, _destination, _load_functions, _write_to_mkdocs
):
    """function to load functions from python files in folders to memory"""

    global scan

    _relevant_file_type = [".py"]

    if _write_to_mkdocs == 1:
        os.chdir(_destination.replace("\\", "/"))

        # remove folder
        os.chdir("\\".join(_destination.split("\\")[:-1]))
        shutil.rmtree(_destination.split("\\")[-1])

        # create folder
        pathlib.Path(_destination.split("\\")[-1]).mkdir(parents=True, exist_ok=True)
        os.chdir(_destination)
        # print('NOTE: functions written to documents site.')
    # else:
    # print('NOTE: functions not written to documents site.')

    # scan folder
    def scan_dir(location_to_scan):
        global scan
        scan = []
        for i in glob.iglob(rf"{location_to_scan}\**\*", recursive=True):
            scan.append(i)
        if len(scan) > 0:
            scan = pd.DataFrame(scan).rename(columns={0: "unc"})
            scan["filename"] = scan["unc"].apply(lambda row: Path(row).name)
            scan["ext"] = scan["unc"].apply(
                lambda row: os.path.splitext(os.path.basename(row))[1]
            )
        else:
            scan = pd.DataFrame({"filename": ""}, index=([0]))

    scan_dir(_source)

    # flag files and folders
    for i in range(0, len(scan)):
        _unc = scan.loc[i, "unc"]
        scan.loc[i, "dir_flag"] = None
        scan.loc[i, "file_flag"] = None
        if os.path.exists(_unc):
            if os.path.isdir(_unc):
                scan.loc[i, "dir_flag"] = os.path.isdir(_unc)
            else:
                scan.loc[i, "dir_flag"] = False
            if os.path.isfile(_unc):
                scan.loc[i, "file_flag"] = os.path.isfile(_unc)
            else:
                scan.loc[i, "file_flag"] = False

    # filter relevant unc
    scan = scan[scan["file_flag"]]
    scan = scan[scan["ext"].isin(_relevant_file_type)]

    # scan['relevant'] = np.where(scan['ext'].isin(_relevant_file_type), 1, 0)

    # exceptions
    scan = scan[~scan["filename"].isin(["edupunk.py"])]
    # scan = scan[~scan['filename'].str.contains('functions', case=False, regex=True, na=False)]

    # dir depth
    scan["unc"] = scan["unc"].str.replace("\\", "/")
    scan["depth"] = scan["unc"].str.count("/") - _source.count("\\") - 1
    scan["unc_l1"] = (scan["unc"].str.rsplit("/", expand=True, n=2)[0]).str.replace(
        "/".join(_source.split("\\")[:-1]), _destination.replace("\\", "/")
    )
    scan["_unc_md"] = (
        (scan["unc"].str.rsplit("/", expand=True, n=1)[0]).str.replace(
            "/".join(_source.split("\\")[:-1]), _destination.replace("\\", "/")
        )
        + ".md"
    )

    # create folder structure
    # for i in scan[scan['depth']>1]['unc_l1'].drop_duplicates():
    # print(i)
    # pathlib.Path(i).mkdir(parents=True, exist_ok=True)

    # write markdown
    select = scan[["unc", "_unc_md", "filename", "ext"]].sort_values(
        ["_unc_md", "filename"]
    )
    select["_filename"] = select["filename"].str.rsplit(".", expand=True, n=1)[0]

    # loop through files
    # _function_count = 0
    for unc in select["unc"].unique().tolist():
        # print('reading...: '+unc)
        function_code = ""

        try:
            # read the contents of the file
            with open(unc, "r", encoding="utf-8") as f:
                file_contents = f.read()

            # parse the file contents into an AST
            # parsed_file = ast.parse(repr(file_contents))
            parsed_file = ast.parse(file_contents)
            methods = find_methods_in_python_file(unc)

            for _function in methods:
                # find the function definition node in the AST
                function_node = next(
                    (
                        node
                        for node in parsed_file.body
                        if isinstance(node, ast.FunctionDef) and node.name == _function
                    ),
                    None,
                )

                # extract the code of the function
                if function_node is not None:
                    function_code = ast.unparse(function_node)
                    # print(function_code)
                else:
                    # print(f"function '{_function}' not found in file '{unc}'")
                    # print('warning... skipping:', unc)
                    continue

                if _write_to_mkdocs == 1:
                    _file = (
                        _function + "__" + str((unc.split("/")[-1]).lower())
                    )  # +'.py'
                    with open(_file, "w", encoding="utf-8") as f:
                        f.write("# " + unc + "\n\n" + function_code)
                        # print('REPORT: written function to disk from: '+unc)

                if 1 == _load_functions:
                    # _function_count += 1
                    exec(function_code, globals())

        except Exception:
            continue
            # print('warning: not able to scan', unc)

    # print('REPORT: # of times functions loaded to memory: '+str(_function_count))


def convert_excel_notes_by_discipline_to_markdown(_source, _destination):
    _filler = "uncat"
    # os.chdir(_destination.replace('\\', '/'))

    # remove folder
    os.chdir("\\".join(str(_destination).split("\\")[:-1]))
    shutil.rmtree(str(_destination).split("\\")[-1])

    # create folder
    pathlib.Path(str(_destination).split("\\")[-1]).mkdir(parents=True, exist_ok=True)
    os.chdir(_destination)

    _notes = pd.read_excel(_source, sheet_name="notes")
    _notes = _notes.fillna(".")

    _fields = ["category", "discipline", "on", "by", "source", "rank"]
    for i in range(0, len(_notes)):
        for _field in _fields:
            if _notes.loc[i, _field] == ".":
                _notes.loc[i, _field] = _filler

    _notes["discipline"] = _notes["discipline"].str.capitalize()
    _notes["on"] = _notes["on"].str.lower()

    for _dir in _notes["discipline"].unique().tolist():
        __dir = _dir.lower()
        pathlib.Path(__dir).mkdir(parents=True, exist_ok=True)
        _notesd = (
            _notes[_notes["discipline"] == _dir]
            .sort_values(["on"])
            .reset_index(drop=True)
        )

        for _c in _notesd["category"].unique().tolist():
            __c = _c.lower()
            _notesc = (
                _notesd[_notesd["category"] == _c]
                .sort_values(["on"])
                .reset_index(drop=True)
            )

            _reference_file_out = str(__c).replace(" ", "_")
            _d_heading = _c.lower().capitalize()
            if _reference_file_out.lower().strip() == _filler.lower().strip():
                file_out = __dir + "/index.md"
                # _d_heading = __dir.lower().capitalize()
                _d_heading = __dir.lower()
            else:
                file_out = __dir + "/" + _reference_file_out + ".md"

            with open(file_out, "w", encoding="utf-8") as f:
                # f.write('---\n# title: ' + _d_heading + '\nhide:' + '\n\t# - navigation' + '\n\t# - toc' + '\n\t# - footer' + '\n---\n\n')
                f.write("# " + _d_heading + "\n\n")

                for _on in _notesc["on"].drop_duplicates().sort_values().tolist():
                    _noteson = (
                        _notesc[_notesc["on"] == _on]
                        .sort_values(["on"])
                        .reset_index(drop=True)
                    )
                    # _t_heading = _on.lower().capitalize()
                    _t_heading = _on.lower()
                    f.write("<hr>\n\n### " + _t_heading + "\n\n")
                    # f.write('!!! ' + 'text' + ' ""\n\n')

                    for _n in _noteson["note"].drop_duplicates().sort_values().tolist():
                        _notesn = (
                            _noteson[_noteson["note"] == _n]
                            .sort_values(["on"])
                            .reset_index(drop=True)
                        )
                        _n = str(_n).replace("\n", "<br>")

                        _reference_by = str(_notesn["by"][0]).replace("\n", "<br>")
                        if _reference_by.lower().strip() == _filler.lower().strip():
                            _n_by = ""
                        else:
                            _n_by = "`" + _reference_by + "`"

                        _reference_source = str(_notesn["source"][0]).replace(
                            "\n", "<br>"
                        )
                        if _reference_source.lower().strip() == _filler.lower().strip():
                            _n_source = ""
                        else:
                            _n_source = "\t`" + _reference_source + "`"
                        # _n_rank = '\t&nbsp; `Rank: ' + str(_notesn['rank'][0]).replace('\n', '<br>')+'`'
                        # _nn = '\t' + str(_notesn['note'][0]).replace('\n', '<br>')
                        f.write(_n + "<br>\n")
                        # f.write('\t'+ _n_by + _n_source + _n_rank+ '\n\n')
                        f.write(_n_by + _n_source + "\n\n")
                        # f.write('\t??? null' + ' ""\n\n')
                        # f.write(_nn + '\n\n\n')


def convert_excel_q_n_a_to_markdown(_source, _destination):
    os.chdir(_destination)

    q = pd.read_excel(_source, sheet_name="q_n_a")
    q = q[~q["discipline"].isin(["sas"])].reset_index(drop=True)
    q["topic"] = q["topic"].str.capitalize()

    d_list = q["discipline"].unique().tolist()
    for _d in d_list:
        _qd = q[q["discipline"] == _d].reset_index(drop=True)
        file_out = str(_d).replace(" ", "_") + ".md"
        # _d_heading = _d.lower().capitalize()
        _d_heading = _d.lower()

        with open(file_out, "w", encoding="utf-8") as f:
            # f.write('---\n# title: ' + _d_heading + '\nhide:' + '\n\t# - navigation' + '\n\t# - toc' + '\n\t# - footer' + '\n---\n\n')
            f.write("# " + _d_heading + "\n\n")

            t_list = _qd["topic"].drop_duplicates().sort_values().tolist()
            for _t in t_list:
                _qt = _qd[_qd["topic"] == _t].reset_index(drop=True)
                # _t_heading = _t.lower().capitalize()
                _t_heading = _t.lower()
                f.write(
                    '<br>\n\n<hr style="height:1px;border-width:100%;color:gray;background-color:#045a8d">\n\n## '
                    + _t_heading
                    + "\n\n"
                )

                on_list = _qt["on"].drop_duplicates().sort_values().tolist()
                on_list_len = len(on_list)
                on_list_r = 0
                for _h in on_list:
                    on_list_r += 1
                    on_list_diff = on_list_len - on_list_r
                    _qh = _qt[_qt["on"] == _h].reset_index(drop=True)
                    # _h_heading = _h.lower().capitalize()
                    _h_heading = _h.lower()
                    if on_list_r == 1:
                        f.write("\n\n\n\n### " + _h_heading + "\n\n")
                    else:
                        f.write("\n\n<hr>\n\n### " + _h_heading + "\n\n")

                    q_list = _qh["question"].drop_duplicates().sort_values().tolist()
                    q_len = len(q_list)
                    q_r = 0
                    for _q in q_list:
                        q_r += 1
                        _qq = _qh[_qh["question"] == _q].reset_index(drop=True)
                        _q = str(_q).replace("\n", "<br>")
                        q_diff = q_len - q_r
                        # print('q_diff: ', q_diff, _q)
                        if q_diff == 0:
                            _qn = (
                                "\t: "
                                + str(_qq["notes"][0]).replace("\n", "<br>")
                                + "\n\n"
                            )
                            f.write("??? " + "null" + ' "' + _q + '"\n\n')
                            f.write(_qn + "\n\n\n\n")
                        else:
                            _qn = (
                                "\t: "
                                + str(_qq["notes"][0]).replace("\n", "<br>")
                                + "\n\n<hr>"
                            )
                            f.write("??? " + "null" + ' "' + _q + '"\n\n')
                            f.write(_qn + "\n\n\n\n")


def scan_dir(location_to_scan, ext=None):
    scan = []
    if ext:
        for i in glob.iglob(
            rf"{location_to_scan}\**\*{ext}".format(ext=ext), recursive=True
        ):
            scan.append(i)
    else:
        for i in glob.iglob(rf"{location_to_scan}\**\*.*", recursive=True):
            scan.append(i)

    if len(scan) > 0:
        scan = pd.DataFrame(scan).rename(columns={0: "unc"})
        scan["filename"] = scan["unc"].apply(lambda row: Path(row).name)
        scan["ext"] = scan["unc"].apply(
            lambda row: os.path.splitext(os.path.basename(row))[1]
        )
        scan["chart_hash"] = scan.filename.str.rsplit(".", expand=True, n=1)[0]
    else:
        scan = pd.DataFrame({"filename": ""}, index=[0])

    return scan


if __name__ == "__main__":
    # Scan for all files with .txt extension
    scan_txt = scan_dir("C:\\path\\to\\scan", ext=".txt")

    # Scan for all files with any extension
    scan_all = scan_dir("C:\\path\\to\\scan")



def scan_py_files_for_headings(unc):
    """function to extract comments from python a file and export as .md to create markmap"""

    # Read the file and process lines
    lines = []
    flags = []
    extracts = []

    pattern0 = re.compile(r"^# ")
    pattern1 = re.compile(r"^# %% ")
    pattern2 = re.compile(r"^###### ")
    pattern3 = re.compile(r"^##### ")
    pattern4 = re.compile(r"^#### ")
    pattern5 = re.compile(r"^### ")
    pattern6 = re.compile(r"^## ")
    pattern7 = re.compile(r"^#([^ ]+)")

    with open(unc, "r") as file:
        for line in file:
            ## exceptions
            line = line.replace(r"some abcd pattern", "a new pattern")
            line = line.strip()
            lines.append(line.strip())
            if pattern1.match(line):
                flags.append(1)
                extracts.append(pattern1.sub("", line).strip())
            elif pattern2.match(line):
                flags.append(2)
                extracts.append(pattern2.sub("", line).strip())
            elif pattern3.match(line):
                flags.append(3)
                extracts.append(pattern3.sub("", line).strip())
            elif pattern4.match(line):
                flags.append(4)
                extracts.append(pattern4.sub("", line).strip())
            elif pattern5.match(line):
                flags.append(5)
                extracts.append(pattern5.sub("", line).strip())
            elif pattern6.match(line):
                flags.append(6)
                extracts.append(pattern6.sub("", line).strip())
            elif pattern7.match(line):
                flags.append(7)
                extracts.append(pattern7.sub(r"\1", line).strip())
            elif pattern0.match(line):
                flags.append(-1)
                extracts.append(pattern0.sub("", line).strip())
            else:
                flags.append(0)
                extracts.append(line.strip())

    # Create a DataFrame
    df = pd.DataFrame({"line": lines, "flag": flags, "extract": extracts})

    # Create markdown
    df["hierarchy"] = np.where(
        (df["flag"].between(1, 6)), df["flag"].apply(lambda x: "#" * x), np.nan
    )
    df["hierarchy"] = np.where((df["flag"] == -1), "-", df["hierarchy"])
    df["md"] = np.where(
        (df["hierarchy"].isnull()), "", df["hierarchy"] + " " + df["extract"]
    )

    markdown_string = ""
    for i in df["md"]:
        if i != "":
            markdown_string = markdown_string + "\n" + i

    # Extract file name
    out_file, _ = os.path.splitext(os.path.basename(unc))
    out_file = out_file + ".md"

    # Export the string to a text file
    with open(out_file, "w") as file:
        file.write(markdown_string)

    # Open the text file using the default text editor without blocking
    subprocess.Popen(out_file, shell=True)



def scan_py_files_in_folders_for_headings(unc, md_name='Project report', heading_order=0, start_heading=1):

    """ function to extract directory tree and python file headings to be human readable
        heading_order = 1: ascending i.e. markdown default heading hierarchy
        heading_order = 0: descending
        start_heading = 1: the starting heading level for the top folder
        md_name = 'Project report': the first line in the .md output
    """

    ## scan folder
    def list_folder_structure(folder_path, unc):
        result = []

        for root, dirs, files in os.walk(folder_path):
            # Calculate the indentation level based on the relative path
            relative_path = os.path.relpath(root, unc)
            indent_level = relative_path.count(os.path.sep)

            # Adjust heading level based on start_heading
            heading_level = start_heading + indent_level

            # Format and append to the result
            formatted_item = f"{'#' * heading_level} {os.path.basename(root)}"
            result.append(formatted_item)

            # Print files in the current folder
            for file in files:
                file_path = os.path.join(root, file)
                file_heading_level = heading_level + 1  # Set the number of hashes for files
                formatted_file = f"{'#' * file_heading_level} {file_path[len(str(unc)) + 1:]}"
                result.append(formatted_file)

        return result

    def export_to_dataframe(folder_path, unc):
        formatted_structure = list_folder_structure(folder_path, unc)

        # Create a Pandas DataFrame
        df = pd.DataFrame({
            'unc': [os.path.join(unc, item.split(' ', 1)[1]) for item in formatted_structure],
            'formatted_structure': [os.path.basename(item.split(' ', 1)[1]) for item in formatted_structure],
            'num_hashes': [item.count('#') for item in formatted_structure]
        })

        return df

    # run
    output_dataframe = export_to_dataframe(unc, unc)
    output_dataframe = output_dataframe.drop(output_dataframe.index[[0]]).reset_index(drop=True)


    ## scan files
    def scan_py_files_for_headings_modified(unc, num_hashes):

        """ function to extract comments from python a file and export as .md to create markmap """

        # Read the file and process lines
        lines = []
        flags = []
        extracts = []

        if heading_order == 0:
            pattern0 = re.compile(r'^(#|--) ')
            pattern1 = re.compile(r'^# %% ')
            pattern2 = re.compile(r'^###### ')
            pattern3 = re.compile(r'^##### ')
            pattern4 = re.compile(r'^#### ')
            pattern5 = re.compile(r'^### ')
            pattern6 = re.compile(r'^## ')
            pattern7 = re.compile(r'^#([^ ]+)')

            with open(unc, 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    lines.append(line.strip())
                    if pattern1.match(line):
                        flags.append(1+num_hashes)
                        extracts.append(pattern1.sub('', line).strip())
                    elif pattern2.match(line):
                        flags.append(2+num_hashes)
                        extracts.append(pattern2.sub('', line).strip())
                    elif pattern3.match(line):
                        flags.append(3+num_hashes)
                        extracts.append(pattern3.sub('', line).strip())
                    elif pattern4.match(line):
                        flags.append(4+num_hashes)
                        extracts.append(pattern4.sub('', line).strip())
                    elif pattern5.match(line):
                        flags.append(5+num_hashes)
                        extracts.append(pattern5.sub('', line).strip())
                    elif pattern6.match(line):
                        flags.append(6+num_hashes)
                        extracts.append(pattern6.sub('', line).strip())
                    elif pattern7.match(line):
                        flags.append(999+num_hashes)
                        extracts.append(pattern7.sub(r'\1', line).strip())
                    elif pattern0.match(line):
                        flags.append(-1)
                        extracts.append(pattern0.sub('', line).strip())
                    else:
                        flags.append(0)
                        extracts.append(line.strip())
        else:
            pattern0 = re.compile(r'^(#|--) ')
            pattern1 = re.compile(r'^# %% ')
            pattern2 = re.compile(r'^## ')
            pattern3 = re.compile(r'^### ')
            pattern4 = re.compile(r'^#### ')
            pattern5 = re.compile(r'^##### ')
            pattern6 = re.compile(r'^###### ')
            pattern7 = re.compile(r'^#([^ ]+)')

            with open(unc, 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    lines.append(line.strip())
                    if pattern1.match(line):
                        flags.append(1+num_hashes)
                        extracts.append(pattern1.sub('', line).strip())
                    elif pattern2.match(line):
                        flags.append(2+num_hashes)
                        extracts.append(pattern2.sub('', line).strip())
                    elif pattern3.match(line):
                        flags.append(3+num_hashes)
                        extracts.append(pattern3.sub('', line).strip())
                    elif pattern4.match(line):
                        flags.append(4+num_hashes)
                        extracts.append(pattern4.sub('', line).strip())
                    elif pattern5.match(line):
                        flags.append(5+num_hashes)
                        extracts.append(pattern5.sub('', line).strip())
                    elif pattern6.match(line):
                        flags.append(6+num_hashes)
                        extracts.append(pattern6.sub('', line).strip())
                    elif pattern7.match(line):
                        flags.append(999+num_hashes)
                        extracts.append(pattern7.sub(r'\1', line).strip())
                    elif pattern0.match(line):
                        flags.append(-1)
                        extracts.append(pattern0.sub('', line).strip())
                    else:
                        flags.append(0)
                        extracts.append(line.strip())

        # Create a DataFrame
        df = pd.DataFrame({'line': lines, 'flag': flags, 'extract': extracts})

        # Create markdown
        df['hierarchy'] = np.where((df['flag'].between(1,15)), df['flag'].apply(lambda x: '#' * x), np.nan)
        df['hierarchy'] = np.where((df['flag'] == -1), '-', df['hierarchy'])
        df['md'] = np.where((df['hierarchy'].isnull()), '', df['hierarchy']+' '+df['extract'])

        markdown_string = ''
        for i in df['md']:
            if i != '':
                markdown_string = markdown_string + '\n'+ i

        return markdown_string


    ## combine folder and file heading structure
    for i in range(0, len(output_dataframe)):
        if isfile(output_dataframe.loc[i, 'unc']):
            output_dataframe.loc[i, 'file_md'] = scan_py_files_for_headings_modified(output_dataframe.loc[i, 'unc'], output_dataframe.loc[i, 'num_hashes'])

    for i in range(0, len(output_dataframe)):
        base_string = '#'*output_dataframe.loc[i, 'num_hashes'] + ' '+ output_dataframe.loc[i, 'formatted_structure']
        if pd.isna(output_dataframe.loc[i, 'file_md']):
            output_dataframe.loc[i, 'md'] = base_string+'\n'
        else:
            output_dataframe.loc[i, 'md'] = base_string+'\n'+output_dataframe.loc[i, 'file_md']+'\n'

    # create markdown
    markdown_statement = f"{md_name}\n"  # Add the md_name as the first line
    for i in output_dataframe['md']:
        markdown_statement = markdown_statement+'\n'+str(i)

    # export
    def export_to_file(file_path, content):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        # Open the file automatically
        try:
            os.startfile(file_path)
        except AttributeError:
            # For non-Windows systems
            subprocess.run(['open', file_path], check=True)

    output_file_path = str(unc).split('\\')[-1]+'.md'

    #formatted_structure = list_folder_structure(folder_path)
    export_to_file(output_file_path, markdown_statement)

if __name__ == '__main__':
    unc = Path("C:/my_disk/edupunk/src/functions")
    md_name_str = """---
    title: Project report
    markmap:
    colorFreezeLevel: 4
    maxWidth: 300
    embedAssets: true
    initialExpandLevel: 4
    ---"""
    scan_py_files_in_folders_for_headings(unc, md_name=md_name_str, heading_order=1)


def scan_py_files_in_folders_for_headings_detailed(unc, md_name='Project report', heading_order=0, start_heading=1, max_heading_level=6, include_comments=True):

    """ function to extract directory tree and python file headings to be human readable
        heading_order = 1: ascending i.e. markdown default heading hierarchy
        heading_order = 0: descending
        start_heading = 1: the starting heading level for the top folder
        max_heading_level = 6: maximum heading level to include in the output
        md_name = 'Project report': the first line in the .md output
        include_comments = True: whether to include comments in the output
    """

    # scan folder
    def list_folder_structure(folder_path, unc):
        result = []

        for root, dirs, files in os.walk(folder_path):
            # Calculate the indentation level based on the relative path
            relative_path = os.path.relpath(root, unc)
            indent_level = relative_path.count(os.path.sep)

            # Adjust heading level based on start_heading
            heading_level = start_heading + indent_level

            if heading_level <= max_heading_level:
                # Format and append to the result
                formatted_item = f"{'#' * heading_level} {os.path.basename(root)}"
                result.append(formatted_item)

                # Print files in the current folder
                for file in files:
                    file_path = os.path.join(root, file)
                    file_heading_level = heading_level + 1  # Set the number of hashes for files
                    if file_heading_level <= max_heading_level:
                        formatted_file = f"{'#' * file_heading_level} {file_path[len(str(unc)) + 1:]}"
                        result.append(formatted_file)

        return result

    def export_to_dataframe(folder_path, unc):
        formatted_structure = list_folder_structure(folder_path, unc)

        # Create a Pandas DataFrame
        df = pd.DataFrame({
            'unc': [os.path.join(unc, item.split(' ', 1)[1]) for item in formatted_structure],
            'formatted_structure': [os.path.basename(item.split(' ', 1)[1]) for item in formatted_structure],
            'num_hashes': [item.count('#') for item in formatted_structure]
        })

        return df

    # run
    output_dataframe = export_to_dataframe(unc, unc)
    output_dataframe = output_dataframe.drop(output_dataframe.index[[0]]).reset_index(drop=True)

    # scan files
    def scan_py_files_for_headings_modified(unc, num_hashes):
        """ function to extract comments from a python file and export as .md to create markmap """

        # Read the file and process lines
        lines = []
        flags = []
        extracts = []

        if heading_order == 0:
            pattern0 = re.compile(r'^\s*(#|--) ')  # Matches lines with leading spaces followed by # or --
            pattern1 = re.compile(r'^\s*# %% ')    # Matches lines with # %% and leading spaces
            pattern2 = re.compile(r'^\s*###### ') # Matches lines with ###### and leading spaces
            pattern3 = re.compile(r'^\s*##### ')  # Matches lines with ##### and leading spaces
            pattern4 = re.compile(r'^\s*#### ')   # Matches lines with #### and leading spaces
            pattern5 = re.compile(r'^\s*### ')    # Matches lines with ### and leading spaces
            pattern6 = re.compile(r'^\s*## ')     # Matches lines with ## and leading spaces
            pattern7 = re.compile(r'^\s*#([^ ]+)') # Matches lines with # followed by non-space characters

        else:
            pattern0 = re.compile(r'^\s*(#|--) ')
            pattern1 = re.compile(r'^\s*# %% ')
            pattern2 = re.compile(r'^\s*## ')
            pattern3 = re.compile(r'^\s*### ')
            pattern4 = re.compile(r'^\s*#### ')
            pattern5 = re.compile(r'^\s*##### ')
            pattern6 = re.compile(r'^\s*###### ')
            pattern7 = re.compile(r'^\s*#([^ ]+)')

        with open(unc, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                lines.append(line.strip())
                if pattern1.match(line) and 1 + num_hashes <= max_heading_level:
                    flags.append(1 + num_hashes)
                    extracts.append(pattern1.sub('', line).strip())
                elif pattern2.match(line) and 2 + num_hashes <= max_heading_level:
                    flags.append(2 + num_hashes)
                    extracts.append(pattern2.sub('', line).strip())
                elif pattern3.match(line) and 3 + num_hashes <= max_heading_level:
                    flags.append(3 + num_hashes)
                    extracts.append(pattern3.sub('', line).strip())
                elif pattern4.match(line) and 4 + num_hashes <= max_heading_level:
                    flags.append(4 + num_hashes)
                    extracts.append(pattern4.sub('', line).strip())
                elif pattern5.match(line) and 5 + num_hashes <= max_heading_level:
                    flags.append(5 + num_hashes)
                    extracts.append(pattern5.sub('', line).strip())
                elif pattern6.match(line) and 6 + num_hashes <= max_heading_level:
                    flags.append(6 + num_hashes)
                    extracts.append(pattern6.sub('', line).strip())
                elif pattern7.match(line):
                    flags.append(999 + num_hashes)
                    extracts.append(pattern7.sub(r'\1', line).strip())
                elif include_comments and pattern0.match(line):
                    flags.append(-1)
                    extracts.append(pattern0.sub('', line).strip())
                else:
                    flags.append(0)
                    extracts.append(line.strip())

        # Create a DataFrame
        df = pd.DataFrame({'line': lines, 'flag': flags, 'extract': extracts})

        # Create markdown
        df['hierarchy'] = np.where((df['flag'].between(1, max_heading_level)), df['flag'].apply(lambda x: '#' * x), np.nan)
        df['hierarchy'] = np.where((df['flag'] == -1), '-', df['hierarchy'])
        df['md'] = np.where((df['hierarchy'].isnull()), '', df['hierarchy'] + ' ' + df['extract'])

        markdown_string = ''
        for i in df['md']:
            if i != '':
                markdown_string = markdown_string + '\n' + i

        return markdown_string

    # combine folder and file heading structure
    for i in range(0, len(output_dataframe)):
        if isfile(output_dataframe.loc[i, 'unc']):
            output_dataframe.loc[i, 'file_md'] = scan_py_files_for_headings_modified(output_dataframe.loc[i, 'unc'], output_dataframe.loc[i, 'num_hashes'])

    for i in range(0, len(output_dataframe)):
        base_string = '#'*output_dataframe.loc[i, 'num_hashes'] + ' '+ output_dataframe.loc[i, 'formatted_structure']
        if pd.isna(output_dataframe.loc[i, 'file_md']):
            output_dataframe.loc[i, 'md'] = base_string+'\n'
        else:
            output_dataframe.loc[i, 'md'] = base_string+'\n'+output_dataframe.loc[i, 'file_md']+'\n'

    # create markdown
    markdown_statement = f"{md_name}\n"  # Add the md_name as the first line
    for i in output_dataframe['md']:
        markdown_statement = markdown_statement+'\n'+str(i)

    # export
    def export_to_file(file_path, content):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        # Open the file automatically
        try:
            os.startfile(file_path)
        except AttributeError:
            # For non-Windows systems
            subprocess.run(['open', file_path], check=True)

    output_file_path = str(unc).split('\\')[-1]+'.md'

    # formatted_structure = list_folder_structure(folder_path)
    export_to_file(output_file_path, markdown_statement)

if __name__ == '__main__':
    scan_py_files_in_folders_for_headings_detailed(
        unc,
        md_name=md_name_str,
        heading_order=1,
        start_heading=1,
        max_heading_level=6,
        include_comments=True,
    )
