# %% Operating system

## Dependencies
import os
import subprocess
from pathlib import Path
import shutil
from datetime import datetime
import re


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


def drop_all_files_in_a_folder(unc, chmod_value=0o777):
    """
    Deletes all files and subdirectories within a given directory.

    Args:
        unc: Path to the directory to be emptied.
        chmod_value: Octal value for changing file/directory permissions before deletion.
                     Default is 0o777 (read, write, execute for all).

    Raises:
        OSError: If an error occurs during file or directory deletion.
    """

    for root, dirs, files in os.walk(unc, topdown=False):
        for f in files:
            file_path = os.path.join(root, f)
            try:
                os.chmod(file_path, chmod_value)
                os.remove(file_path)
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")

        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                os.chmod(dir_path, chmod_value)
                shutil.rmtree(dir_path)
            except OSError as e:
                print(f"Error deleting directory {dir_path}: {e}")


if __name__ == "__main__":
    try:
        drop_all_files_in_a_folder("path/to/your/folder")
    except OSError as e:
        print(f"Error deleting files: {e}")


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


def get_latest_file(directory, start_string, ext):
    try:
        # Get a list of files with the prefix 'explore'
        files = [
            f
            for f in os.listdir(directory)
            if f.startswith(start_string) and f.endswith(ext)
        ]

        if not files:
            print("No files found with the prefix 'explore' and .xlsm extension.")
            return None

        # Parse the timestamp from each filename and find the latest one
        latest_file = max(
            files,
            key=lambda f: datetime.strptime(
                re.search(r"\d{8}_\d{4}", f).group(), "%Y%m%d_%H%M"
            ),
        )

        return os.path.join(directory, latest_file)

    except FileNotFoundError:
        print(f"Directory '{directory}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def open_file_folder(path=None):
    if path is None:
        path = os.getcwd()

    path_adj = f'explorer "{path}"'
    subprocess.Popen(path_adj)


def rename_files(folder_path, prefix=None, suffix=None):
    """Rename files in a folder"""
    # List all files in the folder
    files = os.listdir(folder_path)

    # Iterate through each file
    for file_name in files:
        # Construct the new file name with prefix and/or suffix
        new_name = ""

        if prefix:
            new_name += prefix

        new_name += file_name

        if suffix:
            new_name += suffix

        # Create the full paths for old and new file names
        old_path = os.path.join(folder_path, file_name)
        new_path = os.path.join(folder_path, new_name)

        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed: {file_name} -> {new_name}")


if __name__ == "__main__":
    folder_path = "/path/to/your/folder"
    prefix = "new_"
    suffix = "_v1"

    rename_files(r"C:\Users\Ashut\Downloads", prefix=prefix)


def visualize_directory_tree_full(unc):
    from pathlib import Path
    import subprocess as sp

    class DisplayablePath(object):
        display_filename_prefix_middle = "┣━"
        display_filename_prefix_last = "┗━"
        display_parent_prefix_middle = "    "
        display_parent_prefix_last = "┃   "

        def __init__(self, path, parent_path, is_last):
            self.path = Path(str(path))
            self.parent = parent_path
            self.is_last = is_last
            if self.parent:
                self.depth = self.parent.depth + 1
            else:
                self.depth = 0

        @property
        def displayname(self):
            if self.path.is_dir():
                return self.path.name + "/"
            return self.path.name

        @classmethod
        def make_tree(cls, root, parent=None, is_last=False, criteria=None):
            root = Path(str(root))
            criteria = criteria or cls._default_criteria

            displayable_root = cls(root, parent, is_last)
            yield displayable_root

            children = sorted(
                list(path for path in root.iterdir() if criteria(path)),
                key=lambda s: str(s).lower(),
            )
            count = 1
            for path in children:
                is_last = count == len(children)
                if path.is_dir():
                    yield from cls.make_tree(
                        path,
                        parent=displayable_root,
                        is_last=is_last,
                        criteria=criteria,
                    )
                else:
                    yield cls(path, displayable_root, is_last)
                count += 1

        @classmethod
        def _default_criteria(cls, path):
            return True

        @property
        def displayname(self):
            if self.path.is_dir():
                return self.path.name + "/"
            return self.path.name

        def displayable(self):
            if self.parent is None:
                return self.displayname

            _filename_prefix = (
                self.display_filename_prefix_last
                if self.is_last
                else self.display_filename_prefix_middle
            )

            parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

            parent = self.parent
            while parent and parent.parent is not None:
                parts.append(
                    self.display_parent_prefix_middle
                    if parent.is_last
                    else self.display_parent_prefix_last
                )
                parent = parent.parent

            return "".join(reversed(parts))

    # default run
    paths = DisplayablePath.make_tree(Path(unc))

    # export
    paths = DisplayablePath.make_tree(Path(unc))
    with open(r"directory_tree.txt", "w", encoding="utf-8") as f:
        for path in paths:
            # print(path.displayable())
            f.write(str(path.displayable()) + "\n")
            print(path.displayable())

    # open
    sp.Popen('explorer "directory_tree.txt"')


if __name__ == "__main__":
    visualize_directory_tree(_ao)


# %% Upto folder level


def visualize_directory_tree_levels(unc, max_depth=None):
    from pathlib import Path
    import subprocess as sp

    class DisplayablePath(object):
        display_filename_prefix_middle = "┣━"
        display_filename_prefix_last = "┗━"
        display_parent_prefix_middle = "    "
        display_parent_prefix_last = "┃   "

        def __init__(self, path, parent_path, is_last):
            self.path = Path(str(path))
            self.parent = parent_path
            self.is_last = is_last
            if self.parent:
                self.depth = self.parent.depth + 1
            else:
                self.depth = 0

        @property
        def displayname(self):
            if self.path.is_dir():
                return self.path.name + "/"
            return self.path.name

        @classmethod
        def make_tree(
            cls, root, parent=None, is_last=False, criteria=None, max_depth=None
        ):
            root = Path(str(root))
            criteria = criteria or cls._default_criteria

            displayable_root = cls(root, parent, is_last)
            yield displayable_root

            # Check if we've reached the maximum depth
            if max_depth is not None and displayable_root.depth >= max_depth:
                return

            children = sorted(
                list(path for path in root.iterdir() if criteria(path)),
                key=lambda s: str(s).lower(),
            )
            count = 1
            for path in children:
                is_last = count == len(children)
                if path.is_dir():
                    yield from cls.make_tree(
                        path,
                        parent=displayable_root,
                        is_last=is_last,
                        criteria=criteria,
                        max_depth=max_depth,
                    )
                else:
                    yield cls(path, displayable_root, is_last)
                count += 1

        @classmethod
        def _default_criteria(cls, path):
            return True

        def displayable(self):
            if self.parent is None:
                return self.displayname

            _filename_prefix = (
                self.display_filename_prefix_last
                if self.is_last
                else self.display_filename_prefix_middle
            )

            parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

            parent = self.parent
            while parent and parent.parent is not None:
                parts.append(
                    self.display_parent_prefix_middle
                    if parent.is_last
                    else self.display_parent_prefix_last
                )
                parent = parent.parent

            return "".join(reversed(parts))

    # default run with max_depth parameter
    paths = DisplayablePath.make_tree(Path(unc), max_depth=max_depth)

    # export
    with open(r"directory_tree.txt", "w", encoding="utf-8") as f:
        for path in paths:
            f.write(str(path.displayable()) + "\n")
            print(path.displayable())

    # open
    sp.Popen('explorer "directory_tree.txt"')


if __name__ == "__main__":
    visualize_directory_tree_levels(_ao, max_depth=1)
