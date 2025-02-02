import os
from pathlib import Path


def find_and_combine_files(file_list, search_dir, output_file):
    # Convert to Path objects for better handling
    search_path = Path(search_dir)
    output_path = Path(output_file)

    # Create or clear the output file
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write("")  # Initialize empty file

    found_files = 0

    # Walk through directory tree
    for root, dirs, files in os.walk(search_path):
        dirs[:] = [d for d in dirs if d not in {'.venv', '__pycache__'}]

        for file in files:
            if file in file_list:
                file_path = Path(root) / file
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as in_f:
                        content = in_f.read()

                    # Write to output file
                    with open(output_path, 'a', encoding='utf-8') as out_f:
                        out_f.write(f"\n\n{'=' * 40}\n")
                        out_f.write(f"FILE: {file_path}\n")
                        out_f.write(f"{'=' * 40}\n\n")
                        out_f.write(content)

                    found_files += 1
                    print(f"Processed: {file_path}")

                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

    print(f"\nOperation complete. Found and processed {found_files} files.")
    print(f"Output saved to: {output_path.absolute()}")


if __name__ == "__main__":
    # Configuration
    TARGET_FILES = [  # Add your file names here
        'settings.py',
        'urls.py',
        'models.py',
        'views.py',
        'manage.py'
    ]

    SEARCH_DIRECTORY = r"D:\Projects\NHS\backend"
    OUTPUT_FILE = "output.txt"

    # Run the operation
    find_and_combine_files(TARGET_FILES, SEARCH_DIRECTORY, OUTPUT_FILE)