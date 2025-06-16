from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from ui.register_window import RegisterWindow
from auth import UserManager
from ui.vault_window import VaultWindow
from PyQt5.QtGui import QPixmap
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SleekVault - Login")
        self.setGeometry(100, 100, 350, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # SleekVault logo
        logo = QLabel()
        pixmap = QPixmap(resource_path("resources/sleekvault.png"))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        title = QLabel("<h2>Welcome to SleekVault</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Login")
        layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("Register New User")
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

        # Connect buttons (logic to be implemented)
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.login)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password required.")
            return
        user_manager = UserManager()
        vault_path = user_manager.get_vault_path(username)
        if not vault_path:
            QMessageBox.warning(self, "Error", "User not found.")
            return
        # Try to decrypt vault to verify password
        from vault import VaultManager
        try:
            vault = VaultManager(vault_path, password)
            # If decryption fails, vault.data will be empty
            if vault.data is None:
                raise Exception()
        except Exception:
            QMessageBox.warning(self, "Error", "Incorrect password or vault file corrupted.")
            return
        self.hide()
        self.vault_window = VaultWindow(username, vault_path, password, self)
        self.vault_window.show()

    def register(self):
        self.hide()
        self.register_window = RegisterWindow(self)
        self.register_window.show()
