"""
Append-only CSV audit log for every blockchain action.
`audit_log.csv` lives in the project root when developing, or next to VehicleChain.exe when packaged.
"""

from __future__ import annotations

import csv
from datetime import datetime

from vehiclechain.paths import data_root

LOG_FILE = data_root() / "audit_log.csv"

_COLUMNS = [
    "timestamp",
    "action",
    "vehicle_id",
    "actor_address",
    "tx_hash",
    "block_number",
    "notes",
]


def _ensure_header() -> None:
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_COLUMNS)
            writer.writeheader()


def log_action(
    action: str,
    vehicle_id: str = "",
    actor_address: str = "",
    tx_hash: str = "",
    block_number: int | str = "",
    notes: str = "",
) -> None:
    _ensure_header()
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action.upper(),
        "vehicle_id": vehicle_id,
        "actor_address": actor_address,
        "tx_hash": tx_hash,
        "block_number": str(block_number),
        "notes": notes,
    }
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_COLUMNS)
        writer.writerow(row)


def read_log() -> list[dict[str, str]]:
    _ensure_header()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return list(reversed(rows))


def get_log_path() -> str:
    return str(LOG_FILE)
