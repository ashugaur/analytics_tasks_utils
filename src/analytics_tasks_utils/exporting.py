# %% Export functions

## Dependencies
import zipfile
import os
from datetime import datetime
import shutil


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


# %% convert_color_excel_csv_to_html_md_mkdocs_data_table


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


# %% Abbreviations


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
