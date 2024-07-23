# Advanced File Collector

Advanced File Collector is a PyQt6-based desktop application for collecting, filtering, previewing, and exporting file contents from multiple directories or GitHub repositories.

![Advanced File Collector Screenshot](https://raw.githubusercontent.com/avnigashi/content-collector/main/screen.png)

## Features

- Select multiple folders for scanning
- Download files from GitHub repositories
- Filter files by type
- Exclude specific folders
- Preview collected files before export
- Minify content option
- Export as Plain Text, JSON, YAML, or JSONL
- Save and load profiles for different project types
- User-friendly PyQt6 interface with tabbed layout
- Progress tracking for file collection and GitHub downloads
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
   - Add folders to scan or download GitHub repositories
   - Specify file types to include
   - Customize excluded folders
   - Save and load profiles for different project types
   - Choose export format
   - Toggle content minification

3. Click "Collect" to gather files based on your settings.

4. Use the "Generate Preview" button to review collected files before exporting.

5. Click "Export" to save the collected content in your chosen format.

## New Features

- **GitHub Integration**: Download files directly from GitHub repositories.
- **Preview Functionality**: Generate and view a preview of collected files before exporting.
- **Tabbed Interface**: Easily switch between file list and preview views.
- **Profile Management**: Save and load settings for different project types.
- **Progress Tracking**: Visual feedback for file collection and GitHub download progress.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
