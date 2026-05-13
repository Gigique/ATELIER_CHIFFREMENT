#!/usr/bin/env python3
"""
Atelier Chiffrement — fernet_atelier1.py
La clé Fernet est stockée dans un Repository Secret GitHub (FERNET_KEY)
et injectée comme variable d'environnement par GitHub Actions.

Usage:
  python app/fernet_atelier1.py encrypt <source> <destination>
  python app/fernet_atelier1.py decrypt <source> <destination>
"""

import os
import sys
from cryptography.fernet import Fernet, InvalidToken


def get_key():
    """Récupère la clé Fernet depuis la variable d'environnement injectée par GitHub Actions."""
    key = os.environ.get("FERNET_KEY")
    if not key:
        print("❌ Variable FERNET_KEY introuvable.")
        print("   En local        : export FERNET_KEY='...'")
        print("   GitHub Actions  : env: FERNET_KEY: ${{ secrets.FERNET_KEY }}")
        sys.exit(1)
    return key.encode()


def encrypt_file(src: str, dst: str):
    fernet = Fernet(get_key())
    with open(src, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(dst, "wb") as f:
        f.write(encrypted)
    print(f"✅ Fichier chiffré  : {src} → {dst}")


def decrypt_file(src: str, dst: str):
    fernet = Fernet(get_key())
    with open(src, "rb") as f:
        data = f.read()
    try:
        decrypted = fernet.decrypt(data)
    except InvalidToken:
        print("❌ Échec du déchiffrement : clé incorrecte ou fichier corrompu.")
        sys.exit(1)
    with open(dst, "wb") as f:
        f.write(decrypted)
    print(f"✅ Fichier déchiffré : {src} → {dst}")


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("encrypt", "decrypt"):
        print("Usage:")
        print("  python app/fernet_atelier1.py encrypt <source> <destination>")
        print("  python app/fernet_atelier1.py decrypt <source> <destination>")
        sys.exit(1)

    action, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]

    if not os.path.exists(src):
        print(f"❌ Fichier introuvable : {src}")
        sys.exit(1)

    if action == "encrypt":
        encrypt_file(src, dst)
    else:
        decrypt_file(src, dst)


if __name__ == "__main__":
    main()