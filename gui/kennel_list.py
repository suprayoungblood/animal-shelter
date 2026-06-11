"""Kennel list widget — Treeview of all kennels (occupied and empty).

Animals leave the shelter through adoption, so this list is read-only;
the kennel itself stays in the shelter for reuse.
"""
from __future__ import annotations

from tkinter import ttk

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
    """A card-styled Treeview of kennels."""

    def __init__(self, parent):
        """Render the list.

        :param parent: Tk parent widget.
        """
        super().__init__(parent, text="  Kennels  ", style="Card.TLabelframe")
        self._build()

    def _build(self) -> None:
        """Construct the Treeview and scrollbar."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._tree = self._build_tree()
        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.grid(row=0, column=0, sticky="nsew", padx=(PAD, 0), pady=PAD)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, PAD), pady=PAD)

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
            tree.heading(col, text=COLUMN_HEADINGS[col])
            tree.column(col, width=COLUMN_WIDTHS[col], anchor="w")
        return tree

    def refresh(self, kennels: list[Kennel]) -> None:
        """Redraw the list from the given kennels collection."""
        self._tree.delete(*self._tree.get_children())
        for index, kennel in enumerate(kennels, start=1):
            details = "—" if kennel.is_empty() else str(kennel.animal)
            self._tree.insert(
                "",
                "end",
                values=(index, kennel.get_animal_type(), details),
            )
