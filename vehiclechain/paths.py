"""Project paths: works in development and when frozen (PyInstaller)."""

from __future__ import annotations

import sys
from pathlib import Path


def frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def resource_root() -> Path:
    """Read-only bundled files: contracts/, assets/."""
    if frozen():
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def data_root() -> Path:
    """Writable location: audit log, generated PDFs (folder of VehicleChain.exe when packaged)."""
    if frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def logo_path() -> Path:
    """PNG for sidebar/window/icon/PDF. Beside .exe wins (same as old app_qt + assets/)."""
    override = data_root() / "assets" / "car_logo.png"
    if override.is_file():
        return override
    return resource_root() / "assets" / "car_logo.png"
