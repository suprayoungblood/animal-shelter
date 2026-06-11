"""Adoption widgets — adoption request form and waiting list view."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from animals import ANIMAL_TYPES
from gui.styles import FONTS, PAD, PALETTE

WAITING_COLUMNS = ("type", "waiting")
WAITING_HEADINGS = {
    "type":    "Animal Type",
    "waiting": "Waiting Adopters",
}
WAITING_WIDTHS = {
    "type":    110,
    "waiting": 300,
}
WAITING_ROWS_SHOWN = 4
EMPTY_MESSAGE = "No one is waiting."


class AdoptionForm(ttk.LabelFrame):
    """A card-styled form for requesting an adoption by animal type."""

    def __init__(self, parent, on_adopt: Callable[[str, str], None]):
        """Render the form.

        :param parent: Tk parent widget.
        :param on_adopt: Callback invoked with (animal_type, adopter_name).
        """
        super().__init__(parent, text="  Adopt an Animal  ", style="Card.TLabelframe")
        self._on_adopt = on_adopt
        type_names = list(ANIMAL_TYPES)
        self._type_var = tk.StringVar(value=type_names[0])
        self._adopter_var = tk.StringVar()
        self._error_var = tk.StringVar()
        self._build(type_names)

    def _build(self, type_names: list[str]) -> None:
        """Construct all child widgets."""
        self.columnconfigure(1, weight=1)
        self._row_type(0, type_names)
        self._row_adopter(1)
        self._row_error(2)
        self._row_submit(3)

    def _row_type(self, row: int, type_names: list[str]) -> None:
        """Render the animal type dropdown row."""
        ttk.Label(self, text="Type", style="Field.TLabel").grid(
            row=row, column=0, sticky="w", padx=PAD, pady=PAD
        )
        ttk.Combobox(
            self,
            textvariable=self._type_var,
            values=type_names,
            state="readonly",
        ).grid(row=row, column=1, sticky="ew", padx=PAD, pady=PAD)

    def _row_adopter(self, row: int) -> None:
        """Render the adopter name entry row."""
        ttk.Label(self, text="Adopter", style="Field.TLabel").grid(
            row=row, column=0, sticky="w", padx=PAD, pady=PAD
        )
        ttk.Entry(self, textvariable=self._adopter_var).grid(
            row=row, column=1, sticky="ew", padx=PAD, pady=PAD
        )

    def _row_error(self, row: int) -> None:
        """Render the inline error label."""
        tk.Label(
            self,
            textvariable=self._error_var,
            bg=PALETTE["panel"],
            fg=PALETTE["danger"],
            font=FONTS["small"],
            anchor="w",
            justify="left",
        ).grid(row=row, column=0, columnspan=2, sticky="ew", padx=PAD)

    def _row_submit(self, row: int) -> None:
        """Render the adopt button."""
        ttk.Button(
            self,
            text="Adopt",
            style="Accent.TButton",
            command=self._submit,
        ).grid(row=row, column=0, columnspan=2, sticky="ew", padx=PAD, pady=PAD)

    def _submit(self) -> None:
        """Forward the request to the callback; surface validation errors."""
        try:
            self._on_adopt(self._type_var.get(), self._adopter_var.get())
        except ValueError as exc:
            self._error_var.set(str(exc))
            return
        self._error_var.set("")
        self._adopter_var.set("")


class WaitingListView(ttk.LabelFrame):
    """A card-styled summary of waiting adopters by type.

    Only animal types with at least one waiter get a row. Each row shows
    the count of waiting adopters; clicking the row opens a modal listing
    the adopters in first-come, first-served order.
    """

    def __init__(self, parent):
        """Render the waiting list panel.

        :param parent: Tk parent widget.
        """
        super().__init__(parent, text="  Waiting List  ", style="Card.TLabelframe")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._waiting: dict[str, list[str]] = {}
        self._tree = self._build_tree()
        self._tree.grid(row=0, column=0, sticky="nsew", padx=PAD, pady=PAD)

    def _build_tree(self) -> ttk.Treeview:
        """Create and configure the Treeview widget."""
        tree = ttk.Treeview(
            self,
            columns=WAITING_COLUMNS,
            show="headings",
            style="Kennel.Treeview",
            selectmode="none",
            height=WAITING_ROWS_SHOWN,
        )
        for col in WAITING_COLUMNS:
            tree.heading(col, text=WAITING_HEADINGS[col], anchor="w")
            tree.column(col, width=WAITING_WIDTHS[col], anchor="w")
        tree.bind("<Button-1>", self._open_adopters_modal)
        return tree

    def refresh(self, waiting_list: dict[str, list[str]]) -> None:
        """Redraw the panel: one row per type with waiters."""
        self._waiting = {t: list(names) for t, names in waiting_list.items() if names}
        self._tree.delete(*self._tree.get_children())
        if not self._waiting:
            self._tree.insert("", "end", values=("", EMPTY_MESSAGE))
            return
        for animal_type, adopters in self._waiting.items():
            count = len(adopters)
            label = f"{count} waiting — click to view"
            self._tree.insert("", "end", values=(animal_type, label))

    def _open_adopters_modal(self, event) -> str:
        """Open a modal listing the clicked type's waiting adopters."""
        item = self._tree.identify_row(event.y)
        if item:
            animal_type = self._tree.item(item, "values")[0]
            adopters = self._waiting.get(animal_type)
            if adopters:
                AdoptersModal(self, animal_type, adopters)
        return "break"


class AdoptersModal(tk.Toplevel):
    """A small modal dialog listing one type's waiting adopters in order."""

    def __init__(self, parent, animal_type: str, adopters: list[str]):
        """Build and show the dialog centered over the main window.

        :param parent: The widget the dialog was opened from.
        :param animal_type: The animal type whose waiters are shown.
        :param adopters: Adopter names in first-come, first-served order.
        """
        super().__init__(parent)
        self.title(f"{animal_type} Waiting List")
        self.configure(bg=PALETTE["panel"])
        self.resizable(False, False)
        self._build(animal_type, adopters)
        self._center_over(parent.winfo_toplevel())
        self.transient(parent.winfo_toplevel())
        self.bind("<Escape>", lambda _: self.destroy())
        try:
            self.grab_set()
        except tk.TclError:
            pass  # window not yet viewable (e.g. headless tests)

    def _build(self, animal_type: str, adopters: list[str]) -> None:
        """Construct the header, the numbered name list, and Close."""
        tk.Label(
            self,
            text=f"Waiting for a {animal_type}",
            bg=PALETTE["panel"],
            fg=PALETTE["accent"],
            font=FONTS["h2"],
            anchor="w",
        ).pack(fill="x", padx=PAD, pady=(PAD, 4))
        for position, name in enumerate(adopters, start=1):
            tk.Label(
                self,
                text=f"{position}. {name}",
                bg=PALETTE["panel"],
                fg=PALETTE["text"],
                font=FONTS["body"],
                anchor="w",
            ).pack(fill="x", padx=PAD * 2)
        ttk.Button(
            self,
            text="Close",
            style="Accent.TButton",
            command=self.destroy,
        ).pack(fill="x", padx=PAD, pady=PAD)

    def _center_over(self, window: tk.Misc) -> None:
        """Position the dialog over the center of the given window."""
        self.update_idletasks()
        x = window.winfo_rootx() + (window.winfo_width() - self.winfo_width()) // 2
        y = window.winfo_rooty() + (window.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
