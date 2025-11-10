# components/file_selector_widget.py
import os
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class FileSelectionGroupBox(QGroupBox):
    
    file_selected = pyqtSignal(str)
    file_open = pyqtSignal(str)

    def __init__(self, title="", file_filter="All Files (*)", parent=None):
        super().__init__(title, parent)
        self.file_filter = file_filter
        main_layout = QVBoxLayout()
        file_path_layout = QHBoxLayout()

        self.file_label = QLabel("File Path:")
        file_path_layout.addWidget(self.file_label)

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("No file selected...")
        file_path_layout.addWidget(self.file_path_edit)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)
        file_path_layout.addWidget(self.browse_button)

        self.open_file_button = QPushButton("Open File")
        self.open_file_button.clicked.connect(self.open_selected_file)
        file_path_layout.addWidget(self.open_file_button)

        main_layout.addLayout(file_path_layout)
        self.setLayout(main_layout)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select a file", "", self.file_filter)

        if file_name:
            self.file_path_edit.setText(file_name)
            self.file_selected.emit(file_name)
        else:
            self.file_path_edit.setPlaceholderText("No file selected...")

    def open_selected_file(self):
        selected_file_path = self.file_path_edit.text()

        if not selected_file_path:
            QMessageBox.warning(self, "No File Selected", "Please select a file first using the 'Browse...' button.")
            return

        if not os.path.exists(selected_file_path):
            QMessageBox.critical(self, "File Not Found", f"The selected file does not exist:\n{selected_file_path}")
            return
            
        self.file_open.emit(selected_file_path)
