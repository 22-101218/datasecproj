# Blockchain-Based Vehicle Ownership System

A blockchain-powered vehicle registry using Ganache + Python.

## Project layout

| Path | Purpose |
|------|---------|
| `vehiclechain/` | Python package (GUI, CLI, blockchain, PDF, audit) |
| `vehiclechain/gui.py` | PyQt5 desktop application |
| `vehiclechain/cli.py` | Terminal menu |
| `vehiclechain/blockchain.py` | Web3.py + contract helpers |
| `contracts/VehicleOwnership.sol` | Solidity source |
| `assets/car_logo.png` | Window / PDF logo (replace with your artwork) |
| `app.py` | Shortcut: runs the text CLI |
| `VehicleChain.spec` | PyInstaller definition |
| `build_exe.ps1` | Builds `dist/VehicleChain.exe` |

## Setup

```bash
pip install -r requirements.txt
```

## Run (GUI)

1. Start **Ganache** on `http://127.0.0.1:7545`
2. From this folder:

```bash
python -m vehiclechain
```

## Run (CLI)

```bash
python app.py
```

## Windows executable

```powershell
pip install pyinstaller
pyinstaller --noconfirm VehicleChain.spec
```

(Or run `.\build_exe.ps1` — it also copies `assets\car_logo.png` to `dist\assets\` next to the exe, like the old `app_qt.py` + `assets` folder.) Output: `dist\VehicleChain.exe`. Start **Ganache** on `http://127.0.0.1:7545` first.

Generated files when using the `.exe` (same folder as the executable):

- `audit_log.csv`
- `certificate_<id>.pdf`

## GUI panels (Qt)

- **Dashboard** — live block number, connection status, accounts
- **Deploy Contract** — compile + deploy with one click
- **Register Vehicle** — supports real VINs and custom IDs
- **Transfer Ownership** — secure owner-only transfer
- **Verify Owner** — public lookup by vehicle ID
- **Vehicle Details** — full vehicle card
- **Ownership History** — immutable on-chain timeline
- **PDF Certificate** — generates `certificate_<id>.pdf` with QR code
- **Live Events** — real-time blockchain event feed
- **Audit Log** — every action logged to `audit_log.csv`
- **Set Verifier** — grant/revoke verifier role
