import argparse
import json
import os
import fnmatch
import re
from dir_tree import DirectoryTree
import shutil  # For copying the global config

class FileCollector:
    def __init__(self, root_dir='.', use_global_config=False, permanent=False):
        """
        Initialize the FileCollector with a given root directory.
        If use_global_config is True, work with the global config file. Otherwise, use the local config if it exists.
        If the local config doesn't exist and permanent changes are requested, create it.
        """
        self.root_dir = root_dir
        self.use_global_config = use_global_config
        self.permanent = permanent  # Whether a permanent change is being made

        """
        If ""2gpt ... " and no local config not exits 
        """
        if ((not self.use_global_config) and (not self.local_config_exists())):
            if self.permanent:
                self.config = self.load_local_config() #creating and loading local config
            else:
                self.config = self.load_global_config() #loading global config


        #If 2gpt ...  and local config exits 
        elif ((not self.use_global_config) and self.local_config_exists()):
            if self.permanent:
                self.config = self.load_local_config() #creating and loading local config
            else:
                self.config = self.load_local_config() #loading global config

        #2gpt ... --global-config
        elif self.use_global_config:
            if self.permanent:
                self.config = self.load_local_config() #creating and loading local config
            else:
                self.config = self.load_global_config() #loading global config

        else:
            pass


        # trashs the unpermanent includes/excludes by restoring the includes/excludes
        # from the permanent config. Should be used after each run.
        # if the FileCollector Object is continously used.
        self.reload_settings_from_permanent_config()

    def reload_settings_from_permanent_config(self):
        # Settings from the configuration file
        self.output_file = self.config.get("output_file", "allfiles.txt")
        self.ignore_file = self.config.get("ignore_file", ".gptignore")
        self.include_files = self.config.get("include_files", [])
        self.exclude_files = set(self.config.get("exclude_files", []))
        self.exclude_dirs = set(self.config.get("exclude_dirs", []))

        # Exclude specific files (self-exclusion)
        self.exclude_files.add(self.output_file)
        self.exclude_files.add(self.ignore_file)

    def local_config_exists(self):
        """Check if the local .gptignore config exists."""
        local_config_path = os.path.join(self.root_dir, '.gptignore')
        return os.path.exists(local_config_path)

    def load_global_config(self):
        """Load the global configuration from the package's config.json file."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if not os.path.exists(config_path):
            print(f"Global configuration file not found at {config_path}, using default settings.")
            return {}
        with open(config_path, 'r') as config_file:
            return json.load(config_file)

    def load_local_config(self):
        """Load the local .gptignore configuration or create it from the global config if not present."""
        local_config_path = os.path.join(self.root_dir, '.gptignore')
        global_config_path = os.path.join(os.path.dirname(__file__), 'config.json')

        if os.path.exists(local_config_path):
            # Load existing local config
            with open(local_config_path, 'r') as config_file:
                return json.load(config_file)
        elif self.permanent:
            # If no local config exists and a permanent change is being made, copy from the global config
            print(f"Local .gptignore not found. Creating from global config for permanent changes.")
            shutil.copy(global_config_path, local_config_path)
            return self.load_global_config()
        else:
            # Use global config temporarily if no local config exists and no permanent changes are requested
            return self.load_global_config()

    def save_local_config(self):
        """Save the local .gptignore configuration."""
        local_config_path = os.path.join(self.root_dir, '.gptignore')
        with open(local_config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
        print(f"Local configuration saved to {local_config_path}.")

    def save_global_config(self):
        """Save the global configuration to config.json."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)
        print(f"Global configuration saved to {config_path}.")

    def add_include(self, pattern, permanent=False):
        """Add a file pattern to the include list."""
        self.include_files.append(pattern)
        if permanent:
            self.config['include_files'].append(pattern)
            if self.use_global_config:
                self.save_global_config()
            else:
                self.save_local_config()


    def remove_include(self, pattern, permanent=False):
        """Remove a file pattern from the include list."""
        if pattern in self.include_files:
            self.include_files.remove(pattern)
        if permanent:
            if self.use_global_config:
                if pattern in self.config['include_files']:
                    self.config['include_files'].remove(pattern)
                self.save_global_config()
            else:
                self.save_local_config()

    def add_exclude(self, pattern, permanent=False):
        """Add a file pattern to the exclude list."""
        self.exclude_files.add(pattern)
        if permanent:
            self.config['exclude_files'].append(pattern)
            if self.use_global_config:
                self.save_global_config()
            else:
                self.save_local_config()



    def remove_exclude(self, pattern, permanent=False):
        """Remove a file pattern from the exclude list."""
        if pattern in self.exclude_files:
            self.exclude_files.remove(pattern)
        if permanent:
            if self.use_global_config:
                if pattern in self.config['exclude_files']:
                    self.config['exclude_files'].remove(pattern)
                self.save_global_config()
            else:
                self.save_local_config()

    def list_includes(self):
        """List all the include file patterns."""
        print("Currently included files:")
        for pattern in self.include_files:
            print(f"  {pattern}")

    def list_excludes(self):
        """List all the exclude file patterns."""
        print("Currently excluded files:")
        for pattern in self.exclude_files:
            print(f"  {pattern}")


    def generate_tree(self):
        """Generate the directory tree and write it to the output file."""
        tree = DirectoryTree(root_dir=self.root_dir, exclude_dirs=self.exclude_dirs, exclude_files=self.exclude_files)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("File Structure:\n")
            f.write(json.loads(tree.to_json())["tree_print"])
            f.write("\n\n")

    def collect_files(self):
        """Collect files based on inclusion and exclusion patterns."""
        include_patterns = self._compile_patterns(self.include_files)
        exclude_patterns = self._compile_patterns(list(self.exclude_files))
        print(f"Include patterns: {include_patterns}")  # Debugging line
        print(f"Exclude patterns: {exclude_patterns}")  # Debugging line

        with open(self.output_file, 'a') as f:
            for root, dirs, files in os.walk(self.root_dir):
                print(f"Walking directory: {root}")  # Debugging line
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs and not any(fnmatch.fnmatch(d, pattern) for pattern in self.exclude_dirs)]
                for file in files:
                    print(f"Processing file: {file}")  # Debugging line
                    if any(re.match(pattern, file) for pattern in include_patterns) and not any(re.match(pattern, file) for pattern in exclude_patterns):
                        file_path = os.path.join(root, file)
                        print(f"Including file for content collection: {file_path}")
                        self._append_file_content(f, file_path)

    def _compile_patterns(self, patterns):
        """Compile wildcard patterns into regular expressions."""
        return [fnmatch.translate(pattern) for pattern in patterns]

    def _append_file_content(self, file, file_path):
        """Append file content to the output."""
        print(f"Attempting to append content from: {file_path}")  # Debugging line
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                if not content:
                    print(f"File {file_path} is empty or unreadable.")
                else:
                    print(f"Read content from {file_path}: {content[:100]}")  # First 100 chars of content
                    file.write(f"----- START OF {file_path} -----\n")
                    file.write(content)
                    file.write(f"\n----- END OF {file_path} -----\n\n\n")
        except Exception as e:
            print(f"Error appending content from {file_path}: {e}")

    def run(self):
        """Run the file collection process."""
        self.generate_tree()
        self.collect_files()
        #self.reload_settings_from_permanent_config()

def main():
    parser = argparse.ArgumentParser(description="FileCollector CLI to manage file inclusion and exclusion.")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
   
    # Add global config option
    parser.add_argument('--global-config', action='store_true', help='Apply changes to the global config instead of the local config.')

    # Add subcommand for including files
    include_parser = subparsers.add_parser("include", help="Add a file or directory to the include list.")
    include_parser.add_argument("pattern", help="Pattern to include (e.g., '*.py').")
    include_parser.add_argument("--permanent", action="store_true", help="Make the inclusion permanent.")

    # Add subcommand for excluding files
    exclude_parser = subparsers.add_parser("exclude", help="Add a file or directory to the exclude list.")
    exclude_parser.add_argument("pattern", help="Pattern to exclude (e.g., '*.png').")
    exclude_parser.add_argument("--permanent", action="store_true", help="Make the exclusion permanent.")

    # Add subcommand for removing from include list
    remove_include_parser = subparsers.add_parser("remove-include", help="Remove a file from the include list.")
    remove_include_parser.add_argument("pattern", help="Pattern to remove from include list.")
    remove_include_parser.add_argument("--permanent", action="store_true", help="Remove permanently from config.")

    # Add subcommand for removing from exclude list
    remove_exclude_parser = subparsers.add_parser("remove-exclude", help="Remove a file from the exclude list.")
    remove_exclude_parser.add_argument("pattern", help="Pattern to remove from exclude list.")
    remove_exclude_parser.add_argument("--permanent", action="store_true", help="Remove permanently from config.")

    # Add subcommand for listing includes and excludes
    subparsers.add_parser("list-includes", help="List all permanently included files.")
    subparsers.add_parser("list-excludes", help="List all permanently excluded files.")

    args = parser.parse_args()

    # Determine whether we're using the global config
    global_config = args.global_config if hasattr(args, 'global_config') else False
    permanent = args.permanent if hasattr(args, 'permanent') else False

    # Initialize the collector
    collector = FileCollector(root_dir=".", use_global_config=global_config, permanent=permanent)

    if args.command in ["include", "exclude", "remove-include", "remove-exclude"]:
        if args.command == "include":
            collector.add_include(args.pattern, permanent=permanent)
        elif args.command == "exclude":
            collector.add_exclude(args.pattern, permanent=permanent)
        elif args.command == "remove-include":
            collector.remove_include(args.pattern, permanent=permanent)
        elif args.command == "remove-exclude":
            collector.remove_exclude(args.pattern, permanent=permanent)
    elif args.command == "list-includes":
        collector.list_includes()
    elif args.command == "list-excludes":
        collector.list_excludes()
    else:
        # If no command is provided, just run the collector
        collector.run()

    
