"""Adoption widgets — adoption request form and waiting list view."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from animals import ANIMAL_TYPES
from gui.styles import FONTS, PAD, PALETTE

WAITING_COLUMNS = ("type", "adopters")
WAITING_HEADINGS = {
    "type":     "Animal Type",
    "adopters": "Waiting Adopters",
}
WAITING_WIDTHS = {
    "type":     110,
    "adopters": 320,
}


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
    """A card-styled Treeview of each animal type's waiting adopters."""

    def __init__(self, parent):
        """Render the waiting list panel.

        :param parent: Tk parent widget.
        """
        super().__init__(parent, text="  Waiting List  ", style="Card.TLabelframe")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
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
            height=len(ANIMAL_TYPES),
        )
        for col in WAITING_COLUMNS:
            tree.heading(col, text=WAITING_HEADINGS[col])
            tree.column(col, width=WAITING_WIDTHS[col], anchor="w")
        return tree

    def refresh(self, waiting_list: dict[str, list[str]]) -> None:
        """Redraw the panel from the shelter's waiting list mapping."""
        self._tree.delete(*self._tree.get_children())
        for animal_type, adopters in waiting_list.items():
            names = ", ".join(adopters) if adopters else "—"
            self._tree.insert("", "end", values=(animal_type, names))
