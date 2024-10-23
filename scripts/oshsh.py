"""Ola's Simple HDL Source Handler  (OSHSH)

Extract list of source files in correct order based on module manifests.
Search project directory for all module manifests and extract list of source files in correct order based on module manifests.
Can return list of source files in order for compilation, based on definition of top-level module name.

Example manifest file (manifest.json):

{
"module": "module_name",
"sources": [
    "source1.v",
    "source2.v",
    "source3.v"
],

"dependencies": {
    "work": ["module1", "module2"],
    "lib_name": ["module3"]
}
}
"""

import argparse
import pathlib
import logging
import json

logger = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation missing-function-docstring line-too-long

valid_verilog_endings = [".v", ".sv", ".svp"]
valid_vhdl_endings = [".vhd", ".vhdl", ".vo"]


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
    module = args.module
    top_dir = args.top_dir
    work = args.work

    # Create a logger object
    configure_logging()

    # if top-level is relative path, make it absolute?
    ensure_abs_path(cwd, top_dir)

    # Check if top-level is a directory and exists
    if not validate_top_dir(top_dir):
        error_message = f"The specified top-level directory {top_dir} does not exist or is not a directory."
        logger.error(error_message)
        exit(5)

    # Find all files named "manifest.json" in the current working directory
    all_manifest_files = discover_manifests(top_dir)

    # parse all manifest files
    manifest_data = []
    for manifest_file in all_manifest_files:
        try:
            with open(manifest_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                data["manifest_path"] = str(manifest_file.resolve())
                manifest_data.append(data)
                logger.debug(f"Parsed manifest file: {manifest_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {manifest_file}: {e}")
            exit(3)
        except (OSError, IOError) as e:
            logger.error(f"File error reading {manifest_file}: {e}")
            exit(2)
        except Exception as e:
            logger.error(f"Unexpected error reading {manifest_file}: {e}")
            exit(1)

    # Check if the specified module is found within the list of manifests
    module_found = False
    top_manifest = None
    for manifest in manifest_data:
        if manifest.get("module") == module:
            module_found = True
            top_manifest = manifest

    if not module_found:
        error_message = f"The specified module {module} was not found in any manifest."
        logger.error(error_message)
        exit(4)
    else:
        logger.info(f"Found module {module} in manifest.")

    # Extract dependencies recursively
    dependencies = extract_dependencies(manifest_data, top_manifest, work)

    # Remove duplicate entries
    dependencies = list(dict.fromkeys(dependencies))
    logger.debug(f"Dependencies for module {module}: {dependencies}")

    # Append the top manifest module with the work library to the dependencies list
    dependencies.append((work, module))

    logger.info(f"Complete module list: {dependencies}")

    # Extract source file list from all modules in the final dependencies list
    source_files_by_lib = {}
    for lib_name, module in dependencies:
        # Separate Verilog and VHDL files
        verilog_sources = []
        vhdl_sources = []

        # Find the manifest for the module
        manifest = next((m for m in manifest_data if m.get("module") == module), None)
        if manifest:
            manifest_path = pathlib.Path(manifest["manifest_path"]).parent
            sources = [
                str(manifest_path / source) for source in manifest.get("sources", [])
            ]
            for source in sources:

                if any(source.endswith(ext) for ext in valid_verilog_endings):
                    verilog_sources.append(source)
                elif any(source.endswith(ext) for ext in valid_vhdl_endings):
                    vhdl_sources.append(source)

            # If the library already exists in the source_files_by_lib dictionary, append the source files
            if lib_name in source_files_by_lib:
                source_files_by_lib[lib_name]["verilog"].extend(verilog_sources)
                source_files_by_lib[lib_name]["vhdl"].extend(vhdl_sources)
            else:  # Otherwise, create a new entry in the dictionary and add the source files
                source_files_by_lib[lib_name] = {
                    "verilog": verilog_sources,
                    "vhdl": vhdl_sources,
                }
        else:
            logger.error(f"Manifest for module {module} not found.")
            exit(6)

    # Remove duplicate source files while preserving order within each library
    for lib_name, sources in source_files_by_lib.items():
        sources["verilog"] = list(dict.fromkeys(sources["verilog"]))
        sources["vhdl"] = list(dict.fromkeys(sources["vhdl"]))
        logger.debug(
            f"Source files for library {lib_name}: Verilog: {sources['verilog']}, VHDL: {sources['vhdl']}"
        )

    # Check that all source files exist
    missing_files = []
    for lib_name, source_files in source_files_by_lib.items():
        for source_file in source_files["verilog"] + source_files["vhdl"]:
            if not pathlib.Path(source_file).exists():
                missing_files.append(source_file)

    if missing_files:
        error_message = f"The following source files do not exist: {missing_files}"
        logger.error(error_message)
        exit(7)

    # Print the final source file list for each library in order
    for lib_name, source_files in source_files_by_lib.items():
        print(f"Verilog sources for library {lib_name}:")
        for source_file in source_files["verilog"]:
            print(f"  {source_file}")

        print(f"VHDL sources for library {lib_name}:")
        for source_file in source_files["vhdl"]:
            print(f"  {source_file}")

    # Write the source files to output files, one file per library
    output_dir = pathlib.Path(args.output)
    for lib_name, source_files in source_files_by_lib.items():
        verilog_output_file = output_dir / f"{lib_name}_verilog.src"
        vhdl_output_file = output_dir / f"{lib_name}_vhdl.src"

        if source_files["verilog"]:
            with open(verilog_output_file, "w", encoding="utf-8") as f:
                for source_file in source_files["verilog"]:
                    f.write(f"{source_file}\n")
            logger.info(
                f"Wrote Verilog source files for library {lib_name} to {verilog_output_file}"
            )
        else:
            logger.info(
                f"No Verilog source files for library {lib_name}, skipping file creation."
            )

        if source_files["vhdl"]:
            with open(vhdl_output_file, "w", encoding="utf-8") as f:
                for source_file in source_files["vhdl"]:
                    f.write(f"{source_file}\n")
            logger.info(
                f"Wrote VHDL source files for library {lib_name} to {vhdl_output_file}"
            )
        else:
            logger.info(
                f"No VHDL source files for library {lib_name}, skipping file creation."
            )


def extract_dependencies(manifest_data, top_manifest, work):
    def _extract(manifest, collected_deps, current_work):
        logger.debug(f"Extracting dependencies for {manifest.get('module')}")

        deps = manifest.get("dependencies", {}).items()

        for lib_name, modules in deps:
            # Replace 'work' with the current_work
            if lib_name == "work":
                lib_name = current_work
            for module in modules:
                if (lib_name, module) not in collected_deps:
                    logger.debug(
                        f"Processing dependency {module} in library {lib_name}"
                    )

                    dep_tuple = (lib_name, module)

                    if dep_tuple not in collected_deps:  # Avoid circular dependencies
                        # Find the manifest for the dependency module
                        dep_manifest = next(
                            (m for m in manifest_data if m.get("module") == module),
                            None,
                        )
                        if dep_manifest:
                            _extract(dep_manifest, collected_deps, lib_name)

                    collected_deps.append(dep_tuple)

    collected_deps = []
    _extract(top_manifest, collected_deps, work)
    return collected_deps


def validate_top_dir(top_dir):
    if pathlib.Path(top_dir).is_dir():
        return True
    return False


def ensure_abs_path(cwd, top_dir):
    if not pathlib.Path(top_dir).is_absolute():
        top_dir = (cwd / top_dir).resolve()


def configure_logging():
    logger = logging.getLogger(__name__)

    # Set the logging level to INFO
    logger.setLevel(logging.DEBUG)

    # Create a formatter with a nice formatting
    formatter = logging.Formatter("oshsh - %(levelname)s - %(message)s")

    # Create a file handler to log to a file
    file_handler = logging.FileHandler("debug.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a console handler to log to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add the file handler and console handler to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def discover_manifests(top_dir):

    logger.info(f"Discovering manifest files in {top_dir}")
    manifests = pathlib.Path(top_dir).rglob("manifest*.json")
    manifest_files = list(manifests)
    for manifest in manifest_files:
        logger.info(f"Found manifest file: {manifest}")
    return manifest_files


if __name__ == "__main__":
    main()
