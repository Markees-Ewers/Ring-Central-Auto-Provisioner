"""Tkinter user interface for the keyboard-wedge scanner.

Author: Markees Ewers
Responsibility: Receive keyboard-wedge scans, display validation results, and
show RingCentral provisioning status.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from Model.scanner_controller import ScanResult, ScannerController


def run_scanner_input(
    model: str,
    on_scan: Callable[[ScanResult], str | None],
    integration_status: str | None = None,
    integration_ready: bool | None = None,
) -> bool:
    """Display the scanner page and return True when Back is selected."""
    controller = ScannerController(model)
    root = tk.Tk()
    root.title("MAC barcode scanner")
    root.resizable(False, False)
    root.geometry("900x500")

    ttk.Label(
        root,
        text="Scan the MAC barcode",
        font=("Segoe UI", 16, "bold"),
    ).pack(pady=(20, 6))
    ttk.Label(
        root,
        text="Click the field, then scan. Press Esc to close.",
    ).pack(pady=(0, 12))
    ttk.Label(
        root,
        text=f"Phone model being captured: {controller.model}",
        font=("Segoe UI", 11),
    ).pack(pady=(0, 10))

    connection_text = integration_status or "RingCentral integration is not enabled."
    connection_color = (
        "#16803c"
        if integration_ready is True
        else "#b00020"
        if integration_ready is False
        else "#555555"
    )
    connection_label = tk.Label(
        root,
        text=connection_text,
        fg=connection_color,
        font=("Segoe UI", 10, "bold"),
    )
    connection_label.pack(pady=(0, 8))

    scan_value = tk.StringVar()
    entry = ttk.Entry(root, textvariable=scan_value, width=48)
    entry.pack(padx=20)
    if integration_ready is not False:
        entry.focus_set()
    else:
        entry.configure(state=tk.DISABLED)

    status = tk.StringVar(value="Waiting for scanner input...")
    ttk.Label(root, textvariable=status).pack(pady=18)
    raw_result = tk.StringVar(value="Last scanned value: <none>")
    ttk.Label(root, textvariable=raw_result).pack(pady=(0, 8))
    mac_result = tk.StringVar(value="Last MAC: <none>")
    ttk.Label(root, textvariable=mac_result).pack(pady=(0, 12))
    went_back = [False]

    def handle_scan(_event: tk.Event[tk.Entry]) -> str:
        raw_value = scan_value.get().strip()
        raw_result.set(f"Last scanned value: {raw_value or '<empty>'}")
        result = controller.process_scan(raw_value)
        if result is None:
            status.set(f"Ignored non-MAC barcode: {raw_value or '<empty>'}")
        else:
            mac_result.set(f"Last MAC: {result.mac_address}")
            status.set(
                f"MAC scan successful: {result.mac_address} | "
                f"Model: {result.model}"
            )
            try:
                provision_status = on_scan(result)
            except RuntimeError as exc:
                provision_status = f"Provisioning failed: {exc}"
            if provision_status:
                status.set(provision_status)
        scan_value.set("")
        entry.focus_set()
        return "break"

    def close(_event: tk.Event[tk.Tk] | None = None) -> str:
        root.destroy()
        return "break"

    def go_back() -> None:
        went_back[0] = True
        root.destroy()

    entry.bind("<Return>", handle_scan)
    root.bind("<Escape>", close)
    ttk.Button(root, text="Back", command=go_back).pack(pady=(0, 12))
    root.protocol("WM_DELETE_WINDOW", go_back)
    root.mainloop()
    return went_back[0]
