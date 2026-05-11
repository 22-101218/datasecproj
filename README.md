# VehicleChain - Blockchain Vehicle Ownership System

A secure, transparent blockchain-based vehicle ownership and transfer management system built on Ethereum (Ganache).

## Overview

VehicleChain is a decentralized application that leverages smart contracts to create an immutable, verifiable record of vehicle ownership. The system enables transparent ownership transfers, authorized verification, and comprehensive audit trails on the blockchain.

## Features

- **Blockchain-based Registration**: Permanently record vehicle ownership on the blockchain
- **Ownership Transfers**: Securely transfer vehicle ownership between authorized parties
- **Ownership Verification**: Public verification of current vehicle owner at any time
- **Ownership History**: Complete, immutable record of all ownership transfers with timestamps
- **Role-based Access Control**: Authority, Owner, and Verifier roles with specific permissions
- **Verifier Confirmation**: Trusted third-parties create audit trails for regulatory compliance
- **PDF Certificates**: Generate printable blockchain-verified ownership certificates with QR codes
- **Audit Logging**: Every action logged with transaction hash, block number, and timestamp
- **Dual Interface**: Both GUI and CLI applications for flexible workflow integration

## System Architecture

### Smart Contract (Solidity)

**File**: `contracts/VehicleOwnership.sol`

The smart contract implements:
- Vehicle registration and storage
- Ownership transfer logic
- Role-based access control
- Event logging for transparency
- Ownership history tracking

### Backend (Python)

**File**: `vehiclechain/blockchain.py`

Provides blockchain abstraction layer with functions for:
- Contract deployment
- Vehicle registration
- Ownership transfers
- Verification queries
- History retrieval

### Applications

**GUI Application**: `vehiclechain/gui.py`
- PyQt5-based graphical interface
- 11 feature panels for all operations
- Real-time blockchain connection status
- Interactive forms and result displays

**CLI Application**: `vehiclechain/cli.py`
- Terminal-based menu interface
- 9 operational options
- Scriptable for automation
- Clean output formatting

## Requirements

