import os
import json
from crypto_utils import encrypt_data, decrypt_data

class VaultManager:
    def __init__(self, vault_path, password):
        self.vault_path = vault_path
        self.password = password
        self.data = self.load_vault()

    def load_vault(self):
        if not os.path.exists(self.vault_path):
            return []
        with open(self.vault_path, "rb") as f:
            encrypted = f.read()
        try:
            decrypted = decrypt_data(encrypted, self.password)
            data = json.loads(decrypted.decode())
            if isinstance(data, list):
                return data
            else:
                return []
        except Exception:
            return []

    def save_vault(self):
        with open(self.vault_path, "wb") as f:
            encrypted = encrypt_data(json.dumps(self.data).encode(), self.password)
            f.write(encrypted)

    def add_record(self, record):
        self.data.append(record)
        self.save_vault()

    def delete_record(self, idx):
        if 0 <= idx < len(self.data):
            del self.data[idx]
            self.save_vault()

    def update_record(self, idx, record):
        if 0 <= idx < len(self.data):
            self.data[idx] = record
            self.save_vault()
