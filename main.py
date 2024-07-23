import sys
import os
import json
import yaml
import textwrap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLineEdit, QLabel, QRadioButton, QFileDialog,
    QMessageBox, QButtonGroup, QCheckBox, QListWidgetItem, QComboBox, QInputDialog,
    QGroupBox, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class FileCollectorThread(QThread):
    progress_update = pyqtSignal(int)
    file_collected = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, folders, file_types, excluded_folders, use_relative_path):
        super().__init__()
        self.folders = folders
        self.file_types = file_types
        self.excluded_folders = excluded_folders
        self.use_relative_path = use_relative_path

    def run(self):
        collected_content = {}
        total_files = sum(sum(len(files) for _, _, files in os.walk(folder)) for folder in self.folders)
        processed_files = 0

        for folder in self.folders:
            for root, dirs, files in os.walk(folder):
                dirs[:] = [d for d in dirs if d not in self.excluded_folders]
                for file in files:
                    if not self.file_types or any(file.endswith(ftype) for ftype in self.file_types):
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if self.use_relative_path:
                                    relative_path = os.path.relpath(file_path, folder)
                                    collected_content[relative_path] = content
                                    self.file_collected.emit(relative_path)
                                else:
                                    collected_content[file_path] = content
                                    self.file_collected.emit(file_path)
                        except Exception as e:
                            print(f"Error reading file {file}: {str(e)}")
                    processed_files += 1
                    progress = int(processed_files / total_files * 100)
                    self.progress_update.emit(progress)

        self.finished.emit(collected_content)

class FileCollectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_folders = []
        self.file_types = []
        self.excluded_folders = ["node_modules", "vendor", ".git", ".idea", ".github", ".husky", ".vscode", ".archive", ".cypress", ".scaffoldes", ".storybook", "build", "dist", "public"]
        self.profiles = {
            "Node/TypeScript Project": {
                'file_types': ['ts', 'tsx', 'js', 'jsx', 'json', 'yaml', 'yml', 'md', 'html', 'css', 'scss', 'less', 'graphql'],
                'excluded_folders': ['build', 'dist', 'node_modules', 'public', 'vendor']
            },
            "PHP Project": {
                'file_types': ['php', 'html', 'css', 'scss', 'less', 'js', 'json', 'yaml', 'yml', 'md', 'xml', 'twig', 'blade.php'],
                'excluded_folders': ['build', 'dist', 'node_modules', 'public', 'vendor']
            },
            "Python Project": {
                'file_types': ['py', 'ipynb', 'json', 'yaml', 'yml', 'md', 'txt', 'html', 'css', 'js', 'csv', 'tsv', 'ini', 'cfg', 'rst'],
                'excluded_folders': ['__pycache__', '.ipynb_checkpoints', 'build', 'dist', 'node_modules', 'public', 'vendor']
            }
        }
        self.collected_content = {}
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Advanced File Collector")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)

        # Profile Management
        profile_group = self.create_profile_group()
        left_layout.addWidget(profile_group)

        # Folder Selection
        folder_group = self.create_folder_group()
        left_layout.addWidget(folder_group)

        # File Types
        file_types_group = self.create_file_types_group()
        left_layout.addWidget(file_types_group)

        # Excluded Folders
        exclusion_group = self.create_exclusion_group()
        left_layout.addWidget(exclusion_group)

        # Export Settings
        export_group = self.create_export_group()
        left_layout.addWidget(export_group)

        left_layout.addStretch()

        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)

        # File list
        self.file_list = QListWidget()
        right_layout.addWidget(self.file_list)

        # Progress bar
        self.progress_bar = QProgressBar()
        right_layout.addWidget(self.progress_bar)

        # Relative filepath checkbox
        self.relative_path_checkbox = QCheckBox("Use Relative Filepath")
        right_layout.addWidget(self.relative_path_checkbox)

        # Action Buttons
        button_layout = QHBoxLayout()
        collect_button = self.create_button("Collect", self.collect_files)
        export_button = self.create_button("Export", self.export_files)
        collect_button.setFixedHeight(50)
        export_button.setFixedHeight(50)
        button_layout.addWidget(collect_button)
        button_layout.addWidget(export_button)
        right_layout.addLayout(button_layout)

        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([300, 300])  # Set initial sizes of the splitter

        main_layout.addWidget(content_splitter)

        self.setLayout(main_layout)
        self.setWindowTitle('Advanced File Collector')
        self.setGeometry(100, 100, 1000, 800)

        # Preload the first profile
        first_profile = next(iter(self.profiles))
        self.profile_combo.setCurrentText(first_profile)
        self.load_profile(first_profile)

    def create_profile_group(self):
        profile_group = QGroupBox("Profile Management")
        profile_layout = QHBoxLayout()
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.profiles.keys())
        self.profile_combo.currentTextChanged.connect(self.load_profile)
        save_profile_button = self.create_button("Save", self.save_profile)
        delete_profile_button = self.create_button("Delete", self.delete_profile)
        profile_layout.addWidget(QLabel("Profiles:"))
        profile_layout.addWidget(self.profile_combo)
        profile_layout.addWidget(save_profile_button)
        profile_layout.addWidget(delete_profile_button)
        profile_group.setLayout(profile_layout)
        return profile_group

    def create_folder_group(self):
        folder_group = QGroupBox("Folder Selection")
        folder_layout = QVBoxLayout()
        self.folder_list = QListWidget()
        folder_buttons_layout = QHBoxLayout()
        add_folder_button = self.create_button("Add Folder", self.add_folder)
        remove_folder_button = self.create_button("Remove Selected", self.remove_selected_folder)
        folder_buttons_layout.addWidget(add_folder_button)
        folder_buttons_layout.addWidget(remove_folder_button)
        folder_layout.addWidget(self.folder_list)
        folder_layout.addLayout(folder_buttons_layout)
        folder_group.setLayout(folder_layout)
        return folder_group

    def create_file_types_group(self):
        file_types_group = QGroupBox("File Types")
        file_types_layout = QVBoxLayout()
        self.file_types_list = QListWidget()
        self.file_types_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.file_types_input = QLineEdit()
        file_type_buttons_layout = QHBoxLayout()
        add_file_type_button = self.create_button("Add", self.add_file_type)
        remove_file_type_button = self.create_button("Remove", self.remove_selected_file_type)
        file_type_buttons_layout.addWidget(self.file_types_input)
        file_type_buttons_layout.addWidget(add_file_type_button)
        file_type_buttons_layout.addWidget(remove_file_type_button)
        file_types_layout.addWidget(self.file_types_list)
        file_types_layout.addLayout(file_type_buttons_layout)
        file_types_group.setLayout(file_types_layout)
        return file_types_group

    def create_exclusion_group(self):
        exclusion_group = QGroupBox("Excluded Folders")
        exclusion_layout = QVBoxLayout()
        self.excluded_folders_list = QListWidget()
        self.excluded_folders_input = QLineEdit()
        exclusion_buttons_layout = QHBoxLayout()
        add_exclusion_button = self.create_button("Add", self.add_excluded_folder)
        remove_exclusion_button = self.create_button("Remove", self.remove_selected_excluded_folder)
        exclusion_buttons_layout.addWidget(self.excluded_folders_input)
        exclusion_buttons_layout.addWidget(add_exclusion_button)
        exclusion_buttons_layout.addWidget(remove_exclusion_button)
        exclusion_layout.addWidget(self.excluded_folders_list)
        exclusion_layout.addLayout(exclusion_buttons_layout)
        exclusion_group.setLayout(exclusion_layout)
        return exclusion_group

    def create_export_group(self):
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout()
        self.export_type_group = QButtonGroup(self)
        self.plain_text_radio = QRadioButton("Plain Text")
        self.json_radio = QRadioButton("JSON")
        self.yaml_radio = QRadioButton("YAML")
        self.jsonl_radio = QRadioButton("JSONL")
        self.export_type_group.addButton(self.plain_text_radio)
        self.export_type_group.addButton(self.json_radio)
        self.export_type_group.addButton(self.yaml_radio)
        self.export_type_group.addButton(self.jsonl_radio)
        export_layout.addWidget(self.plain_text_radio)
        export_layout.addWidget(self.json_radio)
        export_layout.addWidget(self.yaml_radio)
        export_layout.addWidget(self.jsonl_radio)
        self.minify_checkbox = QCheckBox("Minify Content")
        export_layout.addWidget(self.minify_checkbox)
        export_group.setLayout(export_layout)
        return export_group

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selected_folders.append(folder)
            self.folder_list.addItem(folder)

    def remove_selected_folder(self):
        for item in self.folder_list.selectedItems():
            self.selected_folders.remove(item.text())
            self.folder_list.takeItem(self.folder_list.row(item))

    def add_file_type(self):
        file_type = self.file_types_input.text().strip()
        if file_type and file_type not in self.file_types:
            self.file_types.append(file_type)
            self.file_types_list.addItem(file_type)
            self.file_types_input.clear()

    def remove_selected_file_type(self):
        for item in self.file_types_list.selectedItems():
            self.file_types.remove(item.text())
            self.file_types_list.takeItem(self.file_types_list.row(item))

    def add_excluded_folder(self):
        folder = self.excluded_folders_input.text().strip()
        if folder and folder not in self.excluded_folders:
            self.excluded_folders.append(folder)
            self.excluded_folders_list.addItem(folder)
            self.excluded_folders_input.clear()

    def remove_selected_excluded_folder(self):
        for item in self.excluded_folders_list.selectedItems():
            self.excluded_folders.remove(item.text())
            self.excluded_folders_list.takeItem(self.excluded_folders_list.row(item))

    def save_profile(self):
        profile_name, ok = QInputDialog.getText(self, 'Save Profile', 'Enter profile name:')
        if ok and profile_name:
            self.profiles[profile_name] = {
                'file_types': self.file_types.copy(),
                'excluded_folders': self.excluded_folders.copy()
            }
            self.profile_combo.addItem(profile_name)
            self.profile_combo.setCurrentText(profile_name)

    def load_profile(self, profile_name):
        if profile_name in self.profiles:
            profile = self.profiles[profile_name]
            self.file_types = profile['file_types']
            self.excluded_folders = profile['excluded_folders']
            self.update_ui_from_profile()

    def update_ui_from_profile(self):
        self.file_types_list.clear()
        self.file_types_list.addItems(self.file_types)
        self.excluded_folders_list.clear()
        self.excluded_folders_list.addItems(self.excluded_folders)

    def delete_profile(self):
        profile_name = self.profile_combo.currentText()
        if profile_name in self.profiles:
            del self.profiles[profile_name]
            self.profile_combo.removeItem(self.profile_combo.currentIndex())

    def collect_files(self):
        if not self.selected_folders:
            QMessageBox.warning(self, "No Folders Selected", "Please select at least one folder.")
            return

        self.progress_bar.setValue(0)
        self.file_list.clear()
        self.collected_content.clear()

        use_relative_path = self.relative_path_checkbox.isChecked()

        self.collector_thread = FileCollectorThread(self.selected_folders, self.file_types, self.excluded_folders, use_relative_path)
        self.collector_thread.progress_update.connect(self.update_progress)
        self.collector_thread.file_collected.connect(self.update_file_list)
        self.collector_thread.finished.connect(self.collection_finished)
        self.collector_thread.start()

    def export_files(self):
        if not self.collected_content:
            QMessageBox.warning(self, "No Files Collected", "Please collect files before exporting.")
            return

        export_type = self.get_export_type()
        if not export_type:
            QMessageBox.warning(self, "No Export Type Selected", "Please select an export type.")
            return

        if self.minify_checkbox.isChecked():
            content_to_export = self.minify_content(self.collected_content)
        else:
            content_to_export = self.collected_content

        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", self.get_file_extension(export_type))

        if save_path:
            try:
                self.save_content(content_to_export, save_path, export_type)
                QMessageBox.information(self, "Export Successful", f"Content exported successfully to {save_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error Exporting File", f"Could not export file: {str(e)}")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_file_list(self, file_path):
        self.file_list.addItem(file_path)

    def collection_finished(self, collected_content):
        self.collected_content = collected_content
        QMessageBox.information(self, "Collection Complete", f"Collected {len(self.collected_content)} files.")

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

    def minify_content(self, content):
        minified_content = {}
        for path, text in content.items():
            minified_content[path] = textwrap.dedent(text).replace('\n', ' ').replace('\r', ' ').strip()
        return minified_content

    def save_content(self, content, path, export_type):
        if export_type == 'plain_text':
            with open(path, 'w', encoding='utf-8') as f:
                for file_path, file_content in content.items():
                    f.write(f"File: {file_path}\n\n{file_content}\n\n{'='*80}\n\n")
        elif export_type == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
        elif export_type == 'yaml':
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(content, f, allow_unicode=True)
        elif export_type == 'jsonl':
            with open(path, 'w', encoding='utf-8') as f:
                for file_path, file_content in content.items():
                    f.write(json.dumps({file_path: file_content}, ensure_ascii=False) + '\n')

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileCollectorApp()
    ex.show()
    sys.exit(app.exec())
