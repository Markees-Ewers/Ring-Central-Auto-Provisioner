"""Application logic for keyboard-wedge MAC scanner input.

Author: Markees Ewers
Responsibility: Validate raw scanner input and convert valid scans into
timestamped domain results.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from Model.mac_parser import parse_mac
from Model.Phone import Phone


@dataclass(frozen=True)
class ScanResult:
    """Validated scanner result passed from the controller to the UI."""

    raw_value: str
    mac_address: str
    model: str
    timestamp: str

    def to_phone(self) -> Phone:
        """Convert this validated scan into the provisioning domain object."""
        return Phone(self.mac_address, self.model)


class ScannerController:
    """Validate scanner input without depending on a UI toolkit."""

    def __init__(self, model: str) -> None:
        if not model.strip():
            raise ValueError("A phone model is required.")
        self.model = model.strip()

    def process_scan(self, raw_value: str) -> ScanResult | None:
        """Validate one raw scanner value and return a result for valid MACs."""
        normalized_value = raw_value.strip()
        mac_address = parse_mac(normalized_value)
        if mac_address is None:
            return None
        return ScanResult(
            raw_value=normalized_value,
            mac_address=mac_address,
            model=self.model,
            timestamp=datetime.now().astimezone().isoformat(timespec="seconds"),
        )
