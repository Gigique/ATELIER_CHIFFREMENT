#!/usr/bin/env python3
"""
Atelier Chiffrement — nacl_atelier2.py
Chiffrement/déchiffrement avec PyNaCl SecretBox.
La clé est stockée dans un Repository Secret GitHub (NACL_KEY)
et injectée comme variable d'environnement par GitHub Actions.

Usage:
  python app/nacl_atelier2.py generate-key
  python app/nacl_atelier2.py encrypt <source> <destination>
  python app/nacl_atelier2.py decrypt <source> <destination>
"""

import os
import sys
import base64
from nacl.secret import SecretBox
from nacl.utils import random
from nacl import exceptions as nacl_exc


SECRET_ENV_VAR = "NACL_KEY"  # Nom du Repository Secret GitHub


def get_key() -> bytes:
    """
    Récupère la clé 32 octets depuis la variable d'environnement
    injectée par GitHub Actions (stockée en base64 dans le secret).
    """
    raw = os.environ.get(SECRET_ENV_VAR)
    if not raw:
        print(f"❌ Variable '{SECRET_ENV_VAR}' introuvable.")
        print(f"   En local       : export {SECRET_ENV_VAR}='...'")
        print(f"   GitHub Actions : env: {SECRET_ENV_VAR}: ${{{{ secrets.{SECRET_ENV_VAR} }}}}")
        print(f"   Générer une clé : python app/nacl_atelier2.py generate-key")
        sys.exit(1)
    try:
        key = base64.b64decode(raw)
        if len(key) != SecretBox.KEY_SIZE:
            raise ValueError
    except Exception:
        print(f"❌ La valeur de '{SECRET_ENV_VAR}' n'est pas une clé valide (32 octets en base64).")
        print(f"   Générez-en une : python app/nacl_atelier2.py generate-key")
        sys.exit(1)
    return key


def cmd_generate_key():
    """Génère une clé aléatoire 32 octets et l'affiche en base64."""
    key = random(SecretBox.KEY_SIZE)          # 32 octets cryptographiquement sûrs
    encoded = base64.b64encode(key).decode()
    print()
    print("✅ Nouvelle clé SecretBox générée (32 octets) :")
    print()
    print(f"   {encoded}")
    print()
    print("👉 Ajoutez-la dans GitHub :")
    print("   Settings → Secrets and variables → Actions → New repository secret")
    print(f"   Nom    : {SECRET_ENV_VAR}")
    print(f"   Valeur : <la clé ci-dessus>")
    print()


def cmd_encrypt(src: str, dst: str):
    """Chiffre src avec SecretBox et écrit le résultat dans dst."""
    box = SecretBox(get_key())

    with open(src, "rb") as f:
        plaintext = f.read()

    # encrypt() génère un nonce aléatoire et l'inclut dans le message chiffré
    encrypted = box.encrypt(plaintext)

    with open(dst, "wb") as f:
        f.write(encrypted)

    print(f"✅ Fichier chiffré  : {src} → {dst}")
    print(f"   Taille originale : {len(plaintext)} octets")
    print(f"   Taille chiffrée  : {len(encrypted)} octets (nonce inclus)")


def cmd_decrypt(src: str, dst: str):
    """Déchiffre src avec SecretBox et écrit le résultat dans dst."""
    box = SecretBox(get_key())

    with open(src, "rb") as f:
        ciphertext = f.read()

    try:
        plaintext = box.decrypt(ciphertext)
    except nacl_exc.CryptoError:
        print("❌ Échec du déchiffrement : clé incorrecte ou fichier corrompu.")
        sys.exit(1)

    with open(dst, "wb") as f:
        f.write(plaintext)

    print(f"✅ Fichier déchiffré : {src} → {dst}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]

    if action == "generate-key":
        cmd_generate_key()

    elif action == "encrypt":
        if len(sys.argv) != 4:
            print("Usage: python app/nacl_atelier2.py encrypt <source> <destination>")
            sys.exit(1)
        src, dst = sys.argv[2], sys.argv[3]
        if not os.path.exists(src):
            print(f"❌ Fichier introuvable : {src}")
            sys.exit(1)
        cmd_encrypt(src, dst)

    elif action == "decrypt":
        if len(sys.argv) != 4:
            print("Usage: python app/nacl_atelier2.py decrypt <source> <destination>")
            sys.exit(1)
        src, dst = sys.argv[2], sys.argv[3]
        if not os.path.exists(src):
            print(f"❌ Fichier introuvable : {src}")
            sys.exit(1)
        cmd_decrypt(src, dst)

    else:
        print(f"❌ Commande inconnue : '{action}'")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()