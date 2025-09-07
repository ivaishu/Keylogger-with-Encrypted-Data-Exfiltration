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
