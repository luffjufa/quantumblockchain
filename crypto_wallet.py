import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

class SecureWalletVault:
    def __init__(self, wallet_filename="wallet_keystore.json"):
        self.wallet_filename = wallet_filename
        self.private_key = None
        self.public_key = None

    def create_wallet(self, password: str):
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.save_to_disk(password)
        print(f"[+] Secure Encrypted Wallet Created! Address: {self.get_address()}")

    def get_address(self):
        if not self.public_key:
            return None
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return base64.b16encode(pub_bytes).decode("utf-8")[:16]

    def save_to_disk(self, password: str):
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)

        priv_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        encrypted_priv = f.encrypt(priv_bytes).decode("utf-8")

        vault_data = {
            "salt": base64.b64encode(salt).decode("utf-8"),
            "encrypted_private_key": encrypted_priv,
            "address": self.get_address()
        }

        with open(self.wallet_filename, "w", encoding="utf-8") as file:
            json.dump(vault_data, file, indent=4)

    def load_from_disk(self, password: str):
        if not os.path.exists(self.wallet_filename):
            return False
        with open(self.wallet_filename, "r", encoding="utf-8") as file:
            vault_data = json.load(file)

        salt = base64.b64decode(vault_data["salt"].encode("utf-8"))
        encrypted_priv = vault_data["encrypted_private_key"].encode("utf-8")
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)

        try:
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            priv_bytes = f.decrypt(encrypted_priv)
            self.private_key = serialization.load_pem_private_key(priv_bytes, password=None)
            self.public_key = self.private_key.public_key()
            return True
        except Exception:
            return False

    def sign_transaction(self, recipient, amount, nonce):
        # Bind recipient, amount, and nonce into the signed message
        message = f"{recipient}:{amount}:{nonce}".encode("utf-8")
        signature = self.private_key.sign(message)
        return base64.b64encode(signature).decode("utf-8")

    @staticmethod
    def verify_signature(sender_pub_hex, recipient, amount, nonce, signature_b64):
        try:
            pub_bytes = base64.b16decode(sender_pub_hex.encode("utf-8"))
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            message = f"{recipient}:{amount}:{nonce}".encode("utf-8")
            signature = base64.b64decode(signature_b64.encode("utf-8"))
            public_key.verify(signature, message)
            return True
        except Exception:
            return False
