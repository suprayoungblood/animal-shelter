"""Kennel list widget — Treeview of all kennels (occupied and empty).

Animals leave the shelter through adoption; the Edit and Remove controls
here exist to correct data-entry mistakes. The kennel itself always
stays in the shelter for reuse.
"""
from __future__ import annotations

from tkinter import ttk
from typing import Callable

from gui.styles import PAD
from kennel import Kennel

COLUMNS = ("number", "type", "details")
COLUMN_HEADINGS = {
    "number":  "#",
    "type":    "Animal Type",
    "details": "Details",
}
COLUMN_WIDTHS = {
    "number":  40,
    "type":    110,
    "details": 380,
}


class KennelList(ttk.LabelFrame):
    """A card-styled Treeview of kennels with correction controls."""

    def __init__(
        self,
        parent,
        on_edit: Callable[[int], None],
        on_remove: Callable[[int], None],
    ):
        """Render the list.

        :param parent: Tk parent widget.
        :param on_edit: Callback invoked with the 1-based kennel number to edit.
        :param on_remove: Callback invoked with the 1-based kennel number
            whose animal should be removed (data fix).
        """
        super().__init__(parent, text="  Kennels  ", style="Card.TLabelframe")
        self._on_edit = on_edit
        self._on_remove = on_remove
        self._build()

    def _build(self) -> None:
        """Construct the Treeview, scrollbar, and action buttons."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._tree = self._build_tree()
        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.grid(row=0, column=0, columnspan=2, sticky="nsew",
                        padx=(PAD, 0), pady=PAD)
        scroll.grid(row=0, column=2, sticky="ns", padx=(0, PAD), pady=PAD)
        ttk.Button(
            self,
            text="Edit Selected",
            style="Accent.TButton",
            command=lambda: self._forward_selection(self._on_edit),
        ).grid(row=1, column=0, sticky="ew", padx=(PAD, 4), pady=(0, PAD))
        ttk.Button(
            self,
            text="Remove Selected",
            style="Danger.TButton",
            command=lambda: self._forward_selection(self._on_remove),
        ).grid(row=1, column=1, columnspan=2, sticky="ew",
               padx=(4, PAD), pady=(0, PAD))

    def _build_tree(self) -> ttk.Treeview:
        """Create and configure the Treeview widget."""
        tree = ttk.Treeview(
            self,
            columns=COLUMNS,
            show="headings",
            style="Kennel.Treeview",
            selectmode="browse",
        )
        for col in COLUMNS:
            tree.heading(col, text=COLUMN_HEADINGS[col], anchor="w")
            tree.column(col, width=COLUMN_WIDTHS[col], anchor="w")
        tree.bind(
            "<Double-Button-1>",
            lambda _: self._forward_selection(self._on_edit),
        )
        return tree

    def refresh(self, kennels: list[Kennel]) -> None:
        """Redraw the list from the given kennels collection."""
        self._tree.delete(*self._tree.get_children())
        for number, kennel in enumerate(kennels, start=1):
            details = "—" if kennel.is_empty() else str(kennel.animal)
            self._tree.insert(
                "",
                "end",
                iid=str(number),
                values=(number, kennel.get_animal_type(), details),
            )

    def _forward_selection(self, callback: Callable[[int], None]) -> None:
        """Pass the selected row's 1-based kennel number to a callback."""
        selection = self._tree.selection()
        if selection:
            callback(int(selection[0]))
