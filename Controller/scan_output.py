"""Console output for completed scans.

Author: Markees Ewers
Responsibility: Format validated scanner and camera results for terminal output.
"""

from __future__ import annotations

import json
from datetime import datetime

from Model.scanner_controller import ScanResult


def print_scanner_result(result: ScanResult) -> None:
    """Print a validated USB scanner result."""
    print("\n" + "=" * 60)
    print(f"MAC SCAN SUCCESS - {result.timestamp}")
    print(f"Raw string: {result.raw_value}")
    print(
        "Parsed data: "
        f"{json.dumps({'mac_address': result.mac_address, 'model': result.model})}"
    )
    print("=" * 60, flush=True)


def print_camera_result(mac_address: str, model: str | None) -> None:
    """Print a validated camera result."""
    print("\n" + "=" * 60)
    print(
        "MAC CAMERA SCAN SUCCESS - "
        f"{datetime.now().astimezone().isoformat(timespec='seconds')}"
    )
    print(
        "Parsed data: "
        f"{json.dumps({'mac_address': mac_address, 'model': model})}"
    )
    print("=" * 60, flush=True)
