from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView, QCheckBox, QLineEdit, QMessageBox, QInputDialog, QDialog, QTextEdit, QStyle, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from vault import VaultManager
import pyperclip
import webbrowser
import json
import os, sys
import re
import functools

DEFAULT_COLUMNS = [
    ("Name", True),
    ("Description", False),
    ("Username", True),
    ("Password", True),
    ("URL", False),
    ("Secret Questions", False),
    ("Comments", False)
]

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class VaultWindow(QWidget):
    def __init__(self, username, vault_path, password, login_window):
        super().__init__()
        self.setWindowTitle(f"SleekVault - {username}'s Vault")
        self.setGeometry(150, 150, 800, 500)
        self.username = username
        self.vault_path = vault_path
        self.password = password
        self.login_window = login_window
        self.vault = VaultManager(vault_path, password)
        self.columns = [col for col, required in DEFAULT_COLUMNS if required or True]
        self.init_ui()
        self.load_table()

    def init_ui(self):
        layout = QVBoxLayout()
        # Top bar with title and logo on the same line
        top_bar = QHBoxLayout()
        title = QLabel(f"<h2>{self.username}'s Vault</h2>")
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        top_bar.addWidget(title)
        top_bar.addStretch(1)
        logo = QLabel()
        pixmap = QPixmap(resource_path("resources/sleekvault.png"))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        top_bar.addWidget(logo)
        layout.addLayout(top_bar)

        # Column selection
        self.column_checkboxes = []
        col_layout = QHBoxLayout()
        for col, required in DEFAULT_COLUMNS:
            cb = QCheckBox(col)
            cb.setChecked(True)
            cb.setEnabled(not required)
            cb.stateChanged.connect(self.update_columns)
            self.column_checkboxes.append(cb)
            col_layout.addWidget(cb)
        layout.addLayout(col_layout)
        self.selected_columns = [col for col, _ in DEFAULT_COLUMNS]

        # Filter input
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search by Name, Description, or URL...")
        self.filter_input.textChanged.connect(self.load_table)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(DEFAULT_COLUMNS) + 2)
        self.table.setHorizontalHeaderLabels([col for col, _ in DEFAULT_COLUMNS] + ["View", "Edit"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Record")
        self.add_btn.clicked.connect(self.add_record)
        btn_layout.addWidget(self.add_btn)
        self.delete_btn = QPushButton("Delete Record")
        self.delete_btn.clicked.connect(self.delete_record)
        btn_layout.addWidget(self.delete_btn)
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        btn_layout.addWidget(self.logout_btn)
        self.delete_user_btn = QPushButton("Delete My User")
        self.delete_user_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(self.delete_user_btn)
        self.export_btn = QPushButton("Export Vault")
        self.export_btn.clicked.connect(self.export_vault)
        btn_layout.addWidget(self.export_btn)
        self.import_btn = QPushButton("Import Vault")
        self.import_btn.clicked.connect(self.import_vault)
        btn_layout.addWidget(self.import_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def update_columns(self):
        self.selected_columns = [cb.text() for cb in self.column_checkboxes if cb.isChecked()]
        self.table.setColumnCount(len(self.selected_columns) + 2)
        self.table.setHorizontalHeaderLabels(self.selected_columns + ["View", "Edit"])
        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        filter_text = self.filter_input.text().strip().lower() if hasattr(self, 'filter_input') else ""
        for record in self.vault.data:
            if filter_text:
                name = str(record.get("Name", "")).lower()
                desc = str(record.get("Description", "")).lower()
                url = str(record.get("URL", "")).lower()
                if filter_text not in name and filter_text not in desc and filter_text not in url:
                    continue
            self.add_table_row(record)

    def add_table_row(self, record):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col_idx, col in enumerate(self.selected_columns):
            value = record.get(col, "")
            if col == "Password":
                copy_btn = QPushButton("******")
                copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
                copy_btn.setStyleSheet("padding: 4px 8px; text-align: center;")
                copy_btn.clicked.connect(functools.partial(self.copy_to_clipboard, value))
                self.table.setCellWidget(row, col_idx, copy_btn)
            elif col == "Username":
                masked = value[:3] + "***" if len(value) > 3 else value + "***"
                copy_btn = QPushButton(masked)
                copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
                copy_btn.setStyleSheet("padding: 4px 8px; text-align: center;")
                copy_btn.clicked.connect(functools.partial(self.copy_to_clipboard, value))
                self.table.setCellWidget(row, col_idx, copy_btn)
            else:
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col_idx, item)
        # Add View and Edit buttons
        view_btn = QPushButton("View")
        view_btn.clicked.connect(lambda _, r=row: self.view_record(r))
        self.table.setCellWidget(row, len(self.selected_columns), view_btn)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda _, r=row: self.edit_record(r))
        self.table.setCellWidget(row, len(self.selected_columns) + 1, edit_btn)

    def view_record(self, row):
        record = self.vault.data[row]
        dialog = RecordDialog(self, record, read_only=True)
        dialog.exec_()

    def edit_record(self, row):
        record = self.vault.data[row]
        existing_names = {rec.get("Name", "").strip().lower() for idx, rec in enumerate(self.vault.data) if idx != row}
        dialog = RecordDialog(self, record, read_only=False, existing_names=existing_names)
        if dialog.exec_() == QDialog.Accepted:
            updated_record = dialog.get_record()
            self.vault.update_record(row, updated_record)
            self.load_table()

    def add_record(self):
        existing_names = {rec.get("Name", "").strip().lower() for rec in self.vault.data}
        dialog = RecordDialog(self, existing_names=existing_names)
        if dialog.exec_() == QDialog.Accepted:
            record = dialog.get_record()
            self.vault.add_record(record)
            self.load_table()

    def delete_record(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a record to delete.")
            return
        confirm = QMessageBox.question(self, "Delete Record", "Do you really want to delete this record?", QMessageBox.Cancel | QMessageBox.Yes, QMessageBox.Cancel)
        if confirm != QMessageBox.Yes:
            return
        self.vault.delete_record(row)
        self.load_table()

    def logout(self):
        self.close()
        self.login_window.show()

    def delete_user(self):
        from auth import UserManager
        confirm = QMessageBox.question(self, "Delete User", "Are you sure you want to delete your user and all credentials? This cannot be undone.", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            user_manager = UserManager()
            success, msg = user_manager.delete_user(self.username, self.password)
            if success:
                QMessageBox.information(self, "Deleted", msg)
                self.close()
                self.login_window.show()
            else:
                QMessageBox.warning(self, "Error", msg)

    def export_vault(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Vault", "vault_export.json", "JSON Files (*.json);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "w") as f:
                json.dump(self.vault.data, f, indent=2)
            QMessageBox.information(self, "Exported", f"Vault exported to {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export: {e}")

    def import_vault(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Vault", "", "JSON Files (*.json);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "r") as f:
                imported_data = json.load(f)
            if not isinstance(imported_data, list):
                QMessageBox.warning(self, "Error", "Imported file is not a valid vault export.")
                return
            # Check for duplicates by Name
            existing_names = {rec.get("Name", "").strip().lower() for rec in self.vault.data}
            new_records = []
            for rec in imported_data:
                name = rec.get("Name", "").strip().lower()
                if name and name not in existing_names:
                    new_records.append(rec)
                    existing_names.add(name)
            if not new_records:
                QMessageBox.information(self, "Import", "No new records to import.")
                return
            self.vault.data.extend(new_records)
            self.vault.save_vault()
            self.load_table()
            QMessageBox.information(self, "Imported", f"Imported {len(new_records)} new records.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to import: {e}")

    def copy_to_clipboard(self, value):
        pyperclip.copy(value)

class RecordDialog(QDialog):
    def __init__(self, parent=None, record=None, read_only=False, existing_names=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Record" if not read_only else "View Record")
        self.setGeometry(200, 200, 400, 400)
        self.read_only = read_only
        self.existing_names = existing_names or set()
        self.original_name = record.get("Name", "").strip().lower() if record else None
        self.init_ui(record)

    def init_ui(self, record=None):
        layout = QVBoxLayout()
        self.inputs = {}
        for col, _ in DEFAULT_COLUMNS:
            if col == "Secret Questions":
                input_widget = QTextEdit()
                input_widget.setPlaceholderText("Q1:Answer1\nQ2:Answer2")
            elif col == "Comments":
                input_widget = QTextEdit()
            else:
                input_widget = QLineEdit()
                if col == "Password":
                    input_widget.setEchoMode(QLineEdit.Password)
            input_widget.setObjectName(col)
            if record:
                if isinstance(input_widget, QTextEdit):
                    input_widget.setPlainText(record.get(col, ""))
                else:
                    input_widget.setText(record.get(col, ""))
            if self.read_only:
                input_widget.setReadOnly(True)
            layout.addWidget(QLabel(col))
            layout.addWidget(input_widget)
            self.inputs[col] = input_widget
        if not self.read_only:
            btn = QPushButton("Save")
            btn.clicked.connect(self.accept)
            layout.addWidget(btn)
        else:
            btn = QPushButton("Close")
            btn.clicked.connect(self.reject)
            layout.addWidget(btn)
        self.setLayout(layout)

    def is_valid_url(self, url):
        if not url.strip():
            return True  # Allow empty
        pattern = re.compile(r'^(https?://)?([\w.-]+)\.([a-zA-Z]{2,})(/\S*)?$')
        return bool(pattern.match(url.strip()))

    def accept(self):
        name = self.inputs["Name"].text().strip().lower()
        url = self.inputs["URL"].text().strip()
        # Duplicate check (ignore original name if editing)
        if name in self.existing_names and name != self.original_name:
            QMessageBox.warning(self, "Duplicate", "A record with this Name already exists. Please choose a different name.")
            return
        if url and not self.is_valid_url(url):
            QMessageBox.warning(self, "Invalid URL", "The URL format is invalid. Please correct it before saving.")
            return
        super().accept()

    def get_record(self):
        record = {}
        for col, _ in DEFAULT_COLUMNS:
            widget = self.inputs[col]
            if isinstance(widget, QTextEdit):
                record[col] = widget.toPlainText()
            else:
                record[col] = widget.text()
        return record
