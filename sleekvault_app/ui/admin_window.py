from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox, QLineEdit, QHBoxLayout, QInputDialog
from PyQt5.QtCore import Qt
from auth import UserManager
from vault import VaultManager
import os

class AdminWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SleekVault Admin Panel")
        self.setGeometry(200, 200, 400, 400)
        self.user_manager = UserManager()
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>All Users</b>"))
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)

        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Delete User")
        self.delete_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(self.delete_btn)
        self.reset_pw_btn = QPushButton("Reset Password")
        self.reset_pw_btn.clicked.connect(self.reset_password)
        btn_layout.addWidget(self.reset_pw_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_users(self):
        self.user_list.clear()
        for username in self.user_manager.users:
            if username != "admin":
                self.user_list.addItem(username)

    def delete_user(self):
        selected = self.user_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Select a user to delete.")
            return
        username = selected.text()
        confirm = QMessageBox.question(self, "Delete User", f"Delete user '{username}' and their vault?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            vault_path = self.user_manager.get_vault_path(username)
            if vault_path and os.path.exists(vault_path):
                os.remove(vault_path)
            del self.user_manager.users[username]
            self.user_manager.save_users()
            self.load_users()
            QMessageBox.information(self, "Deleted", f"User '{username}' deleted.")

    def reset_password(self):
        selected = self.user_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Select a user to reset password.")
            return
        username = selected.text()
        new_pw, ok = QInputDialog.getText(self, "Reset Password", f"Enter new password for '{username}':", QLineEdit.Password)
        if ok and new_pw:
            vault_path = self.user_manager.get_vault_path(username)
            try:
                vault = VaultManager(vault_path, new_pw)  # Try to open with new password (will fail)
            except Exception:
                vault = VaultManager(vault_path, "dummy")  # Open with dummy, will fail, but we want to overwrite
            # Overwrite vault with new password
            vault.password = new_pw
            vault.save_vault()
            QMessageBox.information(self, "Success", f"Password for '{username}' reset.")
