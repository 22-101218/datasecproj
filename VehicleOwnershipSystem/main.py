"""
Blockchain-Based Vehicle Ownership System
A CLI tool for managing vehicle registration and ownership on Ganache blockchain.
Requires: Ganache running at http://127.0.0.1:7545
"""

from web3 import Web3
from solcx import compile_standard, install_solc
from pathlib import Path
from datetime import datetime

GANACHE_URL = "http://127.0.0.1:7545"
CHAIN_ID = 1337
SOLC_VERSION = "0.8.19"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    raise RuntimeError(f"Unable to connect to Ganache at {GANACHE_URL}")

accounts = w3.eth.accounts
if not accounts:
    raise RuntimeError("No unlocked Ganache accounts found")

authority_address = accounts[0]
contract_abi = None
contract_bytecode = None
contract_instance = None


def compile_contract():
    """Compile the Solidity smart contract."""
    install_solc(SOLC_VERSION)
    contract_path = Path(__file__).parent / "contracts" / "VehicleOwnership.sol"
    source = contract_path.read_text(encoding="utf-8")
    
    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {"VehicleOwnership.sol": {"content": source}},
            "settings": {
                "evmVersion": "paris",
                "outputSelection": {
                    "*": {"*": ["abi", "evm.bytecode"]}
                },
            },
        },
        solc_version=SOLC_VERSION,
    )
    
    contract_data = compiled["contracts"]["VehicleOwnership.sol"]["VehicleOwnership"]
    abi = contract_data["abi"]
    bytecode = contract_data["evm"]["bytecode"]["object"]
    return abi, bytecode


def deploy_contract():
    """Deploy the smart contract to Ganache."""
    global contract_abi, contract_bytecode, contract_instance
    
    print("\n⏳ Compiling contract...")
    contract_abi, contract_bytecode = compile_contract()
    
    print("⏳ Deploying to Ganache...")
    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    nonce = w3.eth.get_transaction_count(authority_address)
    
    tx = {
        "from": authority_address,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "gas": 6_000_000,
        "gasPrice": w3.to_wei("20", "gwei"),
    }
    
    tx_hash = contract.constructor().transact(tx)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_instance = w3.eth.contract(
        address=Web3.to_checksum_address(receipt.contractAddress),
        abi=contract_abi,
    )
    
    print(f"✅ Contract deployed at: {receipt.contractAddress}")
    return receipt.contractAddress


def get_contract():
    """Get the deployed contract instance."""
    if contract_instance is None:
        raise RuntimeError("Contract not deployed. Deploy first.")
    return contract_instance


def print_tx_summary(title, tx_hash):
    """Print transaction details."""
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    tx_details = w3.eth.get_transaction(tx_hash)
    to_address = tx_receipt.contractAddress or tx_details["to"]

    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"TX HASH:        {w3.to_hex(tx_hash)}")
    print(f"FROM:           {tx_details['from']}")
    print(f"TO:             {to_address}")
    print(f"GAS USED:       {tx_receipt.gasUsed}")
    print(f"GAS PRICE:      {w3.from_wei(tx_details['gasPrice'], 'gwei')} Gwei")
    print(f"BLOCK NUMBER:   {tx_receipt.blockNumber}")
    print(f"{'='*60}\n")


def register_vehicle():
    """Register a new vehicle (Authority only)."""
    contract = get_contract()
    
    vehicle_id = input("\n📝 Vehicle ID (e.g., VIN or custom ID): ").strip()
    brand = input("🏢 Brand (e.g., Toyota): ").strip()
    model = input("🚗 Model (e.g., Corolla): ").strip()
    owner = input("👤 Owner wallet address (0x...): ").strip()
    
    nonce = w3.eth.get_transaction_count(authority_address)
    tx = {
        "from": authority_address,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "gas": 500_000,
        "gasPrice": w3.to_wei("20", "gwei"),
    }
    
    tx_hash = contract.functions.registerVehicle(
        vehicle_id, brand, model, Web3.to_checksum_address(owner)
    ).transact(tx)
    
    print_tx_summary(f"VEHICLE REGISTERED: {vehicle_id}", tx_hash)


def transfer_ownership():
    """Transfer vehicle ownership (Owner only)."""
    contract = get_contract()
    
    vehicle_id = input("\n📝 Vehicle ID: ").strip()
    new_owner = input("👤 New owner wallet address (0x...): ").strip()
    owner_address = input("👤 Current owner wallet address (0x...): ").strip()
    
    nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(owner_address))
    tx = {
        "from": Web3.to_checksum_address(owner_address),
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "gas": 500_000,
        "gasPrice": w3.to_wei("20", "gwei"),
    }
    
    tx_hash = contract.functions.transferOwnership(
        vehicle_id, Web3.to_checksum_address(new_owner)
    ).transact(tx)
    
    print_tx_summary(f"OWNERSHIP TRANSFERRED: {vehicle_id}", tx_hash)


def verify_owner():
    """Verify current owner of a vehicle."""
    contract = get_contract()
    
    vehicle_id = input("\n📝 Vehicle ID: ").strip()
    owner = contract.functions.verifyCurrentOwner(vehicle_id).call()
    
    print(f"\n✅ Current Owner: {owner}")


def get_vehicle_details():
    """Retrieve vehicle details."""
    contract = get_contract()
    
    vehicle_id = input("\n📝 Vehicle ID: ").strip()
    vehicle = contract.functions.getVehicle(vehicle_id).call()
    
    print(f"\n{'='*60}")
    print(f"VEHICLE DETAILS: {vehicle_id}")
    print(f"{'='*60}")
    print(f"Brand:       {vehicle[1]}")
    print(f"Model:       {vehicle[2]}")
    print(f"Owner:       {vehicle[3]}")
    print(f"Registered:  {datetime.utcfromtimestamp(vehicle[4]).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*60}\n")


def get_history():
    """Retrieve ownership history."""
    contract = get_contract()
    
    vehicle_id = input("\n📝 Vehicle ID: ").strip()
    history = contract.functions.getOwnershipHistory(vehicle_id).call()
    
    print(f"\n{'='*60}")
    print(f"OWNERSHIP HISTORY: {vehicle_id}")
    print(f"{'='*60}")
    for i, record in enumerate(history):
        event = "REGISTERED" if i == 0 else "TRANSFERRED"
        timestamp = datetime.utcfromtimestamp(record[1]).strftime('%Y-%m-%d %H:%M:%S UTC')
        print(f"{i+1}. {event}")
        print(f"   Owner: {record[0]}")
        print(f"   Date:  {timestamp}")
    print(f"{'='*60}\n")


def main():
    """Main CLI menu."""
    print("\n" + "="*60)
    print("🚗 BLOCKCHAIN-BASED VEHICLE OWNERSHIP SYSTEM")
    print("="*60)
    
    while True:
        print("\n📋 MENU:")
        print("1. Deploy Contract")
        print("2. Register Vehicle (Authority)")
        print("3. Transfer Ownership (Owner)")
        print("4. Verify Owner")
        print("5. View Vehicle Details")
        print("6. View Ownership History")
        print("7. Exit")
        
        choice = input("\n👉 Enter choice (1-7): ").strip()
        
        try:
            if choice == "1":
                deploy_contract()
            elif choice == "2":
                register_vehicle()
            elif choice == "3":
                transfer_ownership()
            elif choice == "4":
                verify_owner()
            elif choice == "5":
                get_vehicle_details()
            elif choice == "6":
                get_history()
            elif choice == "7":
                print("\n👋 Goodbye!\n")
                break
            else:
                print("❌ Invalid choice. Please try again.")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
