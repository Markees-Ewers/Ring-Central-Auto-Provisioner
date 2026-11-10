"""Landing page for input and phone-model selection.

Author: Markees Ewers
Responsibility: Let the user choose scanner mode and maintain the saved model
list before a scan begins.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable


def choose_input_mode(
    models: list[str],
    save_models: Callable[[list[str]], None],
) -> tuple[str | None, list[str], str | None]:
    """Return selected input mode, updated models, and selected model."""
    result: list[str | None] = [None]
    selected_model: list[str | None] = [None]
    current_models = models[:]

    root = tk.Tk()
    root.title("Select input device")
    root.resizable(True, True)
    root.geometry("600x300")

    ttk.Label(root, text="Select the input device:").pack(
        padx=16, pady=(18, 6)
    )
    ttk.Label(
        root,
        text=(
            "USB scanners appear as keyboard input and cannot expose a "
            "device name here."
        ),
        wraplength=440,
    ).pack(padx=16, pady=(0, 10))

    input_options = ["USB barcode scanner (keyboard mode)", "Camera"]
    selected_input = tk.StringVar(value=input_options[0])
    input_dropdown = ttk.Combobox(
        root, textvariable=selected_input, values=input_options,
        state="readonly", width=52,
    )
    input_dropdown.pack(padx=16, fill=tk.X)
    input_dropdown.current(0)

    ttk.Label(root, text="Select phone model:").pack(
        anchor=tk.W, padx=16, pady=(14, 3)
    )
    model_value = tk.StringVar()
    model_dropdown = ttk.Combobox(
        root, textvariable=model_value, values=current_models,
        state="readonly", width=52,
    )
    model_dropdown.pack(padx=16, fill=tk.X)
    if current_models:
        model_dropdown.current(0)

    model_entry_frame = ttk.Frame(root)
    model_entry_frame.pack(fill=tk.X, padx=16, pady=8)
    ttk.Label(model_entry_frame, text="New phone model:").pack(
        side=tk.LEFT, padx=(0, 8)
    )
    model_entry = ttk.Entry(model_entry_frame, width=28)
    model_entry.pack(side=tk.LEFT, padx=(0, 8))

    def refresh_models() -> None:
        model_dropdown["values"] = current_models
        if current_models:
            model_dropdown.current(0)
        else:
            model_dropdown.set("")

    def add_model() -> None:
        value = model_entry.get().strip()
        if value and value not in current_models:
            current_models.append(value)
            save_models(current_models)
            refresh_models()
            model_entry.delete(0, tk.END)

    def delete_model() -> None:
        value = model_dropdown.get()
        if value in current_models:
            current_models.remove(value)
            save_models(current_models)
            refresh_models()

    ttk.Button(model_entry_frame, text="Add model", command=add_model).pack(
        side=tk.LEFT
    )
    ttk.Button(
        root, text="Delete selected phone model", command=delete_model
    ).pack(anchor=tk.W, padx=16)

    def start() -> None:
        result[0] = "scanner" if input_dropdown.current() == 0 else "camera"
        selected_model[0] = model_value.get() or None
        root.destroy()

    def cancel() -> None:
        root.destroy()

    buttons = ttk.Frame(root)
    buttons.pack(pady=16)
    ttk.Button(buttons, text="Continue", command=start).pack(
        side=tk.LEFT, padx=5
    )
    ttk.Button(buttons, text="Cancel", command=cancel).pack(
        side=tk.LEFT, padx=5
    )
    root.protocol("WM_DELETE_WINDOW", cancel)
    root.mainloop()
    return result[0], current_models, selected_model[0]
