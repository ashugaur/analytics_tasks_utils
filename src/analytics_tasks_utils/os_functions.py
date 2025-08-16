# %% Operating system

## Dependencies
import os
import subprocess
from pathlib import Path
import shutil


## open_file_folder
def open_file_folder(path):
    path_adj = "explorer " + '"' + str(path) + '"'
    subprocess.Popen(path_adj)


def get_downloads_folder():
    """
    Automatically runs to get the downloads folder directory.
    Run <_download> to know the folder path.
    """
    # Get the user's home directory
    home_dir = str(Path.home())

    # Check the common download folder names on different operating systems
    download_folders = ["Downloads", "My Documents", "Documents"]

    # Iterate through the possible download folders and return the first one that exists
    for folder in download_folders:
        downloads_path = os.path.join(home_dir, folder)
        if os.path.exists(downloads_path):
            return downloads_path

    # If none of the common folders exist, return the user's home directory
    return home_dir


if __name__ == "__main__":
    _download_dir = get_downloads_folder()
    print("\n_download_dir:", _download_dir)


# %% Copy


## Copy files and subfolders without overwriting
def copy_folders(source, destination):
    try:
        # Ensure the destination directory exists
        if not os.path.exists(destination):
            os.makedirs(destination)

        # Copy each item from source to destination
        for item in os.listdir(source):
            s = os.path.join(source, item)
            d = os.path.join(destination, item)
            if os.path.isdir(s):
                # Recursively copy directories
                if os.path.exists(d):
                    copy_folders(s, d)
                else:
                    shutil.copytree(s, d)
            else:
                # Copy files if they don't exist in the destination
                if not os.path.exists(d):
                    shutil.copy2(s, d)

        print(
            f"\ncopy_folders() does not overrite files.\nSuccessfully copied from {source} to {destination}."
        )
    except Exception as e:
        print(f"Error copying from {source} to {destination}: {e}")


## Copy and overwrite files and folders
def copy_folders_overwrite(source, destination):
    try:
        # Ensure the destination directory exists
        if not os.path.exists(destination):
            os.makedirs(destination)

        # Copy each item from source to destination
        for item in os.listdir(source):
            s = os.path.join(source, item)
            d = os.path.join(destination, item)
            if os.path.isdir(s):
                # Recursively copy directories
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                # Copy files
                shutil.copy2(s, d)

        print(f"Successfully copied from {source} to {destination}")
    except Exception as e:
        print(f"Error copying from {source} to {destination}: {e}")


## Copy multiple files to a folder and overwrite
def copy_multiple_files(source_files, destination):
    """
    Copies multiple files from different locations to a destination folder.

    Args:
        source_files (list): List of source file paths to copy
        destination_folder (str): Path to destination folder

    Returns:
        int: Number of files successfully copied
    """
    # Create destination folder if it doesn't exist
    os.makedirs(destination, exist_ok=True)

    copied_count = 0

    for source_file in source_files:
        try:
            # Get the base filename
            filename = os.path.basename(source_file)
            destination_path = os.path.join(destination, filename)

            # Copy file (this will overwrite if exists)
            shutil.copy2(source_file, destination_path)
            copied_count += 1
            print(f"Copied: {source_file} -> {destination_path}")

        except Exception as e:
            print(f"Error copying {source_file}: {str(e)}")

    return copied_count
