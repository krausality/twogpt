import argparse
import json
import os
import fnmatch
import re
from dir_tree import DirectoryTree
import shutil  # For copying the global config

class FileCollector:
    def __init__(self, root_dir='.', global_config=False, permanent=False):
        """
        Initialize the FileCollector with a given root directory.
        If global_config is True, work with the global config file. Otherwise, use the local config if it exists.
        If the local config doesn't exist and permanent changes are requested, create it.
        """
        self.root_dir = root_dir
        self.global_config = global_config
        self.permanent = permanent  # Whether a permanent change is being made
        
        if self.global_config or (not self.local_config_exists() and not self.permanent):
            # Use the global config if explicitly requested or if no local config exists and no permanent change
            self.config = self.load_global_config()
        else:
            # Use local config if it exists, or create it when a permanent change is requested
            self.config = self.load_local_config()

        # Settings from the configuration file
        self.output_file = self.config.get("output_file", "allfiles.txt")
        self.ignore_file = self.config.get("ignore_file", ".gptignore")
        self.include_files = self.config.get("include_files", [])
        self.exclude_files = set(self.config.get("exclude_files", []))
        self.exclude_dirs = set(self.config.get("exclude_dirs", []))

        # Exclude specific files (self-exclusion)
        self.exclude_files.add(self.output_file)
        self.exclude_files.add(self.ignore_file)

        # Parse .gptignore to gather additional exclusion patterns
        self.gptignore_patterns = self.parse_gptignore()
        
        # Classify .gptignore patterns into directories and files
        self._classify_gptignore_patterns()

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
            with open(local_config_path, 'r') as f:
                config = {'include_files': [], 'exclude_files': []}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if line.startswith('include:'):
                            config['include_files'].append(line.split(':', 1)[1].strip())
                        elif line.startswith('exclude:'):
                            config['exclude_files'].append(line.split(':', 1)[1].strip())
                return config
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
            for pattern in self.include_files:
                f.write(f"include: {pattern}\n")
            for pattern in self.exclude_files:
                f.write(f"exclude: {pattern}\n")
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
            if self.global_config:
                self.config['include_files'].append(pattern)
                self.save_global_config()
            else:
                self.save_local_config()

    def remove_include(self, pattern, permanent=False):
        """Remove a file pattern from the include list."""
        if pattern in self.include_files:
            self.include_files.remove(pattern)
        if permanent:
            if self.global_config:
                if pattern in self.config['include_files']:
                    self.config['include_files'].remove(pattern)
                self.save_global_config()
            else:
                self.save_local_config()

    def add_exclude(self, pattern, permanent=False):
        """Add a file pattern to the exclude list."""
        self.exclude_files.add(pattern)
        if permanent:
            if self.global_config:
                self.config['exclude_files'].append(pattern)
                self.save_global_config()
            else:
                self.save_local_config()

    def remove_exclude(self, pattern, permanent=False):
        """Remove a file pattern from the exclude list."""
        if pattern in self.exclude_files:
            self.exclude_files.remove(pattern)
        if permanent:
            if self.global_config:
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

    def parse_gptignore(self):
        """Parse the .gptignore file to get exclusion patterns."""
        gptignore_file = os.path.join(self.root_dir, '.gptignore')
        patterns = []
        if os.path.exists(gptignore_file):
            with open(gptignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Ignore empty lines and comments
                        patterns.append(line)
        return patterns

    def _classify_gptignore_patterns(self):
        """Classify .gptignore patterns into directories and files."""
        for pattern in self.gptignore_patterns:
            if pattern.endswith('/'):
                self.exclude_dirs.add(pattern.rstrip('/'))
            else:
                self.exclude_files.add(pattern)

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

    # Determine whether we're using the global config or local config
    collector = FileCollector(root_dir=".", global_config=args.global_config, permanent=args.permanent)

    if args.command == "include":
        collector.add_include(args.pattern, permanent=args.permanent)
    elif args.command == "exclude":
        collector.add_exclude(args.pattern, permanent=args.permanent)
    elif args.command == "remove-include":
        collector.remove_include(args.pattern, permanent=args.permanent)
    elif args.command == "remove-exclude":
        collector.remove_exclude(args.pattern, permanent=args.permanent)
    elif args.command == "list-includes":
        collector.list_includes()
    elif args.command == "list-excludes":
        collector.list_excludes()

    collector.run()

if __name__ == "__main__":
    main()
