# pylint: disable=logging-fstring-interpolation missing-function-docstring line-too-long

import argparse
import pathlib

from .core import run


def main():
    cwd = pathlib.Path.cwd()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ola's Simple HDL Source Handler")
    parser.add_argument(
        "-t",
        "--top-dir",
        default=cwd,
        help="Path to the project top-level directory. Used as base for searching for manifest files. Default is the current working directory.",
    )
    parser.add_argument(
        "module", help="The name of the module that is treated as the top-level."
    )
    parser.add_argument(
        "-w",
        "--work",
        default="work",
        help="The name of the work library. Default is 'work'.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=cwd,
        help="Output directory for the source file lists. For each library, a file is created with the list of source files in order. Default is the current working directory.",
    )
    args = parser.parse_args()

    run(args, cwd)