- Python 3.10 or higher
- Ganache CLI (v7.x or higher) running locally at http://127.0.0.1:7545
- For GUI: PyQt5 6.x
- Solidity compiler (via solcx, installed automatically)
- Web3.py 6.x
- Additional dependencies in requirements.txt

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd datasec
```

2. Create a Python virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Start Ganache (in a separate terminal)
```bash
ganache --deterministic
```

The default setup uses Ganache's deterministic mode with fixed accounts for consistent testing.

## Quick Start

### GUI Application

Run the graphical interface:
```bash
python -m vehiclechain gui
```

Or execute the compiled executable:
```bash
dist/VehicleChain.exe
```

### CLI Application

Run the text-based menu:
```bash
python -m vehiclechain cli
```

## Basic Workflow

### 1. Deploy Smart Contract

1. Start Ganache (listen on port 7545)
2. Launch the application (GUI or CLI)
3. Select "Deploy Contract"
4. Wait for deployment confirmation
5. Note: Contract deployed to a specific address

### 2. Register a Vehicle

1. Navigate to "Register Vehicle" panel
2. Enter Vehicle ID (VIN or custom format)
3. Enter Brand and Model
4. Enter Owner wallet address (must be Ganache account)
5. Submit - transaction recorded on blockchain

### 3. Transfer Ownership

1. Navigate to "Transfer Ownership" panel
2. Enter Vehicle ID
3. Enter Current Owner address
4. Enter New Owner address (must be Ganache account)
5. Submit - immutable transfer record created

### 4. Verify Current Owner

1. Navigate to "Verify Owner" panel
2. Enter Vehicle ID
3. View current owner address - public query, no permission required

### 5. View Ownership History

1. Navigate to "Ownership History" panel
2. Enter Vehicle ID
3. Review all transfers with timestamps

### 6. Generate Certificate

1. Navigate to "PDF Certificate" panel
2. Enter Vehicle ID
3. Certificate generated with:
   - Current owner
   - Ownership history
   - QR code linking to blockchain proof
   - Blockchain verification details

### 7. Set Verifier Role

1. Navigate to "Set Verifier" panel (Authority only)
2. Enter verifier wallet address
3. Toggle "Grant Access" checkbox
4. Submit - verifier role granted or revoked

### 8. Verifier Confirmation

1. Navigate to "Verifier Confirmation" panel (Verifier only)
2. Enter Vehicle ID
3. Enter Your Verifier Address
4. Submit - creates immutable OwnershipVerified event on blockchain

## Roles and Permissions

### Authority

- Deploys smart contract
- Registers new vehicles
- Grants/revokes verifier role
- Automatic: First Ganache account (0xabc...)

### Vehicle Owner

- Transfers ownership to new owner
- Must be wallet holding vehicle ownership
- Verified on-chain before transfer

### Verifier

- Creates official verification records
- Must be explicitly authorized by Authority
- Generates immutable OwnershipVerified events
- Public audit trail for third-party systems

### Any User

- Verify current owner (public read)
- View ownership history
- Generate certificates
- View audit logs

## Audit Log

Every blockchain action is logged to `audit_log.csv` with:

- Timestamp (YYYY-MM-DD HH:MM:SS)
- Action type (DEPLOY, REGISTER, TRANSFER, VERIFY, SET_VERIFIER, VERIFIER_CONFIRM)
- Vehicle ID
- Actor address
- Transaction hash
- Block number
- Additional notes

Location:
- Development: Project root directory
- Packaged: Same directory as VehicleChain.exe

## Technical Details

### Smart Contract Events

The contract emits the following events:

- **VehicleRegistered**: Fired on new vehicle registration
- **OwnershipTransferred**: Fired on ownership transfer
- **OwnershipVerified**: Fired when verifier confirms ownership
- **VerifierRoleChanged**: Fired on verifier role grant/revoke

### Data Persistence

- Contract state: Stored on Ganache blockchain
- Audit log: CSV file for local record-keeping
- Application state: Dynamically queried from blockchain

### Error Handling

The application includes comprehensive error handling for:
- Ganache disconnection
- Invalid addresses
- Non-existent Ganache accounts
- Transaction failures
- Network errors
- Input validation

## Development

### Project Structure

```
vehiclechain/
  __main__.py           - Application entry point
  blockchain.py         - Blockchain abstraction layer
  gui.py               - PyQt5 GUI application
  cli.py               - CLI menu application
  vin_utils.py         - Vehicle ID validation
  audit_log.py         - Audit logging
  pdf_cert.py          - PDF certificate generation
  paths.py             - Path utilities

contracts/
  VehicleOwnership.sol - Smart contract

assets/
  car_logo.ico         - Application icon
  car_logo.png         - Logo image

requirements.txt       - Python dependencies
VehicleChain.spec      - PyInstaller build configuration
```

### Building Executable

To rebuild the Windows executable:

```bash
pyinstaller VehicleChain.spec
```

Output: `dist/VehicleChain.exe`

## Troubleshooting

### "Unable to connect to Ganache"

- Ensure Ganache is running: `ganache --deterministic`
- Verify connection URL: http://127.0.0.1:7545
- Check firewall settings

### "Sender account not recognized"

- Address is not a valid Ganache account
- Import address into Ganache or use an existing account
- Use first account (0x) for authority operations

### "Insufficient funds for gas"

- Account has insufficient balance
- Ganache provides starting balance - check account history
- Use fresh Ganache instance if needed

### Application crashes on startup

- Check Python version: 3.10+
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check file permissions, especially in OneDrive directories

### Certificate generation fails

- Check if reportlab is installed: `pip install reportlab`
- Verify vehicle ID exists and has history
- Check disk space for PDF output

## License

This project is provided for educational and research purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review audit logs for detailed transaction information
3. Verify Ganache connection status
4. Check input validation messages

## Requirements Compliance

This system fully implements:

- **Requirement 6**: Role-based access control (Authority, Owner, Verifier)
- **Requirement 7**: Ownership verification process (public verify + history)
- **Requirement 8**: Immutability and transparency (blockchain-stored records + audit trail)

All data is permanently recorded on the blockchain with no modification or deletion capabilities.
