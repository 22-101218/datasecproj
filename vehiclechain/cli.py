"""Terminal menu for VehicleChain (same workflow as the GUI)."""

from typing import Optional

from web3 import Web3

from vehiclechain.vin_utils import validate_vehicle_id

try:
    import vehiclechain.blockchain as bc
    _BLOCKCHAIN_ERROR: Optional[Exception] = None
except Exception as exc:
    bc = None
    _BLOCKCHAIN_ERROR = exc


def _blockchain_error_text() -> str:
    if _BLOCKCHAIN_ERROR is not None:
        return str(_BLOCKCHAIN_ERROR)
    return "Ganache is not running or is unreachable."


def _require_blockchain() -> bool:
    if bc is None:
        print(f"Error: {_blockchain_error_text()}")
        return False
    try:
        if not bc.w3.is_connected():
            print("Error: Unable to connect to Ganache at http://127.0.0.1:7545")
            return False
    except Exception as exc:
        print(f"Error: {exc}")
        return False
    return True


def _require_vehicle_id(vehicle_id: str) -> bool:
    result = validate_vehicle_id(vehicle_id)
    if not result.valid:
        print(f"Error: {result.message}")
        return False
    return True


def _require_address(label: str, addr: str) -> bool:
    if not addr:
        print(f"Error: {label} is required.")
        return False
    if not Web3.is_address(addr):
        print(f"Error: {label} must be a valid 0x address.")
        return False
    return True


def _require_ganache_account(label: str, addr: str) -> bool:
    """Check if address is a valid unlocked Ganache account."""
    if not _require_address(label, addr):
        return False
    if not bc.is_valid_ganache_account(addr):
        print(f"Error: {label} is not an unlocked Ganache account. Check your address.")
        return False
    return True


def print_tx_summary(title, tx_hash):
    if not _require_blockchain():
        return
    try:
        tx_receipt = bc.w3.eth.wait_for_transaction_receipt(tx_hash)
        tx_details = bc.w3.eth.get_transaction(tx_hash)
        to_address = tx_receipt.contractAddress or tx_details["to"]

        print(f"\n{title}")
        print(f"TX HASH: {bc.w3.to_hex(tx_hash)}")
        print(f"SENDER ADDRESS: {tx_details['from']}")
        print(f"TO CONTRACT ADDRESS: {to_address}")
        print(f"VALUE: {bc.w3.from_wei(tx_details['value'], 'ether')} ETH")
        print(f"GAS USED: {tx_receipt.gasUsed}")
        print(f"GAS PRICE: {tx_details['gasPrice']}")
        print(f"GAS LIMIT: {tx_details['gas']}")
        print(f"MINED IN BLOCK: {tx_receipt.blockNumber}")
        print(f"BLOCK HASH: {bc.w3.to_hex(tx_receipt.blockHash)}")
    except Exception as exc:
        print(f"Error: Unable to fetch transaction details ({exc})")


def safe_run(action):
    try:
        action()
    except Exception as exc:
        error_msg = str(exc)
        if "sender account not recognized" in error_msg:
            print("Error: The sender account was not recognized. Check the address.")
        elif "insufficient funds" in error_msg.lower():
            print("Error: Insufficient funds for gas.")
        elif "revert" in error_msg.lower():
            print("Error: Transaction reverted. Check your inputs and permissions.")
        else:
            print(f"Error: {error_msg.split(chr(10))[0]}")


def deploy():
    if not _require_blockchain():
        return
    address = bc.deploy_contract()
    print(f"Contract deployed at: {address}")
    print("Next: choose 2 to register your first vehicle.")


def register():
    print("\nRegister Vehicle")
    print("Tip: owner must be a Ganache address (starts with 0x...)")
    vehicle_id = input("Vehicle ID (example VIN123): ").strip()
    brand = input("Brand (example Toyota): ").strip()
    model = input("Model (example Corolla): ").strip()
    owner = input("Owner wallet address (0x...): ").strip()
    if not _require_blockchain():
        return
    if not _require_vehicle_id(vehicle_id):
        return
    if not brand or not model:
        print("Error: Brand and model are required.")
        return
    if not _require_ganache_account("Owner address", owner):
        return
    tx_hash = bc.register_vehicle(vehicle_id, brand, model, owner)
    print_tx_summary("REGISTER VEHICLE", tx_hash)


