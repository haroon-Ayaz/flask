from pathlib import Path
import argparse, os

def find_and_combine_files(file_list, search_dir, output_file, process_all=False):  # MODIFIED: Add process_all parameter
    # If file_list is None or empty, process all files in the directory
    process_all = not file_list  # True when file_list is None or an empty list

    search_path = Path(search_dir)
    output_path = Path(output_file)

    # Create or clear the output file
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write("")
    
    found_files = 0

    # Walk through directory tree
    for root, dirs, files in os.walk(search_path):
        dirs[:] = [d for d in dirs if d not in {'.venv', '__pycache__'}]
        for file in files:
            if process_all or file in file_list:  # Process file if in file_list or if processing all files
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as in_f:
                        content = in_f.read()
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
    # Mode 1: Process only specified file names
    TARGET_FILES = [
        'settings.py',
        'urls.py',
        'models.py',
        'views.py',
        'manage.py'
    ]

    # Mode 2: Process every file under the directory
    # Uncomment the following line and comment out TARGET_FILES if you want to process all files.
    TARGET_FILES = None

    SEARCH_DIRECTORY = r"D:\Projects\NHS\frontend\src\app\updates"
    OUTPUT_FILE = "output.txt"

    find_and_combine_files(TARGET_FILES, SEARCH_DIRECTORY, OUTPUT_FILE)