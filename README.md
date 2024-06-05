# File Collector

File Collector is a desktop application built using PyQt6 that allows users to collect, filter, and save file contents from multiple directories. It provides customizable options for file types and folder exclusions and supports exporting the collected content in various formats, including Plain Text, JSON, YAML, and JSONL.

## Features

- **Select Folders:** Choose multiple folders to scan for files.
- **Specify File Types:** Filter files to be read based on specified file extensions.
- **Exclude Specific Folders:** Pre-fill and customize a list of folders to exclude from the scan.
- **Minify Content:** Option to compress the file content by removing extra whitespace and newlines.
- **Export Formats:** Save the collected content as Plain Text, JSON, YAML, or JSONL.
- **User-Friendly Interface:** Built using PyQt6 for a modern and responsive UI.
- **Error Handling:** Graceful handling of potential errors with user feedback via message boxes.

## Installation

### Prerequisites

- Python 3.x
- Pip (Python package installer)

### Steps

1. Clone the repository:

    ```sh
    git clone https://github.com/avnigashi/content-collector.git
    cd content-collector
    ```

2. Run the setup script:

    ```sh
    ./run.sh
    ```

## Usage

1. Run the application:

    ```sh
    ./run.sh
    ```

2. The application window will appear.

3. Use the "Add Folder" button to select folders you want to scan.

4. Specify the file types you want to read (comma-separated, e.g., `.txt, .py, .md`).

5. Customize the list of excluded folders if needed.

6. Choose the export type (Plain Text, JSON, YAML, or JSONL).

7. Optionally, check the "Minify Content" checkbox to compress the file content.

8. Click the "Collect and Save" button.

9. Select the save location and file name in the file dialog that appears.

10. The collected content will be saved to the specified file.

## Project Structure

- **main.py**: The main application file that contains the PyQt6 UI and logic for collecting and saving file contents.
- **FileMinifier.py**: A utility class for minifying file content by removing comments and unnecessary whitespace.
- **requirements.txt**: A file listing the required Python packages for the project.
- **run.sh**: A shell script to install dependencies and run the application.
