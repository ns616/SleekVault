# SleekVault

SleekVault is a secure, easy-to-use desktop application for managing your credentials locally on your Mac. Each user's data is encrypted and password-protected, ensuring your sensitive information stays private.

---

## Features
- **Multi-user support**: Each user has their own encrypted vault.
- **Modern, colorful UI**: Easy to use and visually appealing.
- **Customizable grid**: Choose which fields to display.
- **Masked/copyable username and password**: Secure and convenient.
- **Add, edit, view, and delete credentials**: Full control over your data.
- **Export/Import**: Backup or transfer your vault as a plain JSON file.
- **Password-protected storage**: All data is encrypted with your password.

---

## Installation

### 1. Download & Install
- Download the latest `SleekVault.app` from your release or build it yourself (see below).
- Drag `SleekVault.app` to your `/Applications` folder or Desktop.

### 2. First Launch
- Double-click `SleekVault.app` to open.
- On first launch, you may need to right-click and choose "Open" due to macOS Gatekeeper.

### 3. Register & Use
- Register a new user with a unique username and password.
- Choose a location in your home directory (e.g., `~/Documents/`) for your encrypted vault file.
- Log in to access your personal vault.
- Add, view, edit, or delete credentials as needed.
- Use the Export/Import buttons to backup or restore your data.

---

## Building from Source (Developers)

1. **Clone the repository** and open a terminal in the project directory.
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```sh
   python main.py
   ```
4. **Build a macOS app:**
   ```sh
   pyinstaller --windowed --onefile --name SleekVault \
     --icon sleekvault.icns \
     --add-data "resources/sleekvault.png:resources" \
     main.py
   ```
   The `.app` will be in the `dist/` folder.

---

## FAQ

**Where is my data stored?**
- User info is stored in `~/Library/Application Support/SleekVault/users.json`.
- Your encrypted vault file is stored wherever you choose during registration.

**Can I open my vault file in a text editor?**
- No, it is encrypted. Use SleekVault to view or export your data.

**How do I backup or move my data?**
- Use the Export/Import buttons in the app to save or restore your credentials as a plain JSON file.

**What if I forget my password?**
- For security, there is no password recovery. Only you can decrypt your vault.

---

## Support
For help or feedback, please contact the developer or open an issue in the project repository.

Enjoy secure, local credential management with SleekVault!
