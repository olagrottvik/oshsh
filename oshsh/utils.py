# pylint: disable=logging-fstring-interpolation missing-function-docstring line-too-long

import pathlib
import logging

logger = logging.getLogger(__name__)

EXIT_SUCCESS = 0
EXIT_UNEXPECTED_ERROR = 1
EXIT_FILE_ERROR = 2
EXIT_JSON_ERROR = 3
EXIT_MODULE_NOT_FOUND = 4
EXIT_INVALID_TOP_DIR = 5
EXIT_MANIFEST_NOT_FOUND = 6
EXIT_MISSING_FILES = 7

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