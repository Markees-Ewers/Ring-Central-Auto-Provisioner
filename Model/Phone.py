"""Validated phone data passed between scanners and provisioning workflows.

Author: Markees Ewers
Responsibility: Define the validated phone value passed from scanning into
RingCentral provisioning.
"""

from __future__ import annotations

from dataclasses import dataclass

from Model.mac_parser import parse_mac


@dataclass(frozen=True)
class Phone:
    """A phone model and normalized MAC address."""

    mac_address: str
    model_number: str

    def __post_init__(self) -> None:
        normalized_mac = parse_mac(self.mac_address)
        if normalized_mac is None:
            raise ValueError(f"Invalid MAC address: {self.mac_address!r}")
        model = self.model_number.strip()
        if not model:
            raise ValueError("A phone model is required.")
        object.__setattr__(self, "mac_address", normalized_mac)
        object.__setattr__(self, "model_number", model)


