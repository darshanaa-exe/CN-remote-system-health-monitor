from cryptography.fernet import Fernet

# Shared key used by both client and server
KEY = b'uFLZrlP7FDwvWLgcJqGnaMtP1hWt2Bpdc83zgmxcwbo='
cipher = Fernet(KEY)

def encrypt_message(message: str) -> bytes:
    return cipher.encrypt(message.encode("utf-8"))

def decrypt_message(encrypted: bytes) -> str:
    return cipher.decrypt(encrypted).decode("utf-8")
