# VehicleChain User Manual

Comprehensive guide for using the VehicleChain blockchain vehicle ownership system.

## Table of Contents

1. Getting Started
2. System Overview
3. Dashboard
4. Deploy Contract
5. Register Vehicle
6. Transfer Ownership
7. Verify Owner
8. Vehicle Details
9. Ownership History
10. PDF Certificate
11. Audit Log
12. Set Verifier
13. Verifier Confirmation
14. Common Workflows
15. Troubleshooting

## 1. Getting Started

### Launching the Application

#### GUI (Graphical User Interface)

Option 1 - From Python:
```bash
python -m vehiclechain gui
```

Option 2 - Execute compiled application:
```bash
dist/VehicleChain.exe
```

#### CLI (Command-Line Interface)

```bash
python -m vehiclechain cli
```

### Initial Setup Requirements

Before using VehicleChain, ensure:

1. Ganache is running locally on port 7545
```bash
ganache --deterministic
```

2. All dependencies are installed
```bash
pip install -r requirements.txt
```

3. Python 3.10+ is available
```bash
python --version
```

### Application Layout (GUI)

The graphical interface consists of:

- Left Sidebar: Navigation menu with 11 panels
- Main Content Area: Dynamic panel displaying current operation
- Status Bar: Bottom-left shows blockchain connection status
- Result Box: Displays operation results, confirmations, or errors

Connection Status Indicators:

- Green: "Connected, block #XX" - Blockchain is accessible
- Red: "Blockchain unavailable" - Cannot reach Ganache
- Gray: "Connecting..." - Initial connection attempt

## 2. System Overview

### Blockchain Concepts

VehicleChain uses Ethereum smart contracts deployed to Ganache (local blockchain).

Key Terms:

- **Transaction (TX)**: An action recorded on blockchain (costs gas)
- **Block**: A container of transactions, identified by block number
- **Block Number**: Sequence number of a block (0, 1, 2, ...)
- **TX Hash**: Unique identifier for a transaction (0x...)
- **Address**: Wallet identifier (0x... format, 42 characters)
- **Gas**: Fee for transaction execution (Ganache provides free gas)
- **Event**: Log entry emitted by smart contract

### User Roles

VehicleChain implements three roles:

#### Authority (System Administrator)

- Default: First Ganache account
- Permissions:
  - Deploy the smart contract
  - Register new vehicles
  - Grant and revoke verifier roles
- Identified by: Account address displayed after deployment

#### Vehicle Owner

- Any account that currently owns a vehicle
- Permissions:
  - Transfer ownership to new owner
  - View their vehicles
  - View ownership history
- Status: Assigned when vehicle is registered or transferred

#### Verifier (Trusted Inspector)

- Must be explicitly authorized by Authority
- Examples: Insurance company, police, DMV
- Permissions:
  - Create official ownership confirmations
  - Generate audit trail events
- Status: Granted/revoked by Authority through blockchain transaction

#### Regular User (No Special Role)

- Any account
- Permissions:
  - Query current owner (read-only)
  - View ownership history
  - Generate certificates
  - View audit logs

## 3. Dashboard

### Location

In GUI: Click "Dashboard" in left sidebar

### Purpose

Central information hub showing:
- System status and connection information
- Ganache account list with balances
- Deployed contract address (if exists)
- Authority account identification

### Information Displayed

#### Blockchain Status

Shows connection state:
- Connected: "Ganache at http://127.0.0.1:7545"
- Disconnected: "Unable to connect to Ganache"

#### Account List

Displays all unlocked Ganache accounts:

- Account 0: Authority account (deploy rights)
- Accounts 1-9: Regular accounts for testing
- Balances: Starting balance for each account

Each row shows:
- Account number
- Wallet address (0x...)
- Account balance (in ETH)

#### Contract Information

After deployment:
- Contract Address: 0x... (20-byte Ethereum address)
- Status: "Contract deployed" (green) or "Not deployed yet" (gray)

### Refreshing Dashboard

Dashboard auto-updates every 3 seconds. Click anywhere on the panel to force immediate refresh.

## 4. Deploy Contract

### Location

In GUI: Click "Deploy Contract" in left sidebar
In CLI: Option 1

### Purpose

Compiles and deploys the VehicleOwnership smart contract to Ganache blockchain. Required before using any other feature.

### Step-by-Step Guide

