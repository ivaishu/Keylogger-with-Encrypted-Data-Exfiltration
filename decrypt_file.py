#!/usr/bin/env python3
from cryptography.fernet import Fernet
from pathlib import Path
import sys

KEY_FILE = Path("key.txt")  # default persistent key file

def decrypt_file(enc_file: Path, out_file: Path = None, key_file: Path = KEY_FILE):
    if not key_file.exists():
        print(f"[!] Key file not found: {key_file}")
        print("    Generate one with your keylogger or provide a custom key.")
        return False

    # Load the key
    key = key_file.read_bytes().strip()
    if isinstance(key, str):
        key = key.encode()
    f = Fernet(key)

    # Load the encrypted data
    encrypted = Path(enc_file).read_bytes()

    try:
        decrypted = f.decrypt(encrypted)
    except Exception as e:
        print(f"[!] Decryption failed: {type(e).__name__}: {e}")
        return False

    # Write output
    if out_file is None:
        out_file = Path(enc_file).with_suffix(".dec.txt")

    Path(out_file).write_bytes(decrypted)
    print(f"[*] Decrypted {enc_file} -> {out_file}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python decrypt_file.py <encrypted_file> [output_file] [key_file]")
        sys.exit(1)

    enc_file = Path(sys.argv[1])
    out_file = Path(sys.argv[2]) if len(sys.argv) >= 3 else None
    key_file = Path(sys.argv[3]) if len(sys.argv) >= 4 else KEY_FILE

    decrypt_file(enc_file, out_file, key_file)
