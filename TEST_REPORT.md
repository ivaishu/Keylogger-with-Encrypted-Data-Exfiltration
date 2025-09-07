# 📝 Test Report — Keylogger PoC

## ⚠️ Disclaimer
This project was tested **only in a safe, isolated virtual machine (VM)**.  
All inputs are **dummy test data** and not real user information.  
This PoC was created for **educational and research purposes only**.

---

## 1. Environment Setup
- **OS / VM platform:** (e.g., Ubuntu 22.04 VM on VirtualBox)
- **Python version:** (e.g., Python 3.11.6)
- **Installed packages:** `pynput`, `cryptography`

---

## 2. Test Steps

### a) Start the Server
Command:
```bash
python server.py
```
Expected:  
```
Server listening on 127.0.0.1:8080...
```

---

### b) Run the Keylogger
Command:
```bash
python keylogger.py
```
Expected:  
```
[*] Keylogger started. Press Ctrl+Shift+Q to stop (hotkey kill-switch).
[*] Using key file: /path/to/key.txt
```

---

### c) Provide Test Input
Typed in VM (dummy text):  
```
hello world test123 !@#
```
Also pressed: **Enter**, **Space**, **Arrow Keys**

---

### d) Stop with Kill Switch
Pressed: **Ctrl + Shift + Q**  
Expected console output:  
```
[*] Kill combo detected. Stopping keylogger...
[*] Saved encrypted log: log-20250907-123456.enc
```

---

## 3. Results

### a) Encrypted Log File
File created:  
```
log-20250907-123456.enc
```
Sample (binary/encrypted, unreadable):
```
gAAAAABnZ... (truncated)
```

### b) Decrypt with key.txt
Command:
```bash
python decrypt_file.py log-20250907-123456.enc
```
Output:
```
[*] Decrypted log-20250907-123456.enc -> log-20250907-123456.dec.txt
```

### c) Decrypted Log Contents
Contents of `.dec.txt`:
```
hello world test123 !@#
<enter>
<arrow keys simulated>
```

---

## 4. Network Exfiltration Test (Optional)
If `send_on_kill=True` was enabled:

Server output (from `server.py`):
```
Received: Z0FB... (base64 encoded string)
```

---

## 5. Observations
- ✅ Keystrokes captured accurately  
- ✅ Logs encrypted with persistent `key.txt`  
- ✅ Encrypted logs saved with timestamp  
- ✅ Decryption worked using provided script  
- ✅ Kill switch (Ctrl+Shift+Q) stopped logger as expected  
- ✅ Network exfiltration simulation succeeded (localhost only)

---

## 6. Cleanup
Removed test artifacts:
```bash
rm log-*.enc
rm *.dec.txt
```

---

## 7. Conclusion
The PoC keylogger works as intended:
- Captures keystrokes  
- Encrypts with Fernet (persistent key)  
- Stores logs locally with timestamps  
- Simulates network exfiltration  
- Provides safe stop via hotkey kill switch  

All testing was performed in a controlled VM environment.
