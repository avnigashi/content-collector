# File Collector

File Collector is a PyQt6-based desktop application for collecting, filtering, and exporting file contents from multiple directories.

![Content Collector Screenshot](https://raw.githubusercontent.com/avnigashi/content-collector/main/screen.png)

## Features

- Select multiple folders for scanning
- Filter files by type
- Exclude specific folders
- Minify content option
- Export as Plain Text, JSON, YAML, or JSONL
- User-friendly PyQt6 interface
- Error handling with user feedback

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

2. Use the interface to:
   - Add folders to scan
   - Specify file types
   - Customize excluded folders
   - Choose export format
   - Toggle content minification

3. Click "Collect and Save" to export the collected content.

## Project Structure

- `main.py`: Main application file
- `FileMinifier.py`: Utility for content minification
- `requirements.txt`: Required Python packages
- `run.sh`: Setup and run script
