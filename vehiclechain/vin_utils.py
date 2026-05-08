"""
vin_utils.py
============
Dual-mode Vehicle ID validator.

- If the ID is exactly 17 characters (and no I/O/Q), it is treated as a
  standard VIN and validated using the official NHTSA transliteration +
  check-digit algorithm.
- Any other non-empty string is accepted as a custom fleet / authority ID.

Returns a ValidationResult named-tuple so the GUI can display the right badge.
"""

from __future__ import annotations

from typing import NamedTuple

# ---------------------------------------------------------------------------
# NHTSA VIN validation tables
# ---------------------------------------------------------------------------

_TRANSLITERATION: dict[str, int] = {
    "A": 1,  "B": 2,  "C": 3,  "D": 4,  "E": 5,
    "F": 6,  "G": 7,  "H": 8,
    "J": 1,  "K": 2,  "L": 3,  "M": 4,  "N": 5,
    "P": 7,  "R": 9,
    "S": 2,  "T": 3,  "U": 4,  "V": 5,  "W": 6,
    "X": 7,  "Y": 8,  "Z": 9,
    "0": 0,  "1": 1,  "2": 2,  "3": 3,  "4": 4,
    "5": 5,  "6": 6,  "7": 7,  "8": 8,  "9": 9,
}

_POSITION_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

_INVALID_CHARS = {"I", "O", "Q"}

_MODEL_YEAR_MAP: dict[str, str] = {
    "A": "1980", "B": "1981", "C": "1982", "D": "1983", "E": "1984",
    "F": "1985", "G": "1986", "H": "1987", "J": "1988", "K": "1989",
    "L": "1990", "M": "1991", "N": "1992", "P": "1993", "R": "1994",
    "S": "1995", "T": "1996", "V": "1997", "W": "1998", "X": "1999",
    "Y": "2000", "1": "2001", "2": "2002", "3": "2003", "4": "2004",
    "5": "2005", "6": "2006", "7": "2007", "8": "2008", "9": "2009",
    "A2": "2010", "B2": "2011", "C2": "2012", "D2": "2013", "E2": "2014",
    "F2": "2015", "G2": "2016", "H2": "2017", "J2": "2018", "K2": "2019",
    "L2": "2020", "M2": "2021", "N2": "2022", "P2": "2023", "R2": "2024",
    "S2": "2025", "T2": "2026",
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

class ValidationResult(NamedTuple):
    valid: bool          # True = passes all checks
    mode: str            # "VIN" | "CUSTOM" | "EMPTY"
    message: str         # Short human-readable verdict
    detail: str          # Longer detail (model year, WMI, etc.)
    wmi: str             # World Manufacturer Identifier (3 chars) or ""
    model_year: str      # Decoded model year or ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_vehicle_id(vehicle_id: str) -> ValidationResult:
    """
    Validate a Vehicle ID string.

    Returns a ValidationResult with full details for the GUI to display.
    """
    vid = vehicle_id.strip().upper()

    # ── Empty ──────────────────────────────────────────────────────────────
    if not vid:
        return ValidationResult(
            valid=False,
            mode="EMPTY",
            message="Vehicle ID is required",
            detail="Please enter a VIN or a custom fleet ID.",
            wmi="",
            model_year="",
        )

    # ── Custom ID (not 17 chars) ────────────────────────────────────────────
    if len(vid) != 17:
        return ValidationResult(
            valid=True,
            mode="CUSTOM",
            message="Custom ID accepted",
            detail=f'"{vehicle_id.strip()}" will be stored as a custom fleet ID.',
            wmi="",
            model_year="",
        )

    # ── Potential VIN (exactly 17 chars) ───────────────────────────────────
    invalid = [c for c in vid if c in _INVALID_CHARS]
    if invalid:
        return ValidationResult(
            valid=False,
            mode="VIN",
            message=f"Invalid VIN character(s): {', '.join(invalid)}",
            detail="VINs must not contain the letters I, O, or Q.",
            wmi="",
            model_year="",
        )

    unknown = [c for c in vid if c not in _TRANSLITERATION]
    if unknown:
        return ValidationResult(
            valid=False,
            mode="VIN",
            message=f"Unknown character(s): {', '.join(set(unknown))}",
            detail="All 17 characters must be alphanumeric (excluding I, O, Q).",
            wmi="",
            model_year="",
        )

    # Check digit calculation
    total = sum(
        _TRANSLITERATION[c] * w
        for c, w in zip(vid, _POSITION_WEIGHTS)
    )
    remainder = total % 11
    expected_check = "X" if remainder == 10 else str(remainder)
    actual_check = vid[8]

    if actual_check != expected_check:
        return ValidationResult(
            valid=False,
            mode="VIN",
            message=f"Invalid VIN — check digit mismatch (got '{actual_check}', expected '{expected_check}')",
            detail="The 9th character check digit does not match the NHTSA algorithm.",
            wmi=vid[:3],
            model_year="",
        )

    # Decode model year (position 10, index 9)
    year_char = vid[9]
    model_year = _MODEL_YEAR_MAP.get(year_char, "Unknown")
    wmi = vid[:3]

    return ValidationResult(
        valid=True,
        mode="VIN",
        message="Valid VIN",
        detail=f"WMI: {wmi}  |  Model Year: {model_year}  |  Check digit: {actual_check}",
        wmi=wmi,
        model_year=model_year,
    )
