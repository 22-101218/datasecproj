# Blockchain-Based Vehicle Ownership System

A secure, transparent, and tamper-proof registry for vehicle registration and ownership transfers using blockchain technology.

## Requirements Met

✅ **Blockchain Network Setup** — Uses Ganache as local blockchain simulator at http://127.0.0.1:7545

✅ **Smart Contract Development** — Solidity contract with:
- Vehicle registration (authority only)
- Ownership transfer (owner only)
- Ownership verification (public)
- History retrieval (immutable records)

✅ **Vehicle Data Structure**:
- Vehicle ID (VIN or custom)
- Brand / Model
- Current owner address
- Registration timestamp

✅ **Vehicle Registration** — Only authority can register, unique IDs, recorded as blockchain transaction

✅ **Ownership Transfer** — Only current owner can transfer, secure smart contract logic, immutable records

✅ **Access Control** — Role-based (Authority, Verifiers, Owners) with modifiers

✅ **Ownership Verification** — Public lookup by vehicle ID with full history

✅ **Immutability & Transparency** — All updates traceable through blockchain history, events logged

## Setup

```bash
pip install -r requirements.txt
```

## Running the CLI

1. **Start Ganache** on http://127.0.0.1:7545

2. **Run the CLI**:
```bash
python main.py
```

3. **Menu Options**:
   - Deploy Contract — Compile and deploy to Ganache
   - Register Vehicle — Add new vehicle (authority)
   - Transfer Ownership — Change owner (owner signs)
   - Verify Owner — Check current owner
   - View Vehicle Details — Full vehicle info
   - View Ownership History — Immutable transaction timeline
   - Exit

## Architecture

```
VehicleOwnershipSystem/
├── main.py                          # CLI application
├── contracts/
│   └── VehicleOwnership.sol         # Smart contract
├── requirements.txt                 # Dependencies
└── README.md                        # This file
```

## Key Features

- **Immutable Records** — Blockchain ensures no modification or deletion
- **Full Audit Trail** — Every transaction recorded with block number
- **Role-Based Security** — Authority controls registration, owners control transfers
- **Real-time Verification** — Query current owner or complete history
- **Transparent** — All actions logged to blockchain with events

## Example Workflow

1. Deploy contract (authority becomes contract owner)
2. Register vehicle with owner address
3. Owner can transfer to new owner
4. Anyone can verify current owner or view full history
5. All changes permanently recorded on blockchain

## Technical Stack

- **Blockchain**: Ganache (local, chain ID 1337)
- **Smart Contract**: Solidity 0.8.19
- **Python**: Web3.py for blockchain interaction
- **Solidity Compiler**: py-solc-x

## Notes

- Ganache must be running before starting the CLI
- All transactions cost simulated gas (no real cost)
- Restart Ganache to reset blockchain state
- Contract address stored in-memory during session