1. Ensure Ganache is running (http://127.0.0.1:7545)
2. Navigate to "Deploy Contract" panel
3. Result box shows: "Click Deploy to compile and deploy the smart contract"
4. Click "Deploy Contract" button
5. Status updates to: "Compiling Solidity contract... please wait"
6. Wait 30-60 seconds for compilation and deployment
7. Upon completion:
   - Result shows contract address (0x...)
   - Authority account displayed
   - Block number recorded

### Deployment Information

After successful deployment:

- Contract Address: Unique identifier for the deployed contract
- Authority Address: Your administrative wallet (always first Ganache account)
- Block Number: Blockchain block where deployment occurred
- TX Hash: Transaction identifier for deployment

Example Result:
```
Contract deployed at: 0x1234567890abcdef1234567890abcdef12345678
Authority: 0xabc1234567890abcdef1234567890abcdef123456
Block: 1
TX Hash: 0xabcd1234...
```

### Important Notes

- Deploy only once per session
- Deployment costs gas (free on Ganache)
- Contract address is permanent for this Ganache instance
- Cannot modify or delete contract after deployment

### Troubleshooting Deployment

If deployment fails:

- Error: "Unable to connect to Ganache" - Start Ganache
- Error: "No unlocked Ganache accounts" - Ganache not responding properly
- Hangs on "Compiling..." - Wait longer (compilation takes time)
- Repeated attempts: First deployment may take 1-2 minutes

## 5. Register Vehicle

### Location

In GUI: Click "Register Vehicle" in left sidebar
In CLI: Option 2

### Purpose

Records a new vehicle on the blockchain. Creates permanent record with brand, model, and owner information.

### Step-by-Step Guide

1. Navigate to "Register Vehicle" panel
2. Fill in required fields:

   **Vehicle ID Field**
   - Format: VIN (Vehicle Identification Number) or custom alphanumeric
   - Examples: "VIN123", "CAR001", "TRUCK_2024"
   - Validation: 3-100 characters
   - Status badge shows validation result:
     - Green "VIN": Standard 17-character VIN format
     - Orange "CUSTOM": Valid but non-standard format
     - Red "INVALID": Does not meet requirements

   **Brand Field**
   - Example: "Toyota"
   - Required: Yes
   - Cannot be empty

   **Model Field**
   - Example: "Corolla"
   - Required: Yes
   - Cannot be empty

   **Owner Address Field**
   - Format: Ethereum address starting with 0x
   - Example: "0x1234567890abcdef..."
   - Must be: Valid Ganache unlocked account
   - Tip: Available accounts shown in Dashboard

3. Click "Register Vehicle" button
4. Status shows: "Sending transaction..."
5. Upon confirmation:
   - Vehicle ID confirmed
   - Owner address recorded
   - TX Hash displayed
   - Block number recorded
   - Vehicle now in blockchain

### Registration Information Recorded

Once registered, vehicle data includes:

- Vehicle ID: Unique identifier
- Brand: Manufacturer
- Model: Vehicle model
- Current Owner: Ethereum address
- Registered At: Timestamp (block timestamp)
- Registration Block: Block number

### Important Notes

- Registration is permanent and cannot be deleted
- Owner must be a valid Ganache account
- Vehicle ID must be unique (cannot register same ID twice)
- All data is publicly readable on blockchain
- Generates audit log entry

### Registration Workflow

Typical workflow for multiple vehicles:

1. Deploy contract (once)
2. Register vehicle 1 (Authority account)
3. Register vehicle 2 (Authority account)
4. Transfer vehicle 1 to Owner account
5. Transfer vehicle 2 to different Owner account
6. Now ready for ownership transfers and queries

## 6. Transfer Ownership

### Location

In GUI: Click "Transfer Ownership" in left sidebar
In CLI: Option 3

### Purpose

Transfers vehicle ownership from current owner to new owner. Creates immutable ownership change record on blockchain.

### Step-by-Step Guide

1. Navigate to "Transfer Ownership" panel
2. Fill in required fields:

   **Vehicle ID Field**
   - Enter the ID of vehicle to transfer
   - Example: "CAR001"
   - Must match registered vehicle ID
   - If invalid: "Vehicle does not exist" error

   **Current Owner Address Field**
   - Address that currently owns the vehicle
   - Must be valid Ganache account
   - If wrong: "Sender account not recognized" error

   **New Owner Address Field**
   - Address of intended new owner
   - Must be valid Ganache account and different from current owner
   - Cannot be same as current owner: "New owner must be different" error

3. Verify all addresses are correct
4. Click "Transfer Ownership" button
5. Status shows: "Sending transaction..."
6. Upon confirmation:
   - Transfer completed
   - Old owner shown
   - New owner confirmed
   - TX Hash displayed
   - Block number recorded
   - Ownership history updated

### Transfer Information

After successful transfer:

- Vehicle ID: Transferred vehicle
- Previous Owner: Old owner address
- New Owner: New owner address
- TX Hash: Transaction identifier
- Block Number: Confirmation block
- Timestamp: Time of transfer

### Important Notes

- Both addresses must be valid Ganache accounts
- Current owner must match vehicle's actual owner
- New owner must be different from current owner
- Transfer is irreversible (immutable on blockchain)
- Creates entry in ownership history
- Generates audit log entry

### Permission Verification

Before transfer, system verifies:

1. Current owner address is valid
2. Current owner actually owns the vehicle
3. New owner address is valid and different
4. Both are unlocked Ganache accounts

If any check fails: Transaction rejected with specific error message.

### Multi-Step Transfer

Example: Transferring vehicle through multiple owners

1. Register: Authority owns CAR001
2. Transfer: CAR001 Authority -> Owner1
3. Query: Verify Owner1 is current owner
4. Transfer: CAR001 Owner1 -> Owner2
5. Query: Verify Owner2 is current owner
6. View History: Shows: Authority -> Owner1 -> Owner2

## 7. Verify Owner

### Location

In GUI: Click "Verify Owner" in left sidebar
In CLI: Option 4

### Purpose

Queries the current owner of a vehicle. Read-only operation requiring no permissions.

### Step-by-Step Guide

1. Navigate to "Verify Owner" panel
2. Enter Vehicle ID
   - Example: "CAR001"
   - Must match registered vehicle ID
3. Click "Verify Owner" button
4. Result displays: Current owner address

### Verification Result

Upon successful verification:

```
Current owner of 'CAR001':

  0x1234567890abcdef1234567890abcdef12345678
```

### Important Notes

- No permission required: Any user can verify
- No gas cost: Read-only blockchain query
- No transaction created
- Instantaneous response
- Cannot verify non-existent vehicle: "Vehicle not found" error

### Use Cases

- Insurance companies verifying policy owner
- Police checking registered owner
- Third parties confirming vehicle status
- Personal verification of ownership

## 8. Vehicle Details

### Location

In GUI: Click "Vehicle Details" in left sidebar
In CLI: Option 5

### Purpose

Retrieves and displays all recorded information for a vehicle in human-readable format.

### Step-by-Step Guide

1. Navigate to "Vehicle Details" panel
2. Enter Vehicle ID
   - Example: "CAR001"
3. Click "Fetch Details" button
4. Result displays comprehensive vehicle information

### Detail Information Displayed

```
Vehicle ID      :  CAR001
Brand           :  Toyota
Model           :  Corolla
Owner           :  0x1234567890abcdef1234567890abcdef12345678
Registered      :  2026-05-11 15:30:45 UTC
```

Field Explanations:

- **Vehicle ID**: Unique identifier used in system
- **Brand**: Manufacturer name
- **Model**: Vehicle model name
- **Owner**: Current owner's wallet address
- **Registered**: Date and time when vehicle was first registered (UTC timezone)

### Important Notes

- Requires valid vehicle ID
- Shows current state only (not historical)
- No permission required
- Instantaneous query
- Useful for verification and record-keeping

## 9. Ownership History

### Location

In GUI: Click "Ownership History" in left sidebar
In CLI: Option 6

### Purpose

Displays complete chronological record of all ownership transfers for a vehicle. Shows full audit trail with timestamps.

### Step-by-Step Guide

1. Navigate to "Ownership History" panel
2. Enter Vehicle ID
   - Example: "CAR001"
3. Click "Fetch History" button
4. Result displays all ownership records

### History Format

Example output:

```
History for 'CAR001'  —  3 record(s)
───────────────────────────────────

[1] REGISTERED
     Address  :  0xabc1234567890abcdef1234567890abcdef123456
     Time     :  2026-05-11 15:30:45 UTC

[2] TRANSFERRED
     Address  :  0x1234567890abcdef1234567890abcdef12345678
     Time     :  2026-05-11 15:35:20 UTC

[3] TRANSFERRED
     Address  :  0xdef1234567890abcdef1234567890abcdef123456
     Time     :  2026-05-11 15:40:10 UTC
```

### Record Explanation

- **Number**: Sequential number (1, 2, 3...)
- **Type**: REGISTERED (initial) or TRANSFERRED (transfer)
- **Address**: Owner address at that point in history
- **Time**: Date and time of the record (UTC timezone)

### Important Notes

- Shows complete ownership chain
- Records are immutable (cannot be modified)
- Latest record is current owner
- Useful for verifying vehicle provenance
- Timestamps prove when ownership changed

### History Interpretation

Reading the history:

1. First record: Vehicle was registered to this address
2. Subsequent records: Each transfer creates new record
3. Latest record: Current owner
4. Timeline: Shows how long each owner held vehicle

## 10. PDF Certificate

### Location

In GUI: Click "PDF Certificate" in left sidebar
In CLI: Option 7

### Purpose

Generates printable blockchain-verified ownership certificate. Includes QR code linking to blockchain proof.

### Step-by-Step Guide

1. Navigate to "PDF Certificate" panel
2. Enter Vehicle ID
   - Example: "CAR001"
3. Click "Generate PDF" button
4. Status shows: "Generating certificate..."
5. Upon completion:
   - Result shows success message
   - Certificate saved to `certificates/` directory
   - Filename format: `vehicle_ID_YYYY-MM-DD_HHMMSS.pdf`
   - File path displayed for reference

### Certificate Contents

Generated PDF includes:

1. **Header**
   - Certificate title
   - Blockchain verification badge

2. **Vehicle Information**
   - Vehicle ID
   - Brand and Model
   - Registration date

3. **Current Owner**
   - Owner address
   - Ownership since date

4. **Ownership History Table**
   - Previous owners
   - Transfer dates
   - Complete chain of custody

5. **Blockchain Proof**
   - Smart contract address
   - Verification block number
   - Current blockchain confirmation
   - Network: Ganache (Private Ethereum)

6. **QR Code**
   - Links to blockchain verification
   - Scannable for digital verification

### Certificate Files

Certificates are saved in: `certificates/` directory

File naming:
- CAR001_2026-05-11_153045.pdf
- Parts: [VehicleID]_[DATE]_[TIME].pdf

### Using the Certificate

Typical use cases:

- Print for vehicle documentation
- Email to insurance company
- Present to regulatory authority
- Store as proof of ownership
- Share with potential buyers

### Important Notes

- PDF generation requires reportlab library
- Requires vehicle to have registration history
- Creates persistent file (not deleted after generation)
- Can generate multiple certificates per vehicle
- Each certificate timestamped

## 11. Audit Log

### Location

In GUI: Click "Audit Log" in left sidebar
In CLI: Not available in CLI

### Purpose

Displays and manages the audit log of all blockchain actions. Provides comprehensive record for compliance and verification.

### Step-by-Step Guide

1. Navigate to "Audit Log" panel
2. Click "Refresh" button to load latest records
3. Log displays in table format

### Audit Log Columns

```
TIMESTAMP                ACTION          VEHICLE ID           TX HASH
2026-05-11 22:58:04     VERIFIER_CONFIRM  1                   ...
2026-05-11 22:58:18     SET_VERIFIER                          ...
2026-05-11 22:57:57     VERIFY            1                   ...
2026-05-11 22:57:39     REGISTER          1                   0x929...
2026-05-11 22:57:39     DEPLOY                                ...
```

### Log Field Descriptions

- **TIMESTAMP**: Date and time of action (YYYY-MM-DD HH:MM:SS)
- **ACTION**: Type of operation performed
- **VEHICLE ID**: Related vehicle (if applicable)
- **TX HASH**: Transaction identifier (first 18 characters)

### Action Types

- **DEPLOY**: Smart contract deployment
- **REGISTER**: New vehicle registration
- **TRANSFER**: Ownership transfer
- **VERIFY**: Owner verification query
- **SET_VERIFIER**: Verifier role grant/revoke
- **VERIFIER_CONFIRM**: Official verification by verifier

### Audit Log Buttons

- **Refresh**: Reload log entries from disk
- **Open CSV**: Opens audit_log.csv in default spreadsheet application

### CSV File Details

Full audit log stored in: `audit_log.csv`

Contains columns:
- timestamp
- action
- vehicle_id
- actor_address
- tx_hash
- block_number
- notes

### Important Notes

- Audit log is append-only (cannot delete entries)
- Records every blockchain action
- Useful for compliance and auditing
- CSV format for easy data analysis
- Located in project root or next to VehicleChain.exe

## 12. Set Verifier

### Location

In GUI: Click "Set Verifier" in left sidebar
In CLI: Option 7

### Purpose

Grants or revokes the Verifier role for an address. Only Authority can perform this operation.

### Who Can Use This Feature

Only the Authority account (first Ganache account) can set verifiers.

### Step-by-Step Guide

1. Navigate to "Set Verifier" panel
2. Enter Wallet Address
   - Address to grant or revoke verifier role
   - Must be valid Ganache account
   - Example: "0x1234567890abcdef..."

3. Set the checkbox:
   - Checked: Grant verifier access
   - Unchecked: Revoke verifier access

4. Click "Apply" button
5. Status shows: "Sending transaction..."
6. Upon confirmation:
   - Action performed (granted or revoked)
   - TX Hash displayed
   - Block number recorded

### Verifier Role Explanation

Verifiers are trusted third parties authorized to:

- Create official ownership confirmations
- Generate immutable verification events on blockchain
- Create audit trail for regulatory compliance
- Build trust with transparent record-keeping

Examples of verifiers:

- Insurance companies
- Police departments
- DMV officials
- Government agencies
- Authorized inspectors

### Granting Verifier Access

Workflow to enable a verifier:

1. Obtain the verifier's wallet address
2. Navigate to "Set Verifier" panel
3. Enter address in field
4. Ensure "Grant Access" checkbox is checked
5. Click "Apply"
6. Verifier status: Now can use verifier functions

### Revoking Verifier Access

To remove verifier privileges:

1. Navigate to "Set Verifier" panel
2. Enter the verifier's address
3. Uncheck "Grant Access" checkbox
4. Click "Apply"
5. Verifier status: Access revoked, cannot verify anymore

### Important Notes

- Authority can grant/revoke at any time
- Verifier role change is immediate (on blockchain)
- Creates transaction and audit log entry
- Revocation prevents future verifications (past remain valid)
- Address must be valid Ganache account

### Permission Verification

System checks:

1. Caller is Authority account (first Ganache)
2. Address is valid Ethereum address
3. Transaction is signed correctly
4. Gas is available

If checks fail: Transaction rejected with reason.

## 13. Verifier Confirmation

### Location

In GUI: Click "Verifier Confirmation" in left sidebar
In CLI: Option 8

### Purpose

Verifiers create official ownership confirmations with audit trail. Creates immutable record for compliance and transparency.

### Who Can Use This Feature

Only addresses with active Verifier role (granted by Authority).

### Step-by-Step Guide

1. Verify you have Verifier role (Authority granted access)
2. Navigate to "Verifier Confirmation" panel
3. Fill in required fields:

   **Vehicle ID Field**
   - Vehicle to confirm
   - Example: "CAR001"
   - Must be registered vehicle

   **Your Verifier Address Field**
   - Your wallet address (must be authorized verifier)
   - Must have active verifier role
   - Verify this matches your address

4. Click "Confirm Ownership" button
5. Status shows: "Sending transaction..."
6. Upon confirmation:
   - Verification recorded on blockchain
   - Current owner confirmed
   - TX Hash displayed
   - Block number recorded
   - "Verification confirmed and recorded" message

### Verification Information

After successful verification:

```
Verification confirmed and recorded.

  Vehicle ID : CAR001
  Owner      : 0x1234567890abcdef1234567890abcdef12345678
  Verifier   : 0xdef1234567890abcdef1234567890abcdef123456
  TX Hash    : 0xabcd1234...
  Block #    : 45
```

### What Gets Recorded

On blockchain, creates immutable record containing:

- Vehicle ID: Which vehicle verified
- Verifier Address: Who confirmed
- Owner Address: Current owner at verification time
- Timestamp: When verification occurred
- Block Number: Blockchain confirmation
- Transaction Hash: Unique identifier

### Use Cases

Typical verification scenarios:

1. **Insurance Verification**
   - Insurance company verifies owner before issuing policy
   - Creates proof for compliance

2. **Police Checkpoint**
   - Police verify vehicle ownership at checkpoint
   - Creates audit trail

3. **Government Registration**
   - DMV verifies ownership for registration
   - Transparent record for future audits

4. **Buyer Verification**
   - Seller has third party verify ownership before sale
   - Buyer trusts blockchain proof

### Important Notes

- Must have active Verifier role
- Creates immutable blockchain record
- Generates audit log entry
- Cannot verify non-existent vehicle
- Cannot verify without authorization

### Permission Verification

System checks:

1. Address has active Verifier role
2. Vehicle ID is valid and registered
3. Address is valid Ganache account
4. Transaction has sufficient gas

If checks fail: Transaction rejected with specific error.

## 14. Common Workflows

### Workflow 1: New Vehicle Registration and Initial Transfer

Timeline: 10 minutes

Steps:

1. Start Ganache (terminal 1)
2. Launch VehicleChain GUI (terminal 2)
3. Deploy contract
   - Panel: "Deploy Contract"
   - Note Authority address shown
   - Note contract address

4. Register vehicle
   - Panel: "Register Vehicle"
   - Vehicle ID: "CAR001"
   - Brand: "Toyota"
   - Model: "Corolla"
   - Owner: Use Account 0 (Authority)

5. Transfer to Owner 1
   - Panel: "Transfer Ownership"
   - Vehicle ID: "CAR001"
   - Current Owner: Account 0 address
   - New Owner: Account 1 address

6. Verify ownership
   - Panel: "Verify Owner"
   - Vehicle ID: "CAR001"
   - Result: Should show Account 1 address

7. View history
   - Panel: "Ownership History"
   - Vehicle ID: "CAR001"
   - Shows: Account 0 registered, Account 1 transferred

### Workflow 2: Multi-Owner Transfer Chain

Timeline: 20 minutes

Steps:

1. Register vehicles (from Workflow 1)
   - CAR001, CAR002, CAR003

2. Create transfer chain
   - CAR001: Acct0 -> Acct1 -> Acct2 -> Acct3
   - CAR002: Acct0 -> Acct2 -> Acct4
   - CAR003: Acct0 -> Acct1 -> Acct4

3. Verify endpoints
   - CAR001 should show Acct3
   - CAR002 should show Acct4
   - CAR003 should show Acct4

4. Generate certificates
   - For each vehicle
   - Creates PDF records
   - Store for documentation

### Workflow 3: Verifier Setup and Verification

Timeline: 15 minutes

Steps:

1. Deploy and register vehicle (from Workflow 1)

2. Authorize verifier
   - Panel: "Set Verifier"
   - Address: Account 5 address
   - Check "Grant Access"
   - Click "Apply"

3. Verify ownership as verifier
   - Panel: "Verifier Confirmation"
   - Vehicle ID: "CAR001"
   - Your Verifier Address: Account 5 address
   - Click "Confirm Ownership"

4. Check audit log
   - Panel: "Audit Log"
   - Should show SET_VERIFIER entry
   - Should show VERIFIER_CONFIRM entry

### Workflow 4: Complete Vehicle Lifecycle

Timeline: 30 minutes

Steps:

1. Setup
   - Deploy contract
   - Register vehicle CAR001
   - Transfer to Owner (Account 1)

2. Verification
   - Authorize Verifier (Account 2)
   - Verifier confirms ownership

3. Transfer chain
   - Owner transfers to Buyer (Account 3)
   - Verify new owner

4. Second verification
   - Verifier confirms new owner

5. Documentation
   - View complete history
   - Generate certificate
   - Review audit log

## 15. Troubleshooting

### Connection Issues

#### "Unable to connect to Ganache"

Problem: Application cannot reach Ganache at http://127.0.0.1:7545

Solutions:

1. Start Ganache in terminal:
   ```bash
   ganache --deterministic
   ```

2. Verify Ganache is listening:
   - Check terminal output for "Listening on 127.0.0.1:7545"

3. Check firewall:
   - Ensure port 7545 is not blocked
   - Disable firewall temporarily for testing

4. Verify network:
   - Ensure localhost/127.0.0.1 is accessible
   - Try: `ping 127.0.0.1`

5. Restart both applications:
   - Close VehicleChain
   - Restart Ganache
   - Relaunch VehicleChain

#### Application Hangs on Startup

Problem: GUI takes very long to start or shows "Connecting..."

Solutions:

1. Check Ganache status
   - Ensure Ganache is running
   - Check for errors in Ganache terminal

2. Wait longer
   - Initial connection can take 30+ seconds
   - First compilation takes extra time

3. Force timeout
   - Close application
   - Wait 10 seconds
   - Relaunch

### Address and Account Issues

#### "Sender account not recognized"

Problem: Address provided is not a valid Ganache account

Solutions:

1. Check address format
   - Must start with "0x"
   - Must be exactly 42 characters
   - Cannot include lowercase/uppercase mix (use lowercase)

2. Copy from Dashboard
   - Navigate to Dashboard
   - Copy address from account list (exact format)
   - Paste into form field

3. Use standard accounts
   - Account 0: 0x1234567890... (Authority)
   - Account 1: 0x5678901234...
   - See Dashboard for complete list

4. Verify account is unlocked
   - Ganache by default unlocks accounts 0-9
   - Check Ganache startup output

#### "New owner must be different from current owner"

Problem: Trying to transfer to same address

Solutions:

1. Verify addresses are different
   - Copy-paste can duplicate
   - Check for extra spaces

2. Use different account
   - Select different address from Dashboard
   - Verify in Ownership History

#### "Address is not an unlocked Ganache account"

Problem: Address is valid but not available in current Ganache instance

Solutions:

1. Check address against Dashboard
   - Only accounts shown in Dashboard are available
   - Might be from different Ganache instance

2. Reset Ganache
   - Stop Ganache
   - Restart with `ganache --deterministic`
   - Uses default accounts 0-9

3. Verify Ganache instance
   - Only one Ganache should run on port 7545
   - Close all other Ganache instances

### Vehicle and Registration Issues

#### "Vehicle not found"

Problem: Trying to access vehicle that doesn't exist

Solutions:

1. Check vehicle ID spelling
   - Case-sensitive
   - No extra spaces
   - Must match exactly

2. Verify vehicle is registered
   - Navigate to Ownership History
   - Try vehicle ID that worked before
   - Check result shows "No history found" or error

3. Register vehicle first
   - Must register before transferring
   - Navigate to "Register Vehicle"
   - Create new vehicle entry

#### "Vehicle already exists"

Problem: Trying to register vehicle ID that already exists

Solutions:

1. Use different vehicle ID
   - Append number: "CAR001_v2"
   - Use different format: "VEHICLE_001"

2. Verify uniqueness
   - Try different ID first to test
   - List out IDs in use

3. Check History
   - Ownership History shows if registered
   - Use new ID if conflict detected

### Transaction Issues

#### "Insufficient funds for gas"

Problem: Account has no balance

Solutions:

1. Use fresh Ganache instance
   - Accounts start with 100 ETH
   - Restart: `ganache --deterministic`

2. Use Account 0
   - Account 0 usually has sufficient balance
   - Navigate to Dashboard to check balance

3. Check balance in Dashboard
   - Navigate to Dashboard
   - View account balances
   - Use account with non-zero balance

#### "Transaction reverted"

Problem: Smart contract rejected the transaction

Solutions:

1. Check permission
   - Only Authority can register/set verifier
   - Only Owner can transfer
   - Only Verifier can verify

2. Verify constraints
   - Vehicle must exist for transfer
   - Owner addresses must be different
   - Addresses must be valid

3. Check input data
   - Vehicle ID format valid
   - Addresses correct format
   - All required fields filled

### PDF Certificate Issues

#### "Certificate generation failed"

Problem: PDF creation encountered error

Solutions:

1. Install reportlab
   ```bash
   pip install reportlab
   ```

2. Check disk space
   - Ensure space available in project directory
   - Certificates stored in `certificates/` folder

3. Check permissions
   - Ensure write permission to project folder
   - Not running from read-only location

4. Verify vehicle data
   - Vehicle must exist
   - Vehicle must have history

#### "File already exists"

Problem: Certificate with same timestamp already created

Solutions:

1. Wait a second and regenerate
   - Filenames include timestamp
   - Regenerating creates new timestamp

2. Check certificates folder
   - Navigate to `certificates/` folder
   - View existing certificates

### GUI Specific Issues

#### GUI Freezes

Problem: Application becomes unresponsive

Solutions:

1. Operation in progress
   - Long operations (compilation, deployment) take time
   - Wait for completion

2. Force quit and restart
   - Close application
   - Wait 10 seconds
   - Relaunch VehicleChain

3. Check resources
   - Close other applications
   - Restart computer if persistent

#### Result Box Shows Nothing

Problem: Operation completes but no result displayed

Solutions:

1. Scroll in result box
   - Result might be scrolled out of view
   - Scroll to bottom of result area

2. Operation failed silently
   - Check connection status (bottom-left)
   - Try operation again

3. Refresh or navigate away
   - Click different panel
   - Click same panel again
   - Try operation fresh

### CLI Specific Issues

#### Menu Navigation

Problem: Typing option doesn't work

Solutions:

1. Type single digit
   - Enter number (1-9) and press Enter
   - Example: Type "1" then press Enter

2. Press Enter after input
   - Command doesn't execute without Enter key

3. Use correct range
   - Valid options: 1-9
   - Invalid numbers show error message

#### Output Formatting

Problem: Text appears cut off or jumbled

Solutions:

1. Expand terminal window
   - Make terminal wider
   - Full text should display

2. Scroll up for output
   - Use scrollbar or Page Up
   - Results might be above current view

3. Check terminal encoding
   - Ensure UTF-8 encoding
   - Special characters should render

### Data and File Issues

#### Audit Log Not Updating

Problem: Audit log shows old data

Solutions:

1. Click Refresh button
   - Manual refresh loads latest entries
   - Auto-refresh happens periodically

2. Check file permissions
   - audit_log.csv must be readable
   - Not corrupted or locked

3. Close other applications
   - Spreadsheet app might lock file
   - Close before opening audit log

#### Certificate Not Saving

Problem: PDF generated but file not found

Solutions:

1. Check certificates folder
   - Location: Project root/certificates/
   - Create folder if doesn't exist: `mkdir certificates`

2. Verify file system
   - Write permission to directory
   - Sufficient disk space
   - Not on read-only drive

3. Check filename
   - Format: vehicle_ID_timestamp.pdf
   - Example: vehicle_CAR001_2026-05-11_153045.pdf

### Performance Issues

#### Slow Deployment

Problem: "Compiling Solidity..." takes very long

Solutions:

1. This is normal
   - Compilation takes 30-60 seconds
   - Wait for completion

2. Computer performance
   - Close heavy applications
   - Free up memory
   - Restart computer

3. Solc caching
   - Subsequent compilations faster
   - First use always slowest

#### Slow Query Results

Problem: "Verify Owner" or history queries take long

Solutions:

1. Check connection
   - Ensure Ganache responsive
   - Ping Ganache in separate terminal

2. Network latency
   - Usually instant on localhost
   - High latency indicates network issue

3. Ganache performance
   - Restart Ganache if many transactions
   - Reset with: `ganache --deterministic`

### General Debugging Steps

When issues occur, follow these steps:

1. Check Connection Status
   - Navigate to Dashboard
   - Verify "Connected, block #XX" message
   - If disconnected, check Ganache

2. Verify Input Data
   - Check field contents
   - Copy values from Dashboard when possible
   - Verify exact format required

3. Check Recent Transactions
   - View Audit Log
   - Identify what actions worked/failed
   - Pattern might indicate issue

4. Try Again
   - Simple operations often work on retry
   - Wait between attempts
   - Ensure Ganache still running

5. Restart Application
   - Close VehicleChain
   - Restart Ganache
   - Relaunch VehicleChain fresh

6. Check System Resources
   - Ensure sufficient disk space
   - Close memory-heavy applications
   - Verify Python version: 3.10+

7. Collect Error Details
   - Note exact error message
   - Check console output
   - Document steps to reproduce

## Support and Additional Information

### Files and Directories

Main project structure:

```
vehiclechain/          - Application source code
contracts/             - Smart contract files
certificates/          - Generated PDF certificates
audit_log.csv          - Audit trail database
README.md              - Project overview
USER_MANUAL.md         - This file
requirements.txt       - Python dependencies
VehicleChain.spec      - Build configuration
```

### Important Addresses

After deployment:

- Authority: First Ganache account (Account 0)
- Deployed Contract: Shown after "Deploy Contract"
- Smart Contract File: contracts/VehicleOwnership.sol

### Keyboard Shortcuts (GUI)

- Alt+F4: Close application
- Ctrl+L: Focus address bar (browser-like)
- Tab: Switch between input fields
- Enter: Submit form (equivalent to clicking button)

### Command Reference (CLI)

```
Option 1: Deploy contract (do this first)
Option 2: Register a new vehicle
Option 3: Transfer ownership to new owner
Option 4: Check current owner by vehicle ID
Option 5: Show full vehicle details
Option 6: Show ownership history
Option 7: Set verifier role
Option 8: Verifier confirmation (create audit trail)
Option 9: Exit
```

### Best Practices

1. Always deploy contract first
2. Use Dashboard to copy addresses (exact format)
3. Document vehicle IDs and ownership chains
4. Check Audit Log for transaction verification
5. Generate certificates for important vehicles
6. Use descriptive vehicle IDs (not just numbers)
7. Verify owners before major operations
8. Keep Ganache running throughout session
9. Close application properly before shutdown
10. Restart Ganache for fresh instance

### When Reporting Issues

Include:

- Exact error message
- Steps to reproduce
- Expected vs. actual behavior
- Ganache version and status
- Python version
- Operating system
- Screenshot if GUI-related

---

End of User Manual

For additional help, see README.md or check Ganache documentation.
