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
TREE_ARROW_WIDTH = 36
WAITING_ROWS_SHOWN = 6
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
    """A card-styled, expandable view of waiting adopters by type.

    Only animal types with at least one waiter get a row. Each row shows
    the count of waiting adopters; clicking the row expands it to list
    the adopters in first-come, first-served order.
    """

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
        """Create and configure the expandable Treeview widget."""
        tree = ttk.Treeview(
            self,
            columns=WAITING_COLUMNS,
            show="tree headings",
            style="Kennel.Treeview",
            selectmode="none",
            height=WAITING_ROWS_SHOWN,
        )
        tree.heading("#0", text="")
        tree.column("#0", width=TREE_ARROW_WIDTH, stretch=False)
        for col in WAITING_COLUMNS:
            tree.heading(col, text=WAITING_HEADINGS[col], anchor="w")
            tree.column(col, width=WAITING_WIDTHS[col], anchor="w")
        tree.bind("<Button-1>", self._toggle_row)
        return tree

    def refresh(self, waiting_list: dict[str, list[str]]) -> None:
        """Redraw the panel: one expandable row per type with waiters."""
        self._tree.delete(*self._tree.get_children())
        populated = {t: names for t, names in waiting_list.items() if names}
        if not populated:
            self._tree.insert("", "end", values=("", EMPTY_MESSAGE))
            return
        for animal_type, adopters in populated.items():
            row = self._tree.insert(
                "", "end", values=(animal_type, f"{len(adopters)} waiting")
            )
            for position, name in enumerate(adopters, start=1):
                self._tree.insert(row, "end", values=("", f"{position}. {name}"))

    def _toggle_row(self, event) -> str:
        """Expand or collapse the clicked type row to show adopter names."""
        item = self._tree.identify_row(event.y)
        if item and not self._tree.parent(item) and self._tree.get_children(item):
            self._tree.item(item, open=not self._tree.item(item, "open"))
        return "break"
