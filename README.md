```markdown
# dir_tree

`dir_tree` is a Python package that generates a directory tree structure in JSON format, with customizable options to exclude certain directories and files. It can be used as both a library in your Python projects and as a command-line tool.

## Features

- **Directory Tree Generation**: Generate a visual and JSON representation of a directory structure.
- **Exclusion Options**: Exclude specific directories and files or file patterns.
- **Preferences Management**: Save and load preferences for exclusions.
- **Command-Line Interface**: Use the tool directly from the command line.

## Installation

You can install the `dir_tree` package locally by cloning the repository and running:

```bash
pip install .
```

## Usage

### As a Python Library

You can use the `dir_tree` package in your Python scripts:

```python
from dir_tree import DirectoryTree, Preferences

# Initialize preferences
prefs = Preferences()
prefs.update_preferences(exclude_dirs=["env", "venv"], exclude_files=["*.log"])
prefs.save_preferences()  # Optionally save preferences for later use

# Generate directory tree
tree = DirectoryTree(root_dir="path/to/directory", exclude_dirs=prefs.prefs["EXCLUDE_DIRS"], exclude_files=prefs.prefs["EXCLUDE_FILES"])
print(tree.to_json())
```

### Command-Line Interface (CLI)

After installing the package, you can use the `dir-tree` command in your terminal.

#### Basic Usage

Generate a directory tree starting from the current directory:

```bash
dir-tree
```

Specify a different directory:

```bash
dir-tree --dir /path/to/directory
```

#### Excluding Directories and Files

Exclude specific directories:

```bash
dir-tree --exclude-dir env venv node_modules
```

Exclude specific files or file patterns:

```bash
dir-tree --exclude-file "*.log" "*.tmp"
```

#### Saving and Loading Preferences

Save the current exclusions as preferences:

```bash
dir-tree --exclude-dir env venv --exclude-file "*.log" --save-prefs
```

Load previously saved preferences:

```bash
dir-tree --load-prefs
```

### JSON Output

The JSON output contains the following fields:

- **`root`**: The name of the root directory.
- **`tree`**: The directory structure as a nested dictionary.
- **`tree_print`**: A visual representation of the directory tree in text form.
- **`excluded_dirs`**: A list of directories that were excluded.
- **`excluded_files`**: A list of files or file patterns that were excluded.

Example JSON output:

```json
{
    "root": "example",
    "tree": {
        ".gptignore": null,
        "8_fileA.file": null,
        "8_fileA.jpg": null,
        "8_fileA.txt": null,
        "allfiles.txt": null,
        "exclude1": {
            "1_fileA.file": null,
            "1_fileA.jpg": null,
            "1_fileA.txt": null
        },
        "exclude2": {
            "2_fileC.file": null,
            "2_fileC.jpg": null,
            "2_fileC.txt": null,
            "sub_folder_ex2": {
                "5_fileC.txt": null
            }
        },
        "keep1": {
            "3_fileA.file": null,
            "3_fileA.jpg": null,
            "3_fileA.txt": null,
            "sub_folder_k1": {
                "4_fileB.file": null,
                "4_fileB.jpg": null,
                "4_fileB.txt": null
            }
        },
        "keep2": {
            "6_fileA.file": null,
            "6_fileA.jpg": null,
            "6_fileA.txt": null,
            "sub_folder_k2": {
                "7_fileA.file": null,
                "7_fileA.jpg": null,
                "7_fileA.txt": null
            }
        },
        "print_tree_dir.py": null
    },
    "tree_print": "example\n├── .gptignore\n├── 8_fileA.file\n├── 8_fileA.jpg\n├── 8_fileA.txt\n├── allfiles.txt\n├── exclude1\n│   ├── 1_fileA.file\n│   ├── 1_fileA.jpg\n│   └── 1_fileA.txt\n├── exclude2\n│   ├── 2_fileC.file\n│   ├── 2_fileC.jpg\n│   ├── 2_fileC.txt\n│   └── sub_folder_ex2\n│       └── 5_fileC.txt\n├── keep1\n│   ├── 3_fileA.file\n│   ├── 3_fileA.jpg\n│   ├── 3_fileA.txt\n│   └── sub_folder_k1\n│       ├── 4_fileB.file\n│       ├── 4_fileB.jpg\n│       └── 4_fileB.txt\n├── keep2\n│   ├── 6_fileA.file\n│   ├── 6_fileA.jpg\n│   ├── 6_fileA.txt\n│   └── sub_folder_k2\n│       ├── 7_fileA.file\n│       ├── 7_fileA.jpg\n│       └── 7_fileA.txt\n└── print_tree_dir.py",
    "excluded_dirs": [
        "env",
        "__pycache__",
        "node_modules",
        ".expo",
        ".idea",
        "venv",
        "dist",
        ".git",
        "build"
    ],
    "excluded_files": [
        "*.log",
        "LICENSE"
    ]
}
```

## Development

If you want to contribute or make changes to this package, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/dir_tree.git
    cd dir_tree
    ```

2. **Install the package in editable mode**:
    ```bash
    pip install -e .
    ```

3. **Run tests and make changes**:
    - You can create tests to verify the functionality and make sure everything works as expected.

4. **Submit a pull request**:
    - Feel free to fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or suggestions, please feel free to reach out to me at `your.email@example.com`.

---

Happy coding!
```

### Key Sections:

1. **Introduction**: Overview of the package.
2. **Features**: Highlight key features.
3. **Installation**: Instructions to install the package locally.
4. **Usage**: Demonstrates how to use the package as a library and via CLI.
5. **JSON Output**: Example of what the output looks like.
6. **Development**: Steps for contributing or making changes.
7. **License**: Information about the license.
8. **Contact**: How users can reach you for support or suggestions.

This `README.md` provides comprehensive documentation to help users understand, install, and use your package effectively.