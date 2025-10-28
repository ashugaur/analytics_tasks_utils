# %% Export functions

## Dependencies
from pathlib import Path
import zipfile
import os
from datetime import datetime
import shutil
from analytics_tasks_utils.os_functions import open_file_folder
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

def export_folder_as_zip(source_folder, destination_folder, exclude_folder_names=None):
    if exclude_folder_names is None:
        exclude_folder_names = []

    os.chdir(destination_folder)

    output_filename = str(source_folder).rsplit("\\")[-1] + ".zip"
    zf = zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED)

    for dirname, subdirs, files in os.walk(source_folder):
        # Check if current directory or any parent directory should be excluded
        relative_path = os.path.relpath(dirname, source_folder)
        path_parts = relative_path.split(os.sep)

        # Skip if any part of the path matches excluded folder names
        if any(part in exclude_folder_names for part in path_parts):
            subdirs.clear()  # Don't traverse subdirectories of excluded folders
            continue

        # Also check the folder name itself
        folder_name = os.path.basename(dirname)
        if folder_name in exclude_folder_names:
            subdirs.clear()  # Don't traverse subdirectories of excluded folders
            continue

        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))

    zf.close()


def export_folder_as_zip_nfp(
    source_folder, destination_folder, exclude_folder_names=None
):
    import os
    import zipfile

    if exclude_folder_names is None:
        exclude_folder_names = []

    os.chdir(destination_folder)

    output_filename = str(source_folder).rsplit("\\")[-1] + ".zip"

    # Create zip file
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zf:
        # Walk through the source folder
        for dirname, subdirs, files in os.walk(source_folder):
            # Check if current directory or any parent directory should be excluded
            relative_path = os.path.relpath(dirname, source_folder)
            path_parts = relative_path.split(os.sep)

            # Skip if any part of the path matches excluded folder names
            if any(part in exclude_folder_names for part in path_parts):
                subdirs.clear()  # Don't traverse subdirectories of excluded folders
                continue

            # Also check the folder name itself
            folder_name = os.path.basename(dirname)
            if folder_name in exclude_folder_names:
                subdirs.clear()  # Don't traverse subdirectories of excluded folders
                continue

            # Add files to zip
            for filename in files:
                # Get the absolute path of the file
                absolute_path = os.path.join(dirname, filename)
                # Create arcname (path within the zip file)
                arcname = os.path.relpath(absolute_path, source_folder)

                # Write file to zip
                zf.write(absolute_path, arcname)


def export_folder_as_zip_timestamp(
    source_folder, destination_folder, exclude_folder_names=None
):
    if exclude_folder_names is None:
        exclude_folder_names = []

    now = datetime.now()
    folder_dt = (
        "{:02d}".format(now.year)
        + "{:02d}".format(now.month)
        + "{:02d}".format(now.day)
    )
    file_dt = (
        "{:02d}".format(now.year)
        + "{:02d}".format(now.month)
        + "{:02d}".format(now.day)
        + "_"
        + "{:02d}".format(now.hour)
        + "{:02d}".format(now.minute)
    )

    os.chdir(destination_folder)

    output_filename = str(source_folder).rsplit("\\")[-1] + "_" + file_dt + ".zip"
    zf = zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED)

    for dirname, subdirs, files in os.walk(source_folder):
        # Check if current directory or any parent directory should be excluded
        relative_path = os.path.relpath(dirname, source_folder)
        path_parts = relative_path.split(os.sep)

        # Skip if any part of the path matches excluded folder names
        if any(part in exclude_folder_names for part in path_parts):
            subdirs.clear()  # Don't traverse subdirectories of excluded folders
            continue

        # Also check the folder name itself
        folder_name = os.path.basename(dirname)
        if folder_name in exclude_folder_names:
            subdirs.clear()  # Don't traverse subdirectories of excluded folders
            continue

        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))

    zf.close()


def backup_folder_force_old(source_folder, destination_folder):
    import shutil
    import os

    try:
        # Delete the destination folder if it exists
        if os.path.exists(destination_folder):
            shutil.rmtree(destination_folder)

        # Copy the source folder to the destination
        shutil.copytree(source_folder, destination_folder)
        # print(f"\nFolder '{source_folder}'\n\tcopied to \n\t'{destination_folder}' successfully.")
    except shutil.Error as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def backup_folder_force(source_folder, destination_folder, exclude_folders=None):
    """
    Copies the source folder to the destination, excluding specified folders.

    Args:
        source_folder (str): The path to the source folder.
        destination_folder (str): The path to the destination folder.
        exclude_folders (list, optional): A list of folder names to exclude. Defaults to None.
    """

    try:
        # Delete the destination folder if it exists
        if os.path.exists(destination_folder):
            shutil.rmtree(destination_folder)

        # Copy the source folder to the destination, excluding specified folders
        if exclude_folders is None:
            shutil.copytree(source_folder, destination_folder)
        else:
            shutil.copytree(
                source_folder,
                destination_folder,
                ignore=shutil.ignore_patterns(*exclude_folders),
            )

    except shutil.Error as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def zip_files(file_list, destination_file):
    """
    Zips a list of files into a single zip file.

    Args:
        file_list (list): A list of file paths to zip.
        destination_file (str): The path to the destination zip file.
    """

    try:
        # Create a zip file
        with zipfile.ZipFile(destination_file, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add files to the zip file
            for file in file_list:
                if os.path.exists(file):
                    relative_path = os.path.relpath(file)
                    zip_file.write(file, relative_path)
                else:
                    print(f"File not found: {file}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    file_list = [
        "/path/to/file1.txt",
        "/path/to/folder/file2.txt",
        "/path/to/file3.pdf",
    ]
    destination_file = "/path/to/destination/zipfile.zip"

    zip_files(file_list, destination_file)


# %% Dataframe to HTML


def generate_html_with_color_and_copy(hex_color):
    html_copy_button = f'<button onclick="copyToClipboard(\'{hex_color}\')" style="width: 60px; height: 20px; background-color: {hex_color}; border: none;"></button>'
    return f"<div>{html_copy_button}</div>"


def generate_html_from_dataframe(df, color_column_name):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Colors.py scan</title>
    <link href="../../assets/data_table/bootstrap.min.css" rel="stylesheet">
    <script src="../../assets/data_table/jquery.min.js"></script>
    <link rel="stylesheet" href="../../assets/data_table/jquery.dataTables.min.css">
    <script type="text/javascript" src="../../assets/data_table/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="../../assets/data_table/bootstrap.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#myTable').dataTable({
                "pageLength": 100 /*load number of rows*/
            });
        });

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text)
                .then(() => {
                    console.log('Copied to clipboard');
                    showNotification('Copied: ' + text);
                })
                .catch(err => {
                    console.error('Error copying to clipboard:', err);
                });
        }

        function showNotification(message) {
            var notification = document.createElement('div');
            notification.textContent = message;
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.left = '50%';
            notification.style.transform = 'translateX(-50%)';
            notification.style.background = '#d95f0e';
            notification.style.padding = '10px';
            notification.style.border = '1px solid #ccc';
            notification.style.borderRadius = '5px';
            notification.style.boxShadow = '0 0 10px rgba(0,0,0,0.1)';
            notification.style.zIndex = '9999';
            document.body.appendChild(notification);
            setTimeout(function() {
                document.body.removeChild(notification);
            }, 3000); // Remove notification after 3 seconds
        }
    </script>
    <style>
        body {
            margin: 0;
            padding: 0;
            /*background-color: transparent;*/ /* Set background color to transparent */
        }
        h1 {
            /* text-align: center; */
            margin-top: 20px;
        }
        table {
            width: 70%;
            margin: 20px auto;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            /* text-align: center; */
            border: 1px solid #ddd;
        }
        th {
            vertical-align: middle;
        }
        .color-cell {
            width: 100px;
            /* text-align: center; */
        }
        button {
            padding: 0;
            line-height: 0;
        }
    </style>
</head>
<body style="margin:20px auto">
    <div class="container">
        <h1 style="padding:0; margin-top:0px"></h1>
        <table id="myTable" class="table table-striped">
            <thead>
                <tr>
"""

    # Add table headers dynamically
    for col in df.columns:
        html_content += f"                    <th>{col}</th>\n"
    html_content += "                    <th>Display color</th>\n"
    html_content += "                </tr>\n"
    html_content += "            </thead>\n"
    html_content += "            <tbody>\n"

    # Iterate over DataFrame rows
    for _, row in df.iterrows():
        html_content += "                <tr>\n"
        for col in df.columns:
            html_content += f"                    <td>{row[col]}</td>\n"
        html_content += f'                    <td class="color-cell">{generate_html_with_color_and_copy(row[color_column_name])}</td>\n'
        html_content += "                </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    return html_content


def generate_html_with_color_and_copy_dark(hex_color):
    html_copy_button = f'<button onclick="copyToClipboard(\'{hex_color}\')" style="width: 60px; height: 20px; background-color: {hex_color}; border: none;"></button>'
    return f"<div>{html_copy_button}</div>"


def generate_html_from_dataframe_dark(df, color_column_name):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Colors.py scan</title>
    <link href="../../assets/data_table/bootstrap.min.css" rel="stylesheet">
    <script src="../../assets/data_table/jquery.min.js"></script>
    <link rel="stylesheet" href="../../assets/data_table/jquery.dataTables.min.css">
    <script type="text/javascript" src="../../assets/data_table/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="../../assets/data_table/bootstrap.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#myTable').dataTable({
                "pageLength": 100 /*load number of rows*/
            });
        });

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text)
                .then(() => {
                    console.log('Copied to clipboard');
                    showNotification('Copied: ' + text);
                })
                .catch(err => {
                    console.error('Error copying to clipboard:', err);
                });
        }

        function showNotification(message) {
            var notification = document.createElement('div');
            notification.textContent = message;
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.left = '50%';
            notification.style.transform = 'translateX(-50%)';
            notification.style.background = '#d95f0e';
            notification.style.padding = '10px';
            notification.style.border = '1px solid #ccc';
            notification.style.borderRadius = '5px';
            notification.style.boxShadow = '0 0 10px rgba(0,0,0,0.1)';
            notification.style.zIndex = '9999';
            document.body.appendChild(notification);
            setTimeout(function() {
                document.body.removeChild(notification);
            }, 3000); // Remove notification after 3 seconds
        }
    </script>
    <style>
        /* Light mode styles */
        body {
            background-color: white;  /* Background outside the table */
            color: black;
        }

        table {
            background-color: white;
            color: black;
        }

        th, td {
            border: 1px solid #ddd;
            background-color: white;
            color: black;
        }

        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1e2129;  /* Dark mode background outside the table */
                color: #e0e0e0;
            }

            /* Optional: you can also target the container specifically if you want */
            .container {
                background-color: #1e2129; /* Dark mode container background */
            }

            /* Table styles in dark mode */
            table, .dataTables_wrapper {
                background-color: #333 !important;
                color: bdbdbd !important;
            }

            th, td {
                border-color: #555;
                background-color: #444 !important; /* Ensure all table cells have dark background */
                color: #bdbdbd !important; /* Ensure all text in table is white */
            }

            /* DataTable plugin-specific styles */
            .dataTables_wrapper .dataTables_paginate .paginate_button {
                background-color: #444 !important; /* Dark background for pagination buttons */
                color: bdbdbd !important; /* White text on pagination buttons */
            }

            .dataTables_wrapper .dataTables_filter input,
            .dataTables_wrapper .dataTables_length select,
            .dataTables_wrapper .dataTables_info {
                background-color: #444 !important; /* Dark background for inputs and dropdowns */
                color: white !important; /* White text for input fields */
            }

            /* Change hover effect in dark mode */
            tr:hover {
                background-color: #636363 !important;
            }

            /* Fix for "Show entries" and "Search" labels */
            .dataTables_wrapper .dataTables_length label,
            .dataTables_wrapper .dataTables_filter label {
                color: #bdbdbd !important; /* Ensure labels like "Show entries" and "Search" are white */
            }
        }
    </style>
</head>
<body style="margin:20px auto">
    <div class="container">
        <h1 style="padding:0; margin-top:0px"></h1>
        <table id="myTable" class="table table-striped">
            <thead>
                <tr>
"""

    # Add table headers dynamically
    for col in df.columns:
        html_content += f"                    <th>{col}</th>\n"
    html_content += "                    <th>Display color</th>\n"
    html_content += "                </tr>\n"
    html_content += "            </thead>\n"
    html_content += "            <tbody>\n"

    # Iterate over DataFrame rows
    for _, row in df.iterrows():
        html_content += "                <tr>\n"
        for col in df.columns:
            html_content += f"                    <td>{row[col]}</td>\n"
        html_content += f'                    <td class="color-cell">{generate_html_with_color_and_copy_dark(row[color_column_name])}</td>\n'
        html_content += "                </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    return html_content


# %% Dataframe to Data table

def dataframe_to_data_table(
    df, func="generate_data_table_from_dataframe_text_dark_internet", out_file=None
):
    func_ref = globals()[func]
    html_content = func_ref(df)
    if out_file is None:
        out_file = Path(
            "C:/my_disk/____tmp/generate_data_table_from_dataframe_text_dark_internet.html"
        )
    with open(Path(out_file), "w") as f:
        f.write(html_content)
    open_file_folder(out_file)


def generate_data_table_from_dataframe_internet(df):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>DataFrame Table</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <script type="text/javascript" src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/js/bootstrap.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#myTable').dataTable({
                "pageLength": 100 /*load number of rows*/
            });
        });
    </script>
    <style>
        body {
            margin: 0;
            padding: 0;
            /*background-color: transparent;*/ /* Set background color to transparent */
        }
        h1 {
            /* text-align: center; */
            margin-top: 20px;
        }
        table {
            width: 70%;
            margin: 20px auto;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            /* text-align: center; */
            border: 1px solid #ddd;
        }
        th {
            vertical-align: middle;
        }
        .color-cell {
            width: 100px;
            /* text-align: center; */
        }
        button {
            padding: 0;
            line-height: 0;
        }
    </style>
</head>
<body style="margin:20px auto">
    <div class="container">
        <h1 style="padding:0; margin-top:0px"></h1>
        <table id="myTable" class="table table-striped">
            <thead>
                <tr>
"""

    # Add table headers dynamically
    for col in df.columns:
        html_content += f"                    <th>{col}</th>\n"
    html_content += "                </tr>\n"
    html_content += "            </thead>\n"
    html_content += "            <tbody>\n"

    # Iterate over DataFrame rows
    for _, row in df.iterrows():
        html_content += "                <tr>\n"
        for col in df.columns:
            html_content += f"                    <td>{row[col]}</td>\n"
        html_content += "                </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    return html_content


def generate_data_table_from_dataframe(df):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>DataFrame Table</title>
    <link href="../../assets/data_table/bootstrap.min.css" rel="stylesheet">
    <script src="../../assets/data_table/jquery.min.js"></script>
    <link rel="stylesheet" href="../../assets/data_table/jquery.dataTables.min.css">
    <script type="text/javascript" src="../../assets/data_table/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="../../assets/data_table/bootstrap.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#myTable').dataTable({
                "pageLength": 100 /*load number of rows*/
            });
        });
    </script>
    <style>
        body {
            margin: 0;
            padding: 0;
            /*background-color: transparent;*/ /* Set background color to transparent */
        }
        h1 {
            /* text-align: center; */
            margin-top: 20px;
        }
        table {
            width: 70%;
            margin: 20px auto;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            /* text-align: center; */
            border: 1px solid #ddd;
        }
        th {
            vertical-align: middle;
        }
        .color-cell {
            width: 100px;
            /* text-align: center; */
        }
        button {
            padding: 0;
            line-height: 0;
        }
    </style>
</head>
<body style="margin:20px auto">
    <div class="container">
        <h1 style="padding:0; margin-top:0px"></h1>
        <table id="myTable" class="table table-striped">
            <thead>
                <tr>
"""

    # Add table headers dynamically
    for col in df.columns:
        html_content += f"                    <th>{col}</th>\n"
    html_content += "                </tr>\n"
    html_content += "            </thead>\n"
    html_content += "            <tbody>\n"

    # Iterate over DataFrame rows
    for _, row in df.iterrows():
        html_content += "                <tr>\n"
        for col in df.columns:
            html_content += f"                    <td>{row[col]}</td>\n"
        html_content += "                </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    return html_content


def generate_data_table_from_dataframe_dark_internet(df):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>DataFrame Table</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <script type="text/javascript" src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/js/bootstrap.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#myTable').dataTable({
                "pageLength": 100 /*load number of rows*/
            });
        });
    </script>
    <style>
        /* Light mode styles */
        body {
            background-color: white;  /* Background outside the table */
            color: black;
        }

        table {
            background-color: white;
            color: black;
        }

        th, td {
            border: 1px solid #ddd;
            background-color: white;
            color: black;
        }

        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1e2129;  /* Dark mode background outside the table */
                color: #e0e0e0;
            }

            /* Optional: you can also target the container specifically if you want */
            .container {
                background-color: #1e2129; /* Dark mode container background */
            }

            /* Table styles in dark mode */
            table, .dataTables_wrapper {
                background-color: #333 !important;
                color: bdbdbd !important;
            }

            th, td {
                border-color: #555;
                background-color: #444 !important; /* Ensure all table cells have dark background */
                color: #bdbdbd !important; /* Ensure all text in table is white */
            }

            /* DataTable plugin-specific styles */
            .dataTables_wrapper .dataTables_paginate .paginate_button {
                background-color: #444 !important; /* Dark background for pagination buttons */
                color: bdbdbd !important; /* White text on pagination buttons */
            }

            .dataTables_wrapper .dataTables_filter input,
            .dataTables_wrapper .dataTables_length select,
            .dataTables_wrapper .dataTables_info {
                background-color: #444 !important; /* Dark background for inputs and dropdowns */
                color: white !important; /* White text for input fields */
            }

            /* Change hover effect in dark mode */
            tr:hover {
                background-color: #636363 !important;
            }

            /* Fix for "Show entries" and "Search" labels */
            .dataTables_wrapper .dataTables_length label,
            .dataTables_wrapper .dataTables_filter label {
                color: #bdbdbd !important; /* Ensure labels like "Show entries" and "Search" are white */
            }
        }
    </style>
</head>
<body style="margin:20px auto">
    <div class="container">
        <h1 style="padding:0; margin-top:0px"></h1>
        <table id="myTable" class="table table-striped">
            <thead>
                <tr>
"""

    # Add table headers dynamically
    for col in df.columns:
        html_content += f"                    <th>{col}</th>\n"
    html_content += "                </tr>\n"
    html_content += "            </thead>\n"
    html_content += "            <tbody>\n"

    # Iterate over DataFrame rows
    for _, row in df.iterrows():
        html_content += "                <tr>\n"
        for col in df.columns:
            html_content += f"                    <td>{row[col]}</td>\n"
        html_content += "                </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    return html_content


def generate_data_table_from_dataframe_dark(df):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>DataFrame Table</title>
    <link href="../../assets/data_table/bootstrap.min.css" rel="stylesheet">
    <script src="../../assets/data_table/jquery.min.js"></script>
    <link rel="stylesheet" href="../../assets/data_table/jquery.dataTables.min.css">
    <script type="text/javascript" src="../../assets/data_table/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="../../assets/data_table/bootstrap.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#myTable').dataTable({
                "pageLength": 100 /*load number of rows*/
            });
        });
    </script>
    <style>
        /* Light mode styles */
        body {
            background-color: white;  /* Background outside the table */
            color: black;
        }

        table {
            background-color: white;
            color: black;
        }

        th, td {
            border: 1px solid #ddd;
            background-color: white;
            color: black;
        }

        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1e2129;  /* Dark mode background outside the table */
                color: #e0e0e0;
            }

            /* Optional: you can also target the container specifically if you want */
            .container {
                background-color: #1e2129; /* Dark mode container background */
            }

            /* Table styles in dark mode */
            table, .dataTables_wrapper {
                background-color: #333 !important;
                color: bdbdbd !important;
            }

            th, td {
                border-color: #555;
                background-color: #444 !important; /* Ensure all table cells have dark background */
                color: #bdbdbd !important; /* Ensure all text in table is white */
            }

            /* DataTable plugin-specific styles */
            .dataTables_wrapper .dataTables_paginate .paginate_button {
                background-color: #444 !important; /* Dark background for pagination buttons */
                color: bdbdbd !important; /* White text on pagination buttons */
            }

            .dataTables_wrapper .dataTables_filter input,
            .dataTables_wrapper .dataTables_length select,
            .dataTables_wrapper .dataTables_info {
                background-color: #444 !important; /* Dark background for inputs and dropdowns */
                color: white !important; /* White text for input fields */
            }

            /* Change hover effect in dark mode */
            tr:hover {
                background-color: #636363 !important;
            }

            /* Fix for "Show entries" and "Search" labels */
            .dataTables_wrapper .dataTables_length label,
            .dataTables_wrapper .dataTables_filter label {
                color: #bdbdbd !important; /* Ensure labels like "Show entries" and "Search" are white */
            }
        }
    </style>
</head>
<body style="margin:20px auto">
    <div class="container">
        <h1 style="padding:0; margin-top:0px"></h1>
        <table id="myTable" class="table table-striped">
            <thead>
                <tr>
"""

    # Add table headers dynamically
    for col in df.columns:
        html_content += f"                    <th>{col}</th>\n"
    html_content += "                </tr>\n"
    html_content += "            </thead>\n"
    html_content += "            <tbody>\n"

    # Iterate over DataFrame rows
    for _, row in df.iterrows():
        html_content += "                <tr>\n"
        for col in df.columns:
            html_content += f"                    <td>{row[col]}</td>\n"
        html_content += "                </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    return html_content


def generate_data_table_from_dataframe_text_dark_internet(df):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>DataFrame Table</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <script type="text/javascript" src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/js/bootstrap.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#myTable').dataTable({
                "pageLength": 100 /*load number of rows*/
            });
        });
    </script>
    <style>
        /* Light mode styles */
        body {
            background-color: white;  /* Background outside the table */
            color: black;
        }

        table {
            background-color: white;
            color: black;
        }

        th, td {
            border: 1px solid #ddd;
            background-color: white;
            color: black;
        }

        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1e2129;  /* Dark mode background outside the table */
                color: #e0e0e0;
            }

            /* Optional: you can also target the container specifically if you want */
            .container {
                background-color: #1e2129; /* Dark mode container background */
            }

            /* Table styles in dark mode */
            table, .dataTables_wrapper {
                background-color: #333 !important;
                color: bdbdbd !important;
            }

            th, td {
                border-color: #555;
                background-color: #444 !important; /* Ensure all table cells have dark background */
                color: #bdbdbd !important; /* Ensure all text in table is white */
            }

            /* DataTable plugin-specific styles */
            .dataTables_wrapper .dataTables_paginate .paginate_button {
                background-color: #444 !important; /* Dark background for pagination buttons */
                color: bdbdbd !important; /* White text on pagination buttons */
            }

            .dataTables_wrapper .dataTables_filter input,
            .dataTables_wrapper .dataTables_length select,
            .dataTables_wrapper .dataTables_info {
                background-color: #444 !important; /* Dark background for inputs and dropdowns */
                color: white !important; /* White text for input fields */
            }

            /* Change hover effect in dark mode */
            tr:hover {
                background-color: #636363 !important;
            }

            /* Fix for "Show entries" and "Search" labels */
            .dataTables_wrapper .dataTables_length label,
            .dataTables_wrapper .dataTables_filter label {
                color: #bdbdbd !important; /* Ensure labels like "Show entries" and "Search" are white */
            }
        }
    </style>
</head>
<body style="margin:20px auto">
    <div class="container">
        <h1 style="padding:0; margin-top:0px"></h1>
        <table id="myTable" class="table table-striped">
            <thead>
                <tr>
"""

    # Add table headers dynamically
    for col in df.columns:
        html_content += f"                    <th>{col}</th>\n"
    html_content += "                </tr>\n"
    html_content += "            </thead>\n"
    html_content += "            <tbody>\n"

    # Iterate over DataFrame rows
    for _, row in df.iterrows():
        html_content += "                <tr>\n"
        for col in df.columns:
            html_content += f"                    <td>{row[col]}</td>\n"
        html_content += "                </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    return html_content


def generate_data_table_from_dataframe_text_dark(df):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>DataFrame Table</title>
    <link href="../../../../assets/data_table/bootstrap.min.css" rel="stylesheet">
    <script src="../../../../assets/data_table/jquery.min.js"></script>
    <link rel="stylesheet" href="../../../../assets/data_table/jquery.dataTables.min.css">
    <script type="text/javascript" src="../../../../assets/data_table/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="../../../../assets/data_table/bootstrap.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#myTable').dataTable({
                "pageLength": 100 /*load number of rows*/
            });
        });
    </script>
    <style>
        /* Light mode styles */
        body {
            background-color: white;  /* Background outside the table */
            color: black;
        }

        table {
            background-color: white;
            color: black;
        }

        th, td {
            border: 1px solid #ddd;
            background-color: white;
            color: black;
        }

        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1e2129;  /* Dark mode background outside the table */
                color: #e0e0e0;
            }

            /* Optional: you can also target the container specifically if you want */
            .container {
                background-color: #1e2129; /* Dark mode container background */
            }

            /* Table styles in dark mode */
            table, .dataTables_wrapper {
                background-color: #333 !important;
                color: bdbdbd !important;
            }

            th, td {
                border-color: #555;
                background-color: #444 !important; /* Ensure all table cells have dark background */
                color: #bdbdbd !important; /* Ensure all text in table is white */
            }

            /* DataTable plugin-specific styles */
            .dataTables_wrapper .dataTables_paginate .paginate_button {
                background-color: #444 !important; /* Dark background for pagination buttons */
                color: bdbdbd !important; /* White text on pagination buttons */
            }

            .dataTables_wrapper .dataTables_filter input,
            .dataTables_wrapper .dataTables_length select,
            .dataTables_wrapper .dataTables_info {
                background-color: #444 !important; /* Dark background for inputs and dropdowns */
                color: white !important; /* White text for input fields */
            }

            /* Change hover effect in dark mode */
            tr:hover {
                background-color: #636363 !important;
            }

            /* Fix for "Show entries" and "Search" labels */
            .dataTables_wrapper .dataTables_length label,
            .dataTables_wrapper .dataTables_filter label {
                color: #bdbdbd !important; /* Ensure labels like "Show entries" and "Search" are white */
            }
        }
    </style>
</head>
<body style="margin:20px auto">
    <div class="container">
        <h1 style="padding:0; margin-top:0px"></h1>
        <table id="myTable" class="table table-striped">
            <thead>
                <tr>
"""

    # Add table headers dynamically
    for col in df.columns:
        html_content += f"                    <th>{col}</th>\n"
    html_content += "                </tr>\n"
    html_content += "            </thead>\n"
    html_content += "            <tbody>\n"

    # Iterate over DataFrame rows
    for _, row in df.iterrows():
        html_content += "                <tr>\n"
        for col in df.columns:
            html_content += f"                    <td>{row[col]}</td>\n"
        html_content += "                </tr>\n"

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    return html_content




# %% Dataframe to excel

def dataframe_to_excel_overwrites(
    df, out_file=None, sheet_name='df', index=False
):
    if out_file is None:
        out_file = Path(
            "C:/my_disk/____tmp/dataframe_to_excel.xlsx"
        )
    
    with pd.ExcelWriter(out_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=index, startrow=1, header=False)
        
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Set formats
        page_format = workbook.add_format({
            'bg_color': '#E0C9A6',
        })
        border_format = workbook.add_format({
            'border': 1,
            'border_color': '#50ABCD',
        })
        header_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'border_color': '#50ABCD',
            'bg_color': '#D4BC96',
            'align': 'left',
        })
        data_format = workbook.add_format({
            'bg_color': '#D4BC96',
            'border': 1,
            'border_color': '#50ABCD',
            'align': 'left',
        })
        
        # Apply page format to all cells
        worksheet.conditional_format(0, 0, len(df) + 1, len(df.columns) + (1 if index else 0), {
            'type': 'formula',
            'criteria': 'TRUE',
            'format': page_format,
        })
        
        # Write header with format
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num + (1 if index else 0), value, header_format)
        if index:
            worksheet.write(0, 0, df.index.name if df.index.name else '', header_format)
        
        # Format data cells
        for row_num, row in df.iterrows():
            if index:
                worksheet.write(row_num + 1, 0, row.name, data_format)
            for col_num, value in enumerate(row):
                worksheet.write(row_num + 1, col_num + (1 if index else 0), value, data_format)
        
        # Apply border format to all cells
        worksheet.conditional_format(0, 0, len(df) + 1, len(df.columns) + (1 if index else 0), {
            'type': 'formula',
            'criteria': 'TRUE',
            'format': border_format,
        })
        
        # Apply filter
        worksheet.autofilter(0, 0, len(df), len(df.columns) + (1 if index else 0) - 1)
        
        # Hide columns beyond the last column with data
        last_col_num = len(df.columns) + (1 if index else 0)
        worksheet.set_column(last_col_num, 16383, None, None, {'hidden': True})
        
        # Freeze top row
        worksheet.freeze_panes(1, 0)
        
        # Turn off gridlines
        worksheet.hide_gridlines(2)
        
        # Auto-adjust column width
        for idx, column in enumerate(df.columns):
            series = df[column]
            max_len = max(
                series.astype(str).map(len).max(),
                len(str(column))
            ) + 2  # Add some padding
            worksheet.set_column(idx + (1 if index else 0), idx + (1 if index else 0), max_len)
        
        if index:
            worksheet.set_column(0, 0, max(7, len(str(df.index.name)) + 2) if df.index.name else 7)
    
    open_file_folder(out_file)




def dataframe_to_excel(
    df, out_file=None, sheet_name='df', index=False
):
    if out_file is None:
        out_file = Path(
            "C:/my_disk/____tmp/dataframe_to_excel.xlsx"
        )
    
    out_file = Path(out_file)
    file_exists = out_file.exists()
    
    if file_exists:
        # Load existing workbook and add new sheet
        wb = openpyxl.load_workbook(out_file)
        
        # Remove sheet if it already exists
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]
        
        ws = wb.create_sheet(sheet_name)
        
        # Define styles
        header_fill = PatternFill(start_color='D4BC96', end_color='D4BC96', fill_type='solid')
        data_fill = PatternFill(start_color='D4BC96', end_color='D4BC96', fill_type='solid')
        page_fill = PatternFill(start_color='E0C9A6', end_color='E0C9A6', fill_type='solid')
        border_style = Border(
            left=Side(style='thin', color='50ABCD'),
            right=Side(style='thin', color='50ABCD'),
            top=Side(style='thin', color='50ABCD'),
            bottom=Side(style='thin', color='50ABCD')
        )
        
        # Apply page background
        for row in range(1, len(df) + 3):
            for col in range(1, len(df.columns) + 2):
                ws.cell(row, col).fill = page_fill
        
        # Write headers
        start_col = 2 if index else 1
        for col_num, value in enumerate(df.columns, start=start_col):
            cell = ws.cell(1, col_num, value)
            cell.font = Font(bold=True)
            cell.fill = header_fill
            cell.border = border_style
            cell.alignment = Alignment(horizontal='left')
        
        if index:
            cell = ws.cell(1, 1, df.index.name if df.index.name else '')
            cell.font = Font(bold=True)
            cell.fill = header_fill
            cell.border = border_style
            cell.alignment = Alignment(horizontal='left')
        
        # Write data
        for row_num, (idx_val, row) in enumerate(df.iterrows(), start=2):
            if index:
                cell = ws.cell(row_num, 1, idx_val)
                cell.fill = data_fill
                cell.border = border_style
                cell.alignment = Alignment(horizontal='left')
            
            for col_num, value in enumerate(row, start=start_col):
                cell = ws.cell(row_num, col_num, value)
                cell.fill = data_fill
                cell.border = border_style
                cell.alignment = Alignment(horizontal='left')
        
        # Apply autofilter
        ws.auto_filter.ref = ws.dimensions
        
        # Freeze top row
        ws.freeze_panes = 'A2'
        
        # Hide gridlines
        ws.sheet_view.showGridLines = False
        
        # Auto-adjust column widths
        for idx, column in enumerate(df.columns, start=start_col):
            series = df[column]
            max_len = max(
                series.astype(str).map(len).max(),
                len(str(column))
            ) + 2
            ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = max_len
        
        if index:
            ws.column_dimensions['A'].width = max(7, len(str(df.index.name)) + 2) if df.index.name else 7
        
        # Hide columns beyond the last column with data
        last_col_num = len(df.columns) + (1 if index else 0)
        for col_idx in range(last_col_num + 1, 16385):  # Excel max is 16384, so go up to and including 16384
            col_letter = openpyxl.utils.get_column_letter(col_idx)
            ws.column_dimensions[col_letter].hidden = True
        
        wb.save(out_file)
        
    else:
        # Create new workbook with xlsxwriter (original code)
        with pd.ExcelWriter(out_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index, startrow=1, header=False)
            
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Set formats
            page_format = workbook.add_format({
                'bg_color': '#E0C9A6',
            })
            border_format = workbook.add_format({
                'border': 1,
                'border_color': '#50ABCD',
            })
            header_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'border_color': '#50ABCD',
                'bg_color': '#D4BC96',
                'align': 'left',
            })
            data_format = workbook.add_format({
                'bg_color': '#D4BC96',
                'border': 1,
                'border_color': '#50ABCD',
                'align': 'left',
            })
            
            # Apply page format to all cells
            worksheet.conditional_format(0, 0, len(df) + 1, len(df.columns) + (1 if index else 0), {
                'type': 'formula',
                'criteria': 'TRUE',
                'format': page_format,
            })
            
            # Write header with format
            for col_num, value in enumerate(df.columns):
                worksheet.write(0, col_num + (1 if index else 0), value, header_format)
            if index:
                worksheet.write(0, 0, df.index.name if df.index.name else '', header_format)
            
            # Format data cells
            for row_num, row in df.iterrows():
                if index:
                    worksheet.write(row_num + 1, 0, row.name, data_format)
                for col_num, value in enumerate(row):
                    worksheet.write(row_num + 1, col_num + (1 if index else 0), value, data_format)
            
            # Apply border format to all cells
            worksheet.conditional_format(0, 0, len(df) + 1, len(df.columns) + (1 if index else 0), {
                'type': 'formula',
                'criteria': 'TRUE',
                'format': border_format,
            })
            
            # Apply filter
            worksheet.autofilter(0, 0, len(df), len(df.columns) + (1 if index else 0) - 1)
            
            # Hide columns beyond the last column with data
            last_col_num = len(df.columns) + (1 if index else 0)
            worksheet.set_column(last_col_num, 16383, None, None, {'hidden': True})
            
            # Freeze top row
            worksheet.freeze_panes(1, 0)
            
            # Turn off gridlines
            worksheet.hide_gridlines(2)
            
            # Auto-adjust column width
            for idx, column in enumerate(df.columns):
                series = df[column]
                max_len = max(
                    series.astype(str).map(len).max(),
                    len(str(column))
                ) + 2
                worksheet.set_column(idx + (1 if index else 0), idx + (1 if index else 0), max_len)
            
            if index:
                worksheet.set_column(0, 0, max(7, len(str(df.index.name)) + 2) if df.index.name else 7)
    
    open_file_folder(out_file)
