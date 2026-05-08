"""Entry point for `python -m vehiclechain` and PyInstaller."""

import sys

from vehiclechain.gui import run

if __name__ == "__main__":
    sys.exit(run())
