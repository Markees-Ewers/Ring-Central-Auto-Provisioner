"""Application navigation and workflow orchestration.

Author: Markees Ewers
Responsibility: Connect the scanner UIs, scan controllers, and RingCentral
provisioning workflow while managing the application's top-level modes.
"""

from __future__ import annotations

import argparse
import tkinter as tk

from Controller.camera_selector import choose_camera, get_camera_names
from Controller.scan_output import print_camera_result, print_scanner_result
from Model.Persistence.Phone_Model_Persistence_Controller import load_models, save_models
from View.camera_ui import run_camera_scanner
from View.input_selection_ui import choose_input_mode
from View.scanner_ui import run_scanner_input
from Controller.ringcentral_browser import (
    ProvisioningOptions,
)
from Model.Phone import Phone
from Model.scanner_controller import ScanResult


def _prepare_ringcentral(
    options: ProvisioningOptions,
) -> tuple[object | None, str | None, bool | None]:
    """Attach and check RingCentral before opening a scanner page."""
    status_messages: list[str] = []
    try:
        from Controller.ringcentral_browser import RingCentralBrowser

        browser = RingCentralBrowser(
            options,
            on_status=status_messages.append,
        )
        browser.check_ready()
        return browser, " | ".join(status_messages), True
    except RuntimeError as exc:
        if "browser" in locals():
            browser.close()
        return None, f"RingCentral unavailable: {exc}", False


def run_scanner_mode(
    model: str | None,
    models: list[str],
    ringcentral_options: ProvisioningOptions | None = None,
) -> bool:
    """Run USB scanner mode."""
    if not models:
        raise RuntimeError(
            "Add at least one phone model on the landing page before scanning."
        )
    if model is None:
        raise RuntimeError(
            "Select a phone model on the landing page before scanning."
        )
    browser, integration_status, integration_ready = _prepare_ringcentral(
        ringcentral_options
    )

    def handle_scan(result: ScanResult) -> str | None:
        print_scanner_result(result)
        if browser is not None:
            message = browser.provision(result.to_phone())
            print(message, flush=True)
            return message
        return "Phone scanned successfully; RingCentral was not ready."

    try:
        return run_scanner_input(
            model,
            handle_scan,
            integration_status,
            integration_ready,
        )
    finally:
        if browser is not None:
            browser.close()


def run_camera_mode(
    camera_index: int,
    model: str | None,
    ringcentral_options: ProvisioningOptions | None = None,
) -> bool:
    """Run capture-based camera mode."""
    if ringcentral_options is not None and model is None:
        raise RuntimeError(
            "Select a phone model before using RingCentral provisioning."
        )

    browser, integration_status, integration_ready = _prepare_ringcentral(
        ringcentral_options
    )

    def handle_scan(mac: str) -> str | None:
        print_camera_result(mac, model)
        if browser is not None:
            phone = Phone(mac_address=mac, model_number=model)
            message = browser.provision(phone)
            print(message, flush=True)
            return message
        return "Phone scanned successfully; RingCentral was not ready."

    try:
        return run_camera_scanner(
            camera_index,
            model,
            handle_scan,
            integration_status,
            integration_ready,
        )
    finally:
        if browser is not None:
            browser.close()


def main() -> None:
    """Start the application and route between its pages."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("camera", "scanner"),
        default=None,
        help="Input mode; USB scanner is selected by default.",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=None,
        help="Camera index, bypassing the camera picker.",
    )
    parser.add_argument(
        "--chrome-debugger-address",
        default="127.0.0.1:9222",
        help="Chrome remote-debugging address used for automatic RingCentral detection.",
    )
    args = parser.parse_args()

    try:
        models = load_models()
        selected_mode = args.mode
        selected_model: str | None = None

        if selected_mode is None:
            selected_mode, models, selected_model = choose_input_mode(
                models, save_models
            )
            if selected_mode is None:
                return

        if selected_mode == "scanner":
            ringcentral_options = ProvisioningOptions(
                debugger_address=args.chrome_debugger_address,
            )
            if run_scanner_mode(selected_model, models, ringcentral_options):
                return main()
            return

        ringcentral_options = ProvisioningOptions(
            debugger_address=args.chrome_debugger_address,
        )
        if args.camera is not None:
            run_camera_mode(args.camera, selected_model, ringcentral_options)
            return

        camera_names = get_camera_names()
        if not camera_names:
            raise RuntimeError(
                "No cameras were found. Connect a camera and run the scanner again."
            )
        selected_camera = choose_camera(camera_names)
        if selected_camera is not None and run_camera_mode(
            selected_camera, selected_model, ringcentral_options
        ):
            return main()
    except (RuntimeError, tk.TclError) as exc:
        raise SystemExit(str(exc)) from exc
