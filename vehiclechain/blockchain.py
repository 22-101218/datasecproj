from pathlib import Path
from typing import Any, Dict, List

from solcx import compile_standard, install_solc
from web3 import Web3
from web3.contract import Contract

from vehiclechain.paths import resource_root

CONTRACT_PATH = resource_root() / "contracts" / "VehicleOwnership.sol"

GANACHE_URL = "http://127.0.0.1:7545"
CHAIN_ID = 1337
SOLC_VERSION = "0.8.19"
AUTHORITY_PRIVATE_KEY = ""

_contract_abi: List[Dict[str, Any]] | None = None
_contract_bytecode: str | None = None
_contract_address: str | None = None
_contract_instance: Contract | None = None

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    raise RuntimeError(f"Unable to connect to Ganache at {GANACHE_URL}")

if AUTHORITY_PRIVATE_KEY:
    authority_account = w3.eth.account.from_key(AUTHORITY_PRIVATE_KEY)
    authority_address = authority_account.address
else:
    accounts = w3.eth.accounts
    if not accounts:
        raise RuntimeError("No unlocked Ganache accounts found")
    authority_address = accounts[0]


def get_authority_address() -> str:
    """Wallet that sends deploy, register, and set_verifier transactions."""
    return authority_address


def compile_contract() -> tuple[List[Dict[str, Any]], str]:
    install_solc(SOLC_VERSION)
    source = CONTRACT_PATH.read_text(encoding="utf-8")
    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {"VehicleOwnership.sol": {"content": source}},
            "settings": {
                "evmVersion": "paris",
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                },
            },
        },
        solc_version=SOLC_VERSION,
    )
    contract_data = compiled["contracts"]["VehicleOwnership.sol"]["VehicleOwnership"]
    abi = contract_data["abi"]
    bytecode = contract_data["evm"]["bytecode"]["object"]
    return abi, bytecode


def _get_compiled_artifacts() -> tuple[List[Dict[str, Any]], str]:
    global _contract_abi, _contract_bytecode
    if _contract_abi is None or _contract_bytecode is None:
        _contract_abi, _contract_bytecode = compile_contract()
    return _contract_abi, _contract_bytecode


def deploy_contract() -> str:
    global _contract_address, _contract_instance
    abi, bytecode = _get_compiled_artifacts()
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(authority_address)
    tx = {
        "from": authority_address,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "gas": 6_000_000,
        "gasPrice": w3.to_wei("20", "gwei"),
    }
    if AUTHORITY_PRIVATE_KEY:
        built = contract.constructor().build_transaction(tx)
        signed = w3.eth.account.sign_transaction(built, private_key=AUTHORITY_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    else:
        tx_hash = contract.constructor().transact(tx)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    _contract_address = receipt.contractAddress
    _contract_instance = w3.eth.contract(
        address=Web3.to_checksum_address(_contract_address),
        abi=abi,
    )
    return _contract_address


def get_contract() -> Contract:
    if _contract_instance is None:
        raise RuntimeError("Contract not deployed. Choose Deploy Contract first.")
    return _contract_instance


def _send_authority_tx(function_call: Any) -> str:
    nonce = w3.eth.get_transaction_count(authority_address)
    tx = {
        "from": authority_address,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "gas": 500_000,
        "gasPrice": w3.to_wei("20", "gwei"),
    }
    if AUTHORITY_PRIVATE_KEY:
        built = function_call.build_transaction(tx)
        signed = w3.eth.account.sign_transaction(built, private_key=AUTHORITY_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    else:
        tx_hash = function_call.transact(tx)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()


def _send_owner_tx(
    function_call: Any,
    owner_private_key: str | None = None,
    owner_address: str | None = None,
) -> str:
    if owner_private_key:
        account = w3.eth.account.from_key(owner_private_key)
        from_address = account.address
    elif owner_address:
        from_address = Web3.to_checksum_address(owner_address)
    else:
        raise ValueError("Either owner_private_key or owner_address is required")

    nonce = w3.eth.get_transaction_count(from_address)
    tx = {
        "from": from_address,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "gas": 500_000,
        "gasPrice": w3.to_wei("20", "gwei"),
    }
    if owner_private_key:
        built = function_call.build_transaction(tx)
        signed = w3.eth.account.sign_transaction(built, private_key=owner_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    else:
        tx_hash = function_call.transact(tx)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()


def register_vehicle(vehicle_id: str, brand: str, model: str, owner: str) -> str:
    contract = get_contract()
    return _send_authority_tx(
        contract.functions.registerVehicle(
            vehicle_id, brand, model, Web3.to_checksum_address(owner)
        )
    )


def set_verifier(verifier: str, allowed: bool) -> str:
    contract = get_contract()
    return _send_authority_tx(
        contract.functions.setVerifier(Web3.to_checksum_address(verifier), allowed)
    )


def transfer_ownership(
    vehicle_id: str,
    new_owner: str,
    current_owner_private_key: str | None = None,
    current_owner_address: str | None = None,
) -> str:
    contract = get_contract()
    return _send_owner_tx(
        contract.functions.transferOwnership(
            vehicle_id, Web3.to_checksum_address(new_owner)
        ),
        current_owner_private_key,
        current_owner_address,
    )


def verify_owner(vehicle_id: str) -> str:
    contract = get_contract()
    return contract.functions.verifyCurrentOwner(vehicle_id).call()


def get_vehicle(vehicle_id: str) -> Dict[str, Any]:
    contract = get_contract()
    v = contract.functions.getVehicle(vehicle_id).call()
    return {
        "vehicle_id": v[0],
        "brand": v[1],
        "model": v[2],
        "current_owner": v[3],
        "registered_at": v[4],
    }


def get_history(vehicle_id: str) -> List[Dict[str, Any]]:
    contract = get_contract()
    rows = contract.functions.getOwnershipHistory(vehicle_id).call()
    return [{"owner": row[0], "transferred_at": row[1]} for row in rows]
