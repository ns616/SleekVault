from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import os
from auth import UserManager

class RegisterWindow(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.setWindowTitle("SleekVault - Register")
        self.setGeometry(120, 120, 400, 300)
        self.login_window = login_window
        self.user_manager = UserManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("<h2>Register New User</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.vault_path_input = QLineEdit()
        self.vault_path_input.setPlaceholderText("Choose vault file location...")
        layout.addWidget(self.vault_path_input)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_btn)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def browse_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Vault File", os.path.expanduser("~"), "Vault Files (*.vault)")
        if path:
            self.vault_path_input.setText(path)

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        vault_path = self.vault_path_input.text().strip()
        if not username or not password or not vault_path:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        try:
            success, msg = self.user_manager.register_user(username, password, vault_path)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.close()
                self.login_window.show()
            else:
                QMessageBox.warning(self, "Error", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {e}")
