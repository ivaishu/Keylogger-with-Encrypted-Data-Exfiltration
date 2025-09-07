# Keylogger-with-Encrypted-Data-Exfiltration (Educational / Research Use Only)

> ⚠️ **Disclaimer**:  
> This project is for **educational and research purposes only**. Do **not** use it on machines without explicit permission. Running keyloggers outside of a controlled environment (like a VM or lab machine) is **illegal and unethical**.

---

## 📌 Features
- Captures keystrokes using `pynput`
- Symmetrically encrypts logs with `cryptography.fernet`
- Saves encrypted logs to timestamped files
- Simulates exfiltration by sending logs to a local server
- Organized with a class-based design

---

## ⚙️ Requirements
Install dependencies inside your safe test environment (e.g., a virtual machine):

```bash
pip install pynput cryptography
```
## 1. Start the Server (Receiver)

Create a simple server (server.py) to receive logs:

```bash import socket
import threading

def handle_client(conn):
    data = conn.recv(4096)
    print("Received:", data.decode())
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen(5)

print("Server listening on 127.0.0.1:8080...")
while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn,))
    thread.start()
```
Run the server in one terminal:

```bash
python server.py
```
## 2. Run the Keylogger

In another terminal, run:

```bash
python keylogger.py
```
## 3. Test Keystrokes

Type normally in your VM

Press special keys (space, enter, arrows, etc.)

Try rapid typing or long sessions

## 🔒 Logs

- Encrypted keystrokes are saved locally as log-YYYYMMDD-HHMMSS.enc

- Logs are also base64-encoded and sent to the server

- Example cleanup:

rm log-*.enc

## 🧪 Testing Scenarios

- ✅ Normal typing

- ✅ Special characters & Unicode

- ✅ Long-running sessions

- ✅ Network transmission reliability

- ✅ Error handling on disconnect

## ⚠️ Notes

- Always run inside a safe, isolated VM

- Do not deploy on production or personal systems

- Useful for demonstrating:

- Keylogging techniques

- Encryption handling

- Safe exfiltration simulation
  
## 📊 Flow Diagram

[Keyboard Input] → [Capture Keystroke] → [Encrypt Log]
        ↓                          ↓
 [Save to .enc File]        [Base64 Encode]
        ↓                          ↓
   Local Storage   ←–––––––→   Send to Server
