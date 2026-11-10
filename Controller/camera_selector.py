"""Camera discovery and selection.

Author: Markees Ewers
Responsibility: Discover Windows camera names and present the camera picker.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import warnings

warnings.filterwarnings(
    "ignore",
    message="You are running 'comtypes' on Python 3.15",
    category=FutureWarning,
)

try:
    from pygrabber.dshow_graph import FilterGraph
except ImportError as exc:
    raise SystemExit(
        "Camera name support is required. Install dependencies with: "
        "python -m pip install -r requirements.txt"
    ) from exc


def get_camera_names() -> list[str]:
    """Return camera names reported by Windows DirectShow."""
    try:
        return [str(name) for name in FilterGraph().get_input_devices()]
    except Exception as exc:
        raise RuntimeError(f"Could not enumerate cameras: {exc}") from exc


def choose_camera(camera_names: list[str]) -> int | None:
    """Show camera choices and return the selected device index."""
    result: list[int | None] = [None]
    root = tk.Tk()
    root.title("Select camera")
    root.resizable(False, False)
    root.geometry("440x150")

    ttk.Label(root, text="Select the camera to use:").pack(
        padx=16, pady=(16, 6)
    )
    selected = tk.StringVar(value=camera_names[0])
    dropdown = ttk.Combobox(
        root, textvariable=selected, values=camera_names,
        state="readonly", width=52,
    )
    dropdown.pack(padx=16, fill=tk.X)
    dropdown.current(0)

    def start() -> None:
        result[0] = camera_names.index(selected.get())
        root.destroy()

    def cancel() -> None:
        root.destroy()

    buttons = ttk.Frame(root)
    buttons.pack(pady=14)
    ttk.Button(buttons, text="Start scanning", command=start).pack(
        side=tk.LEFT, padx=5
    )
    ttk.Button(buttons, text="Cancel", command=cancel).pack(
        side=tk.LEFT, padx=5
    )
    root.protocol("WM_DELETE_WINDOW", cancel)
    root.mainloop()
    return result[0]
