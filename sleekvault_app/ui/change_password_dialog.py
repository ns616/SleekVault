from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from auth import UserManager
from vault import VaultManager

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        self.setModal(True)
        self.setGeometry(150, 150, 350, 220)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Change Password</b>"))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.old_password_input = QLineEdit()
        self.old_password_input.setPlaceholderText("Current Password")
        self.old_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_password_input)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New Password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_input)

        self.change_btn = QPushButton("Change Password")
        self.change_btn.clicked.connect(self.change_password)
        layout.addWidget(self.change_btn)

        self.setLayout(layout)

    def change_password(self):
        username = self.username_input.text().strip()
        old_password = self.old_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        if not username or not old_password or not new_password:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        user_manager = UserManager()
        vault_path = user_manager.get_vault_path(username)
        if not vault_path:
            QMessageBox.warning(self, "Error", "User not found.")
            return
        try:
            vault = VaultManager(vault_path, old_password)
            if vault.data is None:
                raise Exception()
        except Exception:
            QMessageBox.warning(self, "Error", "Current password is incorrect.")
            return
        # Save vault with new password
        vault.password = new_password
        vault.save_vault()
        QMessageBox.information(self, "Success", "Password changed successfully.")
        self.accept()