def transfer():
    print("\nTransfer Ownership")
    print("Use valid Ganache addresses for both current and new owner.")
    vehicle_id = input("Vehicle ID: ").strip()
    current_owner_address = input("Current owner wallet address (0x...): ").strip()
    new_owner = input("New owner wallet address (0x...): ").strip()
    if not _require_blockchain():
        return
    if not _require_vehicle_id(vehicle_id):
        return
    if not _require_ganache_account("Current owner address", current_owner_address):
        return
    if not _require_ganache_account("New owner address", new_owner):
        return
    if current_owner_address.lower() == new_owner.lower():
        print("Error: New owner must be different from current owner.")
        return
    tx_hash = bc.transfer_ownership(
        vehicle_id=vehicle_id,
        new_owner=new_owner,
        current_owner_address=current_owner_address,
    )
    print_tx_summary("TRANSFER OWNERSHIP", tx_hash)


def owner():
    vehicle_id = input("Vehicle ID to check owner: ").strip()
    if not _require_blockchain():
        return
    if not _require_vehicle_id(vehicle_id):
        return
    current_owner = bc.verify_owner(vehicle_id)
    print(f"Current owner: {current_owner}")


def vehicle():
    vehicle_id = input("Vehicle ID to view details: ").strip()
    if not _require_blockchain():
        return
    if not _require_vehicle_id(vehicle_id):
        return
    data = bc.get_vehicle(vehicle_id)
    print(data)


def history():
    vehicle_id = input("Vehicle ID to view history: ").strip()
    if not _require_blockchain():
        return
    if not _require_vehicle_id(vehicle_id):
        return
    records = bc.get_history(vehicle_id)
    for index, record in enumerate(records, start=1):
        print(f"{index}. owner={record['owner']} transferred_at={record['transferred_at']}")


def verifier():
    verifier_address = input("Verifier wallet address (0x...): ").strip()
    allowed_input = input("Allow verifier? (yes/no): ").strip().lower()
    allowed = allowed_input in ("y", "yes", "1", "true")
    if not _require_blockchain():
        return
    if not _require_address("Verifier address", verifier_address):
        return
    tx_hash = bc.set_verifier(verifier_address, allowed)
    print_tx_summary("SET VERIFIER", tx_hash)


def verify_ownership_as_verifier():
    print("\nVerifier Confirmation (Create Audit Trail)")
    vehicle_id = input("Vehicle ID to verify: ").strip()
    verifier_address = input("Your verifier wallet address (0x...): ").strip()
    if not _require_blockchain():
        return
    if not _require_vehicle_id(vehicle_id):
        return
    if not _require_address("Verifier address", verifier_address):
        return
    try:
        owner = bc.verify_ownership_by_verifier(
            vehicle_id=vehicle_id,
            verifier_address=verifier_address,
        )
        print(f"✓ Verified! Current owner: {owner}")
        print("Verification event recorded on blockchain.")
    except Exception as exc:
        print(f"Error: {exc}")


def show_status():
    if bc is None:
        print(f"Blockchain unavailable: {_blockchain_error_text()}")
        return
    try:
        connected = bc.w3.is_connected()
        print(f"Connected: {connected}")
        if connected:
            print(f"Current block: {bc.w3.eth.block_number}")
            print(f"Accounts: {bc.w3.eth.accounts}")
        else:
            print("Ganache is not reachable. Start Ganache and try again.")
        try:
            contract = bc.get_contract()
            print(f"Loaded contract: {contract.address}")
        except Exception:
            print("No deployed contract found yet.")
    except Exception as exc:
        print(f"Error: {exc}")


def main():
    print("Vehicle Ownership System")
    print("If you are new: do 1, then 2, then 4/5/6.")
    show_status()

    while True:
        print("\n================ MENU ================")
        print("1. Deploy contract (do this first)")
        print("2. Register a new vehicle")
        print("3. Transfer ownership to new owner")
        print("4. Check current owner by vehicle ID")
        print("5. Show full vehicle details")
        print("6. Show ownership history")
        print("7. Set verifier role")
        print("8. Verifier confirmation (create audit trail)")
        print("9. Exit")
        print("======================================")
        choice = input("Enter option number (1-9): ").strip()

        if choice == "1":
            safe_run(deploy)
        elif choice == "2":
            safe_run(register)
        elif choice == "3":
            safe_run(transfer)
        elif choice == "4":
            safe_run(owner)
        elif choice == "5":
            safe_run(vehicle)
        elif choice == "6":
            safe_run(history)
        elif choice == "7":
            safe_run(verifier)
        elif choice == "8":
            safe_run(verify_ownership_as_verifier)
        elif choice == "9":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
