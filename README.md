WIP.... COming soon

<!-- # OSHSH — Ola's Simple HDL Source Handler

**OSHSH** is a lightweight command-line tool to manage and organize HDL (Verilog/VHDL) source files based on module manifests.

It scans your project directory for `manifest.json` files, resolves dependencies, and outputs ordered lists of source files for easy compilation.

---

## 🚀 Features
- 🔍 Auto-discovers HDL module manifests.
- 📂 Resolves module dependencies recursively.
- 📝 Generates ordered source file lists for Verilog and VHDL.
- ⚡ Simple command-line interface.
- 🐍 Pure Python, no external dependencies.

---

## 📦 Installation

Install via `pip`:

```bash
pip install oshsh
```

Or clone and install locally:

```bash
git clone https://github.com/olagrottvik/oshsh.git
cd oshsh
pip install .
```

---

## ⚡ Usage

### Basic Command

```bash
oshsh [OPTIONS] module_name
```

OSHSH will:
1. Search for all `manifest.json` files starting from the specified top directory.
2. Resolve dependencies for the given `module_name`.
3. Generate ordered lists of Verilog and VHDL source files for each library.
4. Save the lists as `<lib_name>_verilog.src` and `<lib_name>_vhdl.src` in the output directory.

---

### 📖 Options

| Option                  | Description                                                                                   | Default                     |
|-------------------------|-----------------------------------------------------------------------------------------------|-----------------------------|
| `-t`, `--top-dir`       | Path to the project top-level directory. Searches for manifests starting here.                 | Current working directory   |
| `-w`, `--work`          | Name of the work library.                                                                     | `work`                      |
| `-o`, `--output`        | Output directory where source list files will be written.                                      | Current working directory   |
| `-h`, `--help`          | Show help message and exit.                                                                   |                             |

---

### 🎯 Example

```bash
oshsh -t /home/user/hdl_project -w mylib -o ./src_lists top_module
```

This will:
- Search `/home/user/hdl_project` for `manifest.json` files.
- Treat `top_module` as the top-level module.
- Use `mylib` as the work library name.
- Output ordered source lists in the `./src_lists` directory.

---

### 📂 Output Example

After running, you might get:

```
src_lists/
├── mylib_verilog.src
└── mylib_vhdl.src
```

Each `.src` file contains the absolute paths to your source files in the correct compilation order.

---

## 📄 Manifest File Format

Each module requires a `manifest.json`. Example:

```json
{
  "module": "alu",
  "sources": [
    "alu_core.v",
    "alu_control.vhd"
  ],
  "dependencies": {
    "work": ["adder", "multiplier"],
    "math_lib": ["sqrt_module"]
  }
}
```

- `"module"`: Name of the module.
- `"sources"`: List of HDL source files relative to the manifest.
- `"dependencies"`: Other modules this one depends on, grouped by library.

---

## 🛠️ Development

```bash
git clone https://github.com/olagrottvik/oshsh.git
cd oshsh
pip install -e .
```

Run locally:

```bash
oshsh --help
```

---

## 📃 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributions

Feel free to open issues or submit pull requests!
Bug fixes, improvements, and suggestions are always welcome.

---

## 👤 Author

**Ola Grottvik**
[GitHub](https://github.com/olagrottvik) -->