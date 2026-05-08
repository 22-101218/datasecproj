# 🚗 VehicleChain — Blockchain Vehicle Ownership System

A full-stack desktop application for managing vehicle ownership on the Ethereum blockchain. Built with Python, Solidity, and PyQt5, it provides a modern GUI, PDF certificate generation, VIN validation, CSV audit logging, and real-time event monitoring — all backed by a local Ganache blockchain.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔗 **Blockchain Registry** | Register vehicles and transfer ownership via a Solidity smart contract |
| 🖥️ **Desktop GUI** | Full PyQt5 interface with a futuristic dark/violet theme |
| 📄 **PDF Certificates** | Auto-generate ownership certificates with QR code and branding |
| 🔍 **VIN Validator** | Validates real 17-character VINs or custom vehicle IDs |
| 📋 **Audit Log** | Every action is recorded to `audit_log.csv` automatically |
| ⚡ **Live Event Feed** | Real-time blockchain event listener in the GUI |
| 🔐 **Role-Based Access** | Authority and Verifier roles enforced on-chain |
| 🏠 **Ownership History** | Immutable on-chain timeline of all past owners |

---

## 🗂️ Project Structure

```
datasecproj/
│
├── contracts/
│   └── VehicleOwnership.sol      # Solidity smart contract (Solidity ^0.8.19)
│
├── vehiclechain/                 # Main Python package
│   ├── __main__.py               # Entry point (python -m vehiclechain)
│   ├── gui.py                    # PyQt5 desktop GUI
│   ├── cli.py                    # Terminal CLI menu
│   ├── blockchain.py             # Web3.py + contract interaction helpers
│   ├── pdf_cert.py               # PDF certificate generator (ReportLab + QR)
│   ├── audit_log.py              # CSV audit logging
│   ├── vin_utils.py              # VIN validation logic
│   └── paths.py                  # Path resolution for bundled/dev environments
│
├── VehicleOwnershipSystem/       # Original base project
│   ├── contracts/VehicleOwnership.sol
│   ├── main.py
│   └── requirements.txt
│
├── assets/
│   ├── car_logo.png              # App logo (GUI + PDF)
│   └── car_logo.ico              # Windows icon
│
├── app.py                        # Shortcut: launches the CLI
├── requirements.txt              # Python dependencies
├── VehicleChain.spec             # PyInstaller build config
└── README.md
```

---

## ⚙️ Prerequisites

- **Python 3.10+**
- **[Ganache](https://trufflesuite.com/ganache/)** — local Ethereum blockchain (GUI or CLI)
- **Node.js** (only needed if using Truffle/Hardhat for contract deployment)

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/22-101218/datasecproj.git
cd datasecproj
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Ganache
Launch **Ganache** and ensure it is running on:
```
http://127.0.0.1:7545
```

---

## ▶️ Running the App

### GUI (Recommended)
```bash
python -m vehiclechain
```

### CLI (Terminal menu)
```bash
python app.py
```

---

## 🖥️ GUI Panels

| Panel | Description |
|---|---|
| **Dashboard** | Live block number, connection status, and available accounts |
| **Deploy Contract** | Compile and deploy the smart contract with one click |
| **Register Vehicle** | Register a new vehicle using a real VIN or custom ID |
| **Transfer Ownership** | Securely transfer a vehicle to a new owner (owner-only) |
| **Verify Owner** | Public lookup of current owner by vehicle ID |
| **Vehicle Details** | Full vehicle info card (brand, model, owner, timestamp) |
| **Ownership History** | Complete immutable transfer history from the blockchain |
| **PDF Certificate** | Generate a signed PDF ownership certificate with QR code |
| **Live Events** | Real-time feed of blockchain events as they happen |
| **Audit Log** | View all logged actions from `audit_log.csv` |
| **Set Verifier** | Grant or revoke the verifier role for an address |

---

## 📜 Smart Contract Overview

**`contracts/VehicleOwnership.sol`** — Solidity `^0.8.19`

### Key Roles
- **Authority** — the deploying address; can register vehicles and manage verifiers
- **Verifier** — can call `verifyOwnershipByVerifier()` and emit a verification event

### Core Functions

| Function | Access | Description |
|---|---|---|
| `registerVehicle(id, brand, model, owner)` | Authority only | Register a new vehicle |
| `transferOwnership(id, newOwner)` | Current owner only | Transfer to new owner |
| `verifyCurrentOwner(id)` | Public (view) | Returns current owner address |
| `verifyOwnershipByVerifier(id)` | Verifier only | Emits `OwnershipVerified` event |
| `getVehicle(id)` | Public (view) | Returns full vehicle details |
| `getOwnershipHistory(id)` | Public (view) | Returns all past owner records |
| `setVerifier(address, bool)` | Authority only | Grant/revoke verifier role |

### Events
- `VehicleRegistered`
- `OwnershipTransferred`
- `OwnershipVerified`
- `VerifierUpdated`

---

## 📦 Dependencies

```
web3==6.20.2
py-solc-x==2.0.3
PyQt5
reportlab
qrcode[pil]
Pillow
pyinstaller>=6.0
```

---

## 🏗️ Building the Windows Executable

```powershell
pip install pyinstaller
pyinstaller --noconfirm VehicleChain.spec
```

Output: `dist\VehicleChain.exe`

> Make sure Ganache is running on `http://127.0.0.1:7545` before launching the `.exe`.

**Generated files (same folder as the executable):**
- `audit_log.csv` — CSV log of all actions
- `certificate_<vehicleId>.pdf` — PDF ownership certificates

---

## 📄 License

This project was developed as an academic submission. All rights reserved.
