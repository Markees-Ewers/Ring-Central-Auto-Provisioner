"""Capture-based camera scanning UI.

Author: Markees Ewers
Responsibility: Display the camera preview, start one-shot image scans, and
report scan and provisioning status to the user.
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

import cv2
from PIL import Image, ImageTk

from Controller.camera_capture import CameraCapture
from Model.mac_scan_service import MacScanService
from Model.mac_parser import parse_mac_prefix


def run_camera_scanner(
    camera_index: int,
    model: str | None,
    on_success: Callable[[str], str | None],
    integration_status: str | None = None,
    integration_ready: bool | None = None,
) -> bool:
    """Show a live preview and scan only when Scan label is pressed."""
    capture = CameraCapture(camera_index)
    scanner = MacScanService()
    root = tk.Tk()
    root.title("MAC camera scanner")
    root.geometry("820x650")
    root.resizable(False, False)

    connection_text = integration_status or "RingCentral integration is not enabled."
    connection_color = (
        "#16803c"
        if integration_ready is True
        else "#b00020"
        if integration_ready is False
        else "#555555"
    )
    tk.Label(
        root,
        text=connection_text,
        fg=connection_color,
        font=("Segoe UI", 10, "bold"),
    ).pack(pady=(0, 8))

    preview = ttk.Label(root)
    preview.pack(padx=10, pady=10)
    status = tk.StringVar(
        value=integration_status
        or "Position the complete label, then click Scan label."
    )
    model_text = tk.StringVar(value=model or "Not selected")
    ttk.Label(root, text="Phone model:").pack()
    ttk.Label(root, textvariable=model_text).pack(pady=(0, 8))
    prefix_frame = ttk.Frame(root)
    prefix_frame.pack(pady=(0, 8))
    ttk.Label(prefix_frame, text="MAC prefix (first 3 octets):").pack(side=tk.LEFT)
    prefix_text = tk.StringVar()
    prefix_entry = ttk.Entry(prefix_frame, textvariable=prefix_text, width=14)
    prefix_entry.pack(side=tk.LEFT, padx=(6, 0))
    ttk.Label(prefix_frame, text="Example: C81FEA or C8:1F:EA").pack(
        side=tk.LEFT, padx=(6, 0)
    )
    ttk.Label(root, textvariable=status).pack(pady=(0, 8))
    controls = ttk.Frame(root)
    controls.pack(pady=(0, 10))
    stop_button = ttk.Button(root, text="Stop scan", state=tk.DISABLED)
    scan_button = ttk.Button(controls, text="Scan label")
    stop_button = ttk.Button(controls, text="Stop scan", state=tk.DISABLED)
    back_button = ttk.Button(controls, text="Back")
    if integration_ready is False:
        scan_button.configure(state=tk.DISABLED)
    scan_button.pack(side=tk.LEFT, padx=5)
    stop_button.pack(side=tk.LEFT, padx=5)
    back_button.pack(side=tk.LEFT, padx=5)
    busy = [False]
    cancelled = [threading.Event()]
    went_back = [False]

    def update_preview() -> None:
        if not root.winfo_exists():
            return
        try:
            frame = capture.read()
            display = cv2.resize(frame, (780, 438))
            cv2.rectangle(display, (30, 30), (750, 408), (0, 220, 0), 3)
            image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(display, cv2.COLOR_BGR2RGB)))
            preview.configure(image=image)
            preview.image = image
            preview.frame = frame
        except RuntimeError as exc:
            status.set(str(exc))
        root.after(15, update_preview)

    def scan_label() -> None:
        if busy[0]:
            return
        prefix = prefix_text.get().strip()
        if prefix and parse_mac_prefix(prefix) is None:
            status.set("Invalid MAC prefix. Enter 6 hex digits, such as C81FEA.")
            prefix_entry.focus_set()
            return
        busy[0] = True
        cancelled[0] = threading.Event()
        scan_button.configure(state=tk.DISABLED)
        stop_button.configure(state=tk.NORMAL)
        status.set("Scanning captured label...")
        frame = getattr(preview, "frame", None)

        def worker() -> None:
            try:
                mac = (
                    scanner.scan(frame, cancelled[0], prefix)
                    if frame is not None
                    else None
                )
                root.after(0, lambda: scan_complete(mac, cancelled[0].is_set()))
            except RuntimeError as exc:
                root.after(0, lambda: scan_complete(None, error=str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def stop_scan() -> None:
        if busy[0]:
            cancelled[0].set()
            status.set("Stopping scan...")

    def scan_complete(
        mac: str | None, cancelled_scan: bool = False, error: str | None = None
    ) -> None:
        busy[0] = False
        scan_button.configure(state=tk.NORMAL)
        stop_button.configure(state=tk.DISABLED)
        if error:
            status.set(error)
        elif cancelled_scan:
            status.set("Scan stopped. Press Scan label to try again.")
        elif mac:
            status.set(f"MAC scan successful: {mac}")
            try:
                provision_status = on_success(mac)
            except RuntimeError as exc:
                provision_status = f"Provisioning failed: {exc}"
            if provision_status:
                status.set(provision_status)
        else:
            status.set("No valid MAC found. Reposition the label and try again.")

    def go_back() -> None:
        if busy[0]:
            cancelled[0].set()
        went_back[0] = True
        close()

    def close() -> None:
        capture.close()
        root.destroy()

    scan_button.configure(command=scan_label)
    stop_button.configure(command=stop_scan)
    back_button.configure(command=go_back)
    root.protocol("WM_DELETE_WINDOW", close)
    update_preview()
    root.mainloop()
    return went_back[0]
