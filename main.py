import sys
import os
import json
import yaml
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QLineEdit, QCheckBox, QFormLayout, QListWidget, QListWidgetItem
from FileMinifier import FileMinifier

class DirectoryScanner:
    def __init__(self, folder_path, minify=False, file_formats=None, regex_pattern=None, exclusions=None, ignore_content=False, ignore_hidden_folders=False):
        self.folder_path = folder_path
        self.minify = minify
        self.file_formats = file_formats if file_formats else []
        self.regex_pattern = regex_pattern
        self.exclusions = exclusions if exclusions else []
        self.ignore_content = ignore_content
        self.ignore_hidden_folders = ignore_hidden_folders

    def scan_directory(self):
        return self._scan(self.folder_path)

    def _scan(self, path):
        contents = []
        try:
            for entry in os.scandir(path):
                if self._is_excluded(entry.path) or (self.ignore_hidden_folders and self._is_hidden(entry.path)):
                    continue
                relative_path = os.path.relpath(entry.path, self.folder_path)
                if entry.is_dir(follow_symlinks=False):
                    folder_contents = self._scan(entry.path)  # Recursive call
                    contents.append({
                        "type": "folder",
                        "name": entry.name,
                        "path": relative_path,
                        "contents": folder_contents
                    })
                elif entry.is_file(follow_symlinks=False) and self._matches_filter(entry):
                    file_content = None
                    if not self.ignore_content:
                        with open(entry.path, 'r', errors='ignore') as file:
                            file_content = file.read()
                            if self.minify:
                                file_content = FileMinifier.minify_content(file_content)

                    if not self.ignore_content:
                        contents.append({
                            "type": "file",
                            "filename": entry.name,
                            "path": relative_path,
                            "filecontent": file_content
                        })
                    else:
                        contents.append({
                            "type": "file",
                            "filename": entry.name,
                            "path": relative_path
                        })
        except PermissionError:
            pass
        return contents

    def _matches_filter(self, entry):
        if self.file_formats and not any(entry.name.endswith(f'.{fmt}') for fmt in self.file_formats):
            return False
        if self.regex_pattern and not re.search(self.regex_pattern, entry.name):
            return False
        return True

    def _is_excluded(self, path):
        return any(exclusion in path for exclusion in self.exclusions)

    def _is_hidden(self, path):
        return os.path.basename(path).startswith('.')

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Advanced File and Folder Exporter'
        self.initUI()
        self.folder_path = None
        self.scanner = None

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 600, 300)
        layout = QFormLayout()

        btn_select = QPushButton('Select Folder', self)
        btn_select.clicked.connect(self.showFolderDialog)
        layout.addRow("Select Folder:", btn_select)

        self.file_format_list = QListWidget(self)
        self.file_format_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for format in ["txt", "py", "js", "json", "yaml"]:
            QListWidgetItem(format, self.file_format_list)
        layout.addRow("File Formats (optional):", self.file_format_list)

        self.regex_line = QLineEdit(self)
        self.regex_line.setPlaceholderText("Enter regex pattern (optional)")
        layout.addRow("Regex Pattern (optional):", self.regex_line)

        self.exclude_line = QLineEdit(self)
        predefined_exclusions =["node_modules", "vendor",".git", ",".github",".vscode", ".idea"]
        self.exclude_line.setText(", ".join(predefined_exclusions))
        layout.addRow("Additional Exclusions (optional):", self.exclude_line)

        self.minify_checkbox = QCheckBox("Minify content", self)
        layout.addRow(self.minify_checkbox)

        self.ignore_content_checkbox = QCheckBox("Ignore content", self)
        layout.addRow(self.ignore_content_checkbox)

        self.ignore_hidden_folders_checkbox = QCheckBox("Ignore hidden folders", self)
        layout.addRow(self.ignore_hidden_folders_checkbox)

        self.export_json_button = QPushButton('Export to JSON', self)
        self.export_json_button.clicked.connect(self.exportToJson)
        layout.addRow(self.export_json_button)

        self.export_yaml_button = QPushButton('Export to YAML', self)
        self.export_yaml_button.clicked.connect(self.exportToYAML)
        layout.addRow(self.export_yaml_button)

        self.export_txt_button = QPushButton('Export to TXT', self)
        self.export_txt_button.clicked.connect(self.exportToTxt)
        layout.addRow(self.export_txt_button)

        self.setLayout(layout)
        self.show()

    def showFolderDialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path = folder_path

    def exportToJson(self):
        self.exportToFile('json')

    def exportToYAML(self):
        self.exportToFile('yaml')

    def exportToTxt(self):
        self.exportToFile('txt')

    def exportToFile(self, file_type):
        if self.folder_path:
            file_formats = [item.text() for item in self.file_format_list.selectedItems()]
            file_path = QFileDialog.getSaveFileName(self, f"Save {file_type.upper()} File", "", f"{file_type.upper()} files (*.{file_type})")[0]
            if file_path:
                exclusions = [exclusion.strip() for exclusion in self.exclude_line.text().split(',')] if self.exclude_line.text() else []
                self.scanner = DirectoryScanner(self.folder_path, minify=self.minify_checkbox.isChecked(),
                                                file_formats=file_formats,
                                                regex_pattern=self.regex_line.text() or None,
                                                exclusions=exclusions,
                                                ignore_content=self.ignore_content_checkbox.isChecked(),
                                                ignore_hidden_folders=self.ignore_hidden_folders_checkbox.isChecked())
                data = self.scanner.scan_directory()
                with open(file_path, 'w', encoding='utf-8') as file:
                    if file_type == 'json':
                        json.dump(data, file, separators=(',', ':')) if self.minify_checkbox.isChecked() else json.dump(data, file, indent=4)
                    elif file_type == 'yaml':
                        yaml.dump(data, file, allow_unicode=True)
                    else:  # Text export
                        for item in data:
                            file.write(f"{item['type']}: {item['name']}\n")
                QMessageBox.information(self, "Export Successful", f"The files and folders have been exported to {file_type.upper()}.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())
