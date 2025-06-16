import os
import json
from crypto_utils import encrypt_data, decrypt_data

def get_users_file():
    app_support = os.path.expanduser('~/Library/Application Support/SleekVault')
    os.makedirs(app_support, exist_ok=True)
    return os.path.join(app_support, 'users.json')

class UserManager:
    def __init__(self, users_file=None):
        if users_file is None:
            users_file = get_users_file()
        self.users_file = users_file
        self.users = self.load_users()

    def load_users(self):
        if not os.path.exists(self.users_file):
            return {}
        with open(self.users_file, "r") as f:
            return json.load(f)

    def save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=2)

    def register_user(self, username, password, vault_path):
        if username in self.users:
            return False, "Username already exists."
        self.users[username] = {
            "vault_path": vault_path
        }
        self.save_users()
        # Create empty encrypted vault
        with open(vault_path, "wb") as f:
            f.write(encrypt_data(b"[]", password))
        return True, "User registered."

    def delete_user(self, username, password):
        if username not in self.users:
            return False, "User not found."
        vault_path = self.users[username]["vault_path"]
        if os.path.exists(vault_path):
            os.remove(vault_path)
        del self.users[username]
        self.save_users()
        return True, "User deleted."

    def get_vault_path(self, username):
        return self.users.get(username, {}).get("vault_path")