if __name__ == "__main__":
    main()


"""
2gpt

Lokale config wird ausgelesen falls sie exististiert 
Falls lokale config nicht existiert. Globale config auslesen.
Einen run starten mit determinierter config.


2gpt include "file.py"

Lokale config wird ausgelesen falls sie exististiert 
Falls lokale config nicht existiert. Globale config auslesen.

file.py wird nur für den direkt folgenden run included, config files bleiben unverändert.
Einen run starten mit determinierter config.


2gpt include "file.py" --permanent

Lokale config wird ausgelesen falls sie exististiert 
Falls lokale config nicht existiert. Globale config auslesen und als .gptignore in
das jeweilig rootverzeichnis abspeichern.
Dann die include "file.py" operation auf der configdatei durschführen, sodass "file.py" jetzt permanent und für
erstmal alle zukünftigen runs included ist.

2gpt include "file.py" --permanent --global-config

Lokale config wird ignoriert
Globale config auslesen.
Dann die include "file.py" operation auf der globalen configdatei durchführen, sodass "file.py" jetzt permanent
und für alle zukünftigen runs included ist, welche die globale config nutzen müssen.


Einen run starten mit determinierter config.


Globale config wird nur ausgelesen fall "--global-config" als parameter, dann egal ob lokale existiert

Perm



---------------------


To implement the desired behavior for the **CLI tool** with local and global configuration management for `include`, `exclude`, `list-includes`, `list-excludes`, and `remove` functionality, here’s how the CLI should behave for each command:

### Overall Workflow for Local and Global Configurations:

1. **Default Run (`2gpt`)**:
    - **Local config is used** if it exists.
    - **If local config does not exist**, the global config is used.
    - Perform the run with the determined config (local or global).

2. **Temporary Include (`2gpt include "file.py"`)**:
    - **Local config is used** if it exists.
    - **If local config does not exist**, the global config is used.
    - Include the file `file.py` for this run temporarily (the config files remain unchanged).
    - Start a run with the determined config and the temporary include.

3. **Permanent Include Locally (`2gpt include "file.py" --permanent`)**:
    - **Local config is used** if it exists.
    - **If local config does not exist**, the global config is copied to a new local `.gptignore` file.
    - Modify the local config to include `file.py` permanently.
    - Start a run with the modified local config.

4. **Permanent Include Globally (`2gpt include "file.py" --permanent --global-config`)**:
    - **Local config is ignored**.
    - **Global config is used**.
    - Modify the global config to include `file.py` permanently.
    - Start a run with the modified global config.

---

### Adding `exclude`, `list-includes`, `list-excludes`, and `remove` Functionality:

1. **Temporary Exclude (`2gpt exclude "file.py"`)**:
    - **Local config is used** if it exists.
    - **If local config does not exist**, the global config is used.
    - Exclude the file `file.py` for this run temporarily (the config files remain unchanged).
    - Start a run with the determined config and the temporary exclusion.

2. **Permanent Exclude Locally (`2gpt exclude "file.py" --permanent`)**:
    - **Local config is used** if it exists.
    - **If local config does not exist**, the global config is copied to a new local `.gptignore` file.
    - Modify the local config to exclude `file.py` permanently.
    - Start a run with the modified local config.

3. **Permanent Exclude Globally (`2gpt exclude "file.py" --permanent --global-config`)**:
    - **Local config is ignored**.
    - **Global config is used**.
    - Modify the global config to exclude `file.py` permanently.
    - Start a run with the modified global config.

4. **List Includes (`2gpt list-includes`)**:
    - **Local config is used** if it exists.
    - **If local config does not exist**, the global config is used.
    - List all files or patterns that are included in the config.

5. **List Includes Globally (`2gpt list-includes --global-config`)**:
    - **Local config is ignored**.
    - **Global config is used**.
    - List all files or patterns that are included in the global config.

6. **List Excludes (`2gpt list-excludes`)**:
    - **Local config is used** if it exists.
    - **If local config does not exist**, the global config is used.
    - List all files or patterns that are excluded in the config.

7. **List Excludes Globally (`2gpt list-excludes --global-config`)**:
    - **Local config is ignored**.
    - **Global config is used**.
    - List all files or patterns that are excluded in the global config.

8. **Remove Include/Exclude Locally (`2gpt remove-include "file.py"` or `2gpt remove-exclude "file.py"`)**:
    - **Local config is used** if it exists.
    - **If local config does not exist**, the global config is used.
    - Remove the specified file or pattern (`file.py`) from the inclusion/exclusion list.
    - If the file is removed temporarily, the config remains unchanged.
    - **If `--permanent` is specified**, the change is applied permanently to the local config.

9. **Remove Include/Exclude Globally (`2gpt remove-include "file.py" --permanent --global-config` or `2gpt remove-exclude "file.py" --permanent --global-config`)**:
    - **Local config is ignored**.
    - **Global config is used**.
    - Remove the specified file or pattern (`file.py`) from the inclusion/exclusion list in the global config permanently.

---

### Command Breakdown:

#### 1. **Default Run (`2gpt`)**:
- **Local config** is used if it exists. If not, the **global config** is used.
- Executes a run based on the configuration.

#### 2. **Include**:
- `2gpt include "file.py"`:
    - Temporarily includes `file.py` for the next run without modifying the config files.

- `2gpt include "file.py" --permanent`:
    - Modifies the **local config** permanently to include `file.py`. If no local config exists, the global config is copied to the local `.gptignore`.

- `2gpt include "file.py" --permanent --global-config`:
    - Modifies the **global config** permanently to include `file.py`. The local config is ignored.

#### 3. **Exclude**:
- `2gpt exclude "file.py"`:
    - Temporarily excludes `file.py` for the next run without modifying the config files.

- `2gpt exclude "file.py" --permanent`:
    - Modifies the **local config** permanently to exclude `file.py`. If no local config exists, the global config is copied to the local `.gptignore`.

- `2gpt exclude "file.py" --permanent --global-config`:
    - Modifies the **global config** permanently to exclude `file.py`. The local config is ignored.

#### 4. **List Includes**:
- `2gpt list-includes`:
    - Lists all files or patterns included in the **local config** (if it exists) or the **global config**.

- `2gpt list-includes --global-config`:
    - Lists all files or patterns included in the **global config**.

#### 5. **List Excludes**:
- `2gpt list-excludes`:
    - Lists all files or patterns excluded in the **local config** (if it exists) or the **global config**.

- `2gpt list-excludes --global-config`:
    - Lists all files or patterns excluded in the **global config**.

#### 6. **Remove Include/Exclude**:
- `2gpt remove-include "file.py"` or `2gpt remove-exclude "file.py"`:
    - Removes `file.py` from the inclusion/exclusion list temporarily (no permanent config changes).

- `2gpt remove-include "file.py" --permanent` or `2gpt remove-exclude "file.py" --permanent`:
    - Permanently removes `file.py` from the **local config**.

- `2gpt remove-include "file.py" --permanent --global-config` or `2gpt remove-exclude "file.py" --permanent --global-config`:
    - Permanently removes `file.py` from the **global config**, ignoring the local config.

---

### Example Workflows:

1. **Run with Default Configuration**:
    ```bash
    2gpt
    ```

2. **Temporarily Include a File**:
    ```bash
    2gpt include "file.py"
    ```

3. **Permanently Include a File Locally**:
    ```bash
    2gpt include "file.py" --permanent
    ```

4. **Permanently Include a File Globally**:
    ```bash
    2gpt include "file.py" --permanent --global-config
    ```

5. **List Includes in Local Config**:
    ```bash
    2gpt list-includes
    ```

6. **List Includes in Global Config**:
    ```bash
    2gpt list-includes --global-config
    ```

7. **Remove a File from Local Exclude List Permanently**:
    ```bash
    2gpt remove-exclude "file.py" --permanent
    ```

8. **Remove a File from Global Include List Permanently**:
    ```bash
    2gpt remove-include "file.py" --permanent --global-config
    ```

---

This description covers the complete behavior for `include`, `exclude`, `list-includes`, `list-excludes`, and `remove` operations with local and global configurations, using the `--permanent` and `--global-config` flags where appropriate.

"""
