# %% Create functions

## Dependencies
import os
import subprocess as sp

## Dataframes for testing


## mkdocs_build
def mkdocs_build(path, tool=None):
    """Build mkdocs static site.

    Options: tool='uv | pip', default 'uv'
    """

    print("Running: MkDocs build (defaults to uv)...")
    os.chdir(path)

    if tool == "pip":
        print("Using pip may be compartively slower than uv (default).")
        sp.check_output(
            "powershell -Executionpolicy ByPass -command python -m mkdocs build"
        )
    else:
        sp.check_output(
            "powershell -Executionpolicy ByPass -command uv run mkdocs build"
        )


# %% mkdocs build dirty


## Dirty build
def mkdocs_build_dirty(path, tool=None):
    """Build mkdocs static site with latest partial updates.

    Options: tool='uv | pip', default 'uv'
    """

    print("Running: MkDocs dirty build (defaults to uv)...")
    os.chdir(path.replace("\\", "/"))

    if tool == "pip":
        print("Using pip may be compartively slower than uv (default).")
        sp.check_output(
            "powershell -Executionpolicy ByPass -command uv run mkdocs build --dirty"
        )
