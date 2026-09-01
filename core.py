import os
import json
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Paths for storing application data locally
DATA_DIR = Path.home() / ".cryptanote"
KEY_FILE = DATA_DIR / "secret.key"
STORAGE_FILE = DATA_DIR / "notes.enc"

class Note:
    """Represents an individual note."""
    def __init__(self, title: str, content: str = "", created_at: str = None, updated_at: str = None):
        self.title = title
        self.content = content
        now = datetime.now().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def update_content(self, content: str):
        self.content = content
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            title=data["title"],
            content=data.get("content", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

class EncryptionManager:
    """Handles 256-bit AES-GCM key generation, encryption, and decryption."""
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.key = self._get_or_create_key()
        self.aesgcm = AESGCM(self.key)

    def _get_or_create_key(self) -> bytes:
        if not KEY_FILE.exists():
            # Generate a raw 256-bit (32-byte) key
            key = AESGCM.generate_key(bit_length=256)
            KEY_FILE.write_bytes(key)
            return key
        return KEY_FILE.read_bytes()

    def encrypt(self, raw_str: str) -> bytes:
        # A 12-byte nonce (number used once) is required for AES-GCM
        nonce = os.urandom(12)
        data_bytes = raw_str.encode("utf-8")
        ciphertext = self.aesgcm.encrypt(nonce, data_bytes, associated_data=None)
        # Store the nonce alongside the ciphertext (nonce + ciphertext)
        return nonce + ciphertext

    def decrypt(self, enc_bytes: bytes) -> str:
        # Extract the 12-byte nonce from the beginning of the payload
        nonce = enc_bytes[:12]
        ciphertext = enc_bytes[12:]
        decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, associated_data=None)
        return decrypted_bytes.decode("utf-8")

class StorageManager:
    """Manages loading, saving, and searching encrypted notes on disk."""
    def __init__(self):
        self.crypto = EncryptionManager()
        self.notes = {}  # Format: {"Note Title": Note Object}
        self.load_notes()

    def load_notes(self):
        if not STORAGE_FILE.exists():
            self.notes = {}
            return
        try:
            raw_bytes = STORAGE_FILE.read_bytes()
            json_str = self.crypto.decrypt(raw_bytes)
            data = json.loads(json_str)
            self.notes = {title: Note.from_dict(n_data) for title, n_data in data.items()}
        except Exception:
            # Fallback if key missing or file corrupt
            self.notes = {}

    def save_notes(self):
        data = {title: note.to_dict() for title, note in self.notes.items()}
        json_str = json.dumps(data)
        enc_bytes = self.crypto.encrypt(json_str)
        STORAGE_FILE.write_bytes(enc_bytes)

    def search_notes(self, query: str) -> list:
        q = query.lower()
        return [
            note for note in self.notes.values()
            if q in note.title.lower() or q in note.content.lower()
        ]