import sys
import os
import json
import yaml
import textwrap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLineEdit, QLabel, QRadioButton, QFileDialog,
    QMessageBox, QButtonGroup, QCheckBox
)
from PyQt6.QtCore import Qt


class FileCollectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_folders = []
        self.excluded_folders = ["node_modules", "vendor", ".git", ".idea", ".github", ".husky", ".vscode", ".archive", ".cypress", ".git", ".github", ".husky", ".idea", ".scaffoldes", ".storybook", ".vscode", "build", "dist", "node_modules", "public", "vendor"]
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Folder Selection
        folder_selection_layout = QHBoxLayout()
        self.folder_list = QListWidget()
        add_folder_button = QPushButton("Add Folder")
        add_folder_button.clicked.connect(self.add_folder)
        remove_folder_button = QPushButton("Remove Selected")
        remove_folder_button.clicked.connect(self.remove_selected_folder)
        folder_selection_layout.addWidget(self.folder_list)
        folder_selection_layout.addWidget(add_folder_button)
        folder_selection_layout.addWidget(remove_folder_button)
        layout.addLayout(folder_selection_layout)

        # File Types
        file_types_layout = QHBoxLayout()
        file_types_label = QLabel("File Types (comma-separated):")
        self.file_types_input = QLineEdit()
        file_types_layout.addWidget(file_types_label)
        file_types_layout.addWidget(self.file_types_input)
        layout.addLayout(file_types_layout)

        # Excluded Folders
        exclusion_layout = QHBoxLayout()
        exclusion_label = QLabel("Excluded Folders (comma-separated):")
        self.exclusion_input = QLineEdit(','.join(self.excluded_folders))
        exclusion_layout.addWidget(exclusion_label)
        exclusion_layout.addWidget(self.exclusion_input)
        layout.addLayout(exclusion_layout)

        # Export Type
        export_type_layout = QHBoxLayout()
        self.export_type_group = QButtonGroup(self)
        self.plain_text_radio = QRadioButton("Plain Text")
        self.json_radio = QRadioButton("JSON")
        self.yaml_radio = QRadioButton("YAML")
        self.jsonl_radio = QRadioButton("JSONL")
        self.export_type_group.addButton(self.plain_text_radio)
        self.export_type_group.addButton(self.json_radio)
        self.export_type_group.addButton(self.yaml_radio)
        self.export_type_group.addButton(self.jsonl_radio)
        export_type_layout.addWidget(self.plain_text_radio)
        export_type_layout.addWidget(self.json_radio)
        export_type_layout.addWidget(self.yaml_radio)
        export_type_layout.addWidget(self.jsonl_radio)
        layout.addLayout(export_type_layout)

        # Minify Content
        self.minify_checkbox = QCheckBox("Minify Content")
        layout.addWidget(self.minify_checkbox)

        # Action Buttons
        action_layout = QHBoxLayout()
        collect_button = QPushButton("Collect and Save")
        collect_button.clicked.connect(self.collect_and_save)
        action_layout.addWidget(collect_button)
        layout.addLayout(action_layout)

        self.setLayout(layout)
        self.setWindowTitle('File Collector')
        self.setGeometry(100, 100, 800, 400)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selected_folders.append(folder)
            self.folder_list.addItem(folder)

    def remove_selected_folder(self):
        selected_items = self.folder_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.selected_folders.remove(item.text())
            self.folder_list.takeItem(self.folder_list.row(item))

    def collect_and_save(self):
        file_types = [ftype.strip() for ftype in self.file_types_input.text().split(',')]
        excluded_folders = [efolder.strip() for efolder in self.exclusion_input.text().split(',')]
        export_type = self.get_export_type()

        if not export_type:
            QMessageBox.warning(self, "No Export Type Selected", "Please select an export type.")
            return

        collected_content = self.collect_file_contents(self.selected_folders, file_types, excluded_folders)

        if not collected_content:
            QMessageBox.warning(self, "No Content Collected", "No content collected based on the specified criteria.")
            return

        if self.minify_checkbox.isChecked():
            collected_content = self.minify_content(collected_content)

        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", self.get_file_extension(export_type))

        if save_path:
            self.save_content(collected_content, save_path, export_type)
            QMessageBox.information(self, "Save Successful", f"Content saved successfully to {save_path}")

    def get_export_type(self):
        if self.plain_text_radio.isChecked():
            return 'plain_text'
        elif self.json_radio.isChecked():
            return 'json'
        elif self.yaml_radio.isChecked():
            return 'yaml'
        elif self.jsonl_radio.isChecked():
            return 'jsonl'
        return None

    def get_file_extension(self, export_type):
        if export_type == 'plain_text':
            return "Text Files (*.txt)"
        elif export_type == 'json':
            return "JSON Files (*.json)"
        elif export_type == 'yaml':
            return "YAML Files (*.yaml)"
        elif export_type == 'jsonl':
            return "JSONL Files (*.jsonl)"
        return ""

    def collect_file_contents(self, folders, file_types, excluded_folders):
        collected_content = {}
        for folder in folders:
            for root, dirs, files in os.walk(folder):
                dirs[:] = [d for d in dirs if d not in excluded_folders]
                for file in files:
                    if any(file.endswith(ftype) for ftype in file_types):
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r') as f:
                                collected_content[file_path] = f.read()
                        except Exception as e:
                            QMessageBox.warning(self, "Error Reading File", f"Could not read file {file}: {str(e)}")
        return collected_content

    def minify_content(self, content):
        minified_content = {}
        for path, text in content.items():
            minified_content[path] = textwrap.dedent(text).replace('\n', ' ').replace('\r', ' ').strip()
        return minified_content

    def save_content(self, content, path, export_type):
        try:
            if export_type == 'plain_text':
                with open(path, 'w') as f:
                    for file_path, file_content in content.items():
                        f.write(f"{file_path}: {file_content}\n")
            elif export_type == 'json':
                with open(path, 'w') as f:
                    json.dump(content, f, indent=4)
            elif export_type == 'yaml':
                with open(path, 'w') as f:
                    yaml.dump(content, f)
            elif export_type == 'jsonl':
                with open(path, 'w') as f:
                    for file_path, file_content in content.items():
                        f.write(json.dumps({file_path: file_content}) + '\n')
        except Exception as e:
            QMessageBox.warning(self, "Error Saving File", f"Could not save file: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileCollectorApp()
    ex.show()
    sys.exit(app.exec())
