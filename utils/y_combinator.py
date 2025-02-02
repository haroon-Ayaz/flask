import os


def generate_directory_tree(root_dir, indent='', last=True, is_root=True):
    """
    Recursively generates a directory tree structure with proper indentation and formatting.
    """
    if is_root:
        print(f'└── {os.path.basename(root_dir)}/')
        is_root = False
    else:
        print(f'{indent}{"└── " if last else "├── "}{os.path.basename(root_dir)}'
              f'{"/" if os.path.isdir(root_dir) else ""}')

    if not os.path.isdir(root_dir):
        return

    entries = sorted(os.listdir(root_dir), key=lambda x: (not os.path.isdir(os.path.join(root_dir, x)), x))
    entries = [os.path.join(root_dir, entry) for entry in entries]

    for index, entry in enumerate(entries):
        if os.path.basename(entry) in ['.venv', '']:  # Add folders to ignore here
            continue
        is_last = index == len(entries) - 1
        new_indent = indent + ('    ' if last else '│   ')
        generate_directory_tree(entry, new_indent, is_last, False)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python tree_generator.py <directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"Error: '{target_dir}' is not a valid directory")
        sys.exit(1)

    generate_directory_tree(target_dir)