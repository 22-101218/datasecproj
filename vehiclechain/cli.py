"""Terminal menu for VehicleChain (same workflow as the GUI)."""

from vehiclechain.blockchain import (
    deploy_contract,
    get_contract,
    get_history,
    get_vehicle,
    register_vehicle,
    set_verifier,
    transfer_ownership,
    verify_owner,
    w3,
)


def print_tx_summary(title, tx_hash):
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    tx_details = w3.eth.get_transaction(tx_hash)
    to_address = tx_receipt.contractAddress or tx_details["to"]

    print(f"\n{title}")
    print(f"TX HASH: {w3.to_hex(tx_hash)}")
    print(f"SENDER ADDRESS: {tx_details['from']}")
    print(f"TO CONTRACT ADDRESS: {to_address}")
    print(f"VALUE: {w3.from_wei(tx_details['value'], 'ether')} ETH")
    print(f"GAS USED: {tx_receipt.gasUsed}")
    print(f"GAS PRICE: {tx_details['gasPrice']}")
    print(f"GAS LIMIT: {tx_details['gas']}")
    print(f"MINED IN BLOCK: {tx_receipt.blockNumber}")
    print(f"BLOCK HASH: {w3.to_hex(tx_receipt.blockHash)}")


def safe_run(action):
    try:
        action()
    except Exception as exc:
        print(f"Error: {exc}")


def deploy():
    address = deploy_contract()
    print(f"Contract deployed at: {address}")
    print("Next: choose 2 to register your first vehicle.")


def register():
    print("\nRegister Vehicle")
    print("Tip: owner must be a Ganache address (starts with 0x...)")
    vehicle_id = input("Vehicle ID (example VIN123): ").strip()
    brand = input("Brand (example Toyota): ").strip()
    model = input("Model (example Corolla): ").strip()
    owner = input("Owner wallet address (0x...): ").strip()
    tx_hash = register_vehicle(vehicle_id, brand, model, owner)
    print_tx_summary("REGISTER VEHICLE", tx_hash)


def transfer():
    print("\nTransfer Ownership")
    print("Use valid Ganache addresses for both current and new owner.")
    vehicle_id = input("Vehicle ID: ").strip()
    current_owner_address = input("Current owner wallet address (0x...): ").strip()
    new_owner = input("New owner wallet address (0x...): ").strip()
    tx_hash = transfer_ownership(
        vehicle_id=vehicle_id,
        new_owner=new_owner,
        current_owner_address=current_owner_address,
    )
    print_tx_summary("TRANSFER OWNERSHIP", tx_hash)


def owner():
    vehicle_id = input("Vehicle ID to check owner: ").strip()
    current_owner = verify_owner(vehicle_id)
    print(f"Current owner: {current_owner}")


def vehicle():
    vehicle_id = input("Vehicle ID to view details: ").strip()
    data = get_vehicle(vehicle_id)
    print(data)


def history():
    vehicle_id = input("Vehicle ID to view history: ").strip()
    records = get_history(vehicle_id)
    for index, record in enumerate(records, start=1):
        print(f"{index}. owner={record['owner']} transferred_at={record['transferred_at']}")


def verifier():
    verifier_address = input("Verifier wallet address (0x...): ").strip()
    allowed_input = input("Allow verifier? (yes/no): ").strip().lower()
    allowed = allowed_input in ("y", "yes", "1", "true")
    tx_hash = set_verifier(verifier_address, allowed)
    print_tx_summary("SET VERIFIER", tx_hash)


def show_status():
    print(f"Connected: {w3.is_connected()}")
    print(f"Current block: {w3.eth.block_number}")
    print(f"Accounts: {w3.eth.accounts}")
    try:
        contract = get_contract()
        print(f"Loaded contract: {contract.address}")
    except Exception:
        print("No deployed contract found yet.")


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
        print("8. Exit")
        print("======================================")
        choice = input("Enter option number (1-8): ").strip()

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
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")


if __name__ == "__main__":
    main()
