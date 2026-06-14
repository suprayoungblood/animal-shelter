"""Pending adoption requests modal — confirm or cancel held pickups.

Lists every reservation created when a wanted animal arrived for someone
on the waiting list. Each row can be confirmed (the adopter picked the
animal up) or cancelled (they never came, freeing the animal).
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from gui.styles import FONTS, PAD, PALETTE
from shelter import PendingRequest


class PendingRequestsModal(tk.Toplevel):
    """A modal listing pending pickups with Confirm / Cancel per row."""

    def __init__(
        self,
        parent,
        requests: list[PendingRequest],
        on_confirm: Callable[[int], None],
        on_cancel: Callable[[int], None],
    ):
        """Build and show the dialog centered over the main window.

        :param parent: The widget the dialog was opened from.
        :param requests: The pending requests to display.
        :param on_confirm: Callback with the 1-based kennel number to confirm.
        :param on_cancel: Callback with the 1-based kennel number to cancel.
        """
        super().__init__(parent)
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self.title("Process Adoption Requests")
        self.configure(bg=PALETTE["panel"])
        self.resizable(False, False)
        self._build(requests)
        self._center_over(parent.winfo_toplevel())
        self.transient(parent.winfo_toplevel())
        self.bind("<Escape>", lambda _: self.destroy())
        try:
            self.grab_set()
        except tk.TclError:
            pass  # window not yet viewable (e.g. headless tests)

    def _build(self, requests: list[PendingRequest]) -> None:
        """Construct the header and one row per pending request."""
        self.columnconfigure(0, weight=1)
        tk.Label(
            self,
            text="Pending pickups (matched from the waiting list)",
            bg=PALETTE["panel"],
            fg=PALETTE["accent"],
            font=FONTS["h2"],
            anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky="ew", padx=PAD, pady=(PAD, 4))
        if not requests:
            tk.Label(
                self,
                text="No pending adoption requests.",
                bg=PALETTE["panel"],
                fg=PALETTE["text"],
                font=FONTS["body"],
                anchor="w",
            ).grid(row=1, column=0, columnspan=3, sticky="ew", padx=PAD, pady=PAD)
        for row, request in enumerate(requests, start=1):
            self._build_request_row(row, request)
        ttk.Button(
            self, text="Close", style="Danger.TButton", command=self.destroy
        ).grid(row=len(requests) + 1, column=0, columnspan=3,
               sticky="ew", padx=PAD, pady=PAD)

    def _build_request_row(self, row: int, request: PendingRequest) -> None:
        """Render one request: label, Confirm, and Cancel."""
        text = (
            f"#{request.kennel_number}  {request.animal_type} "
            f"'{request.animal_name}' → {request.adopter}"
        )
        tk.Label(
            self,
            text=text,
            bg=PALETTE["panel"],
            fg=PALETTE["text"],
            font=FONTS["body"],
            anchor="w",
        ).grid(row=row, column=0, sticky="ew", padx=(PAD, 4), pady=2)
        ttk.Button(
            self, text="Confirm", style="Accent.TButton",
            command=lambda n=request.kennel_number: self._finish(self._on_confirm, n),
        ).grid(row=row, column=1, sticky="ew", padx=4, pady=2)
        ttk.Button(
            self, text="Cancel", style="Danger.TButton",
            command=lambda n=request.kennel_number: self._finish(self._on_cancel, n),
        ).grid(row=row, column=2, sticky="ew", padx=(4, PAD), pady=2)

    def _finish(self, callback: Callable[[int], None], kennel_number: int) -> None:
        """Run a confirm/cancel callback, then close the dialog."""
        callback(kennel_number)
        self.destroy()

    def _center_over(self, window: tk.Misc) -> None:
        """Position the dialog over the center of the given window."""
        self.update_idletasks()
        x = window.winfo_rootx() + (window.winfo_width() - self.winfo_width()) // 2
        y = window.winfo_rooty() + (window.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
