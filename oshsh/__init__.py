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