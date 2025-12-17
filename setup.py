from setuptools import setup, Extension
from Cython.Build import cythonize
import os
import re

# Collect all Python files to compile, excluding migrations, backups, and invalid files
def find_py_files(directory):
    py_files = []
    for root, _, files in os.walk(directory):
        # Exclude directories with invalid names (e.g., containing hyphens)
        if "-" in root:
            continue
        for file in files:
            if file.endswith(".py") and file != "manage.py":  # Exclude manage.py if needed
                # Exclude migration files, backup files, and files with invalid names
                if "migrations" in root or "bckup" in root or " - Copy" in file:
                    continue
                # Exclude files with invalid module names (e.g., containing hyphens)
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*\.py$", file):
                    continue
                py_files.append(os.path.join(root, file))
    return py_files

# List of all Python files in the project
py_files = find_py_files(".")

# Define extensions for Cython
extensions = [
    Extension(
        os.path.splitext(os.path.relpath(file, "."))[0].replace(os.sep, "."),
        [file]
    )
    for file in py_files
]

# Setup configuration
setup(
    name="watchcase_tracker",
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
)