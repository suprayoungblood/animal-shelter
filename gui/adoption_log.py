"""Adoption log widget — Treeview history of every completed adoption."""
from __future__ import annotations

from tkinter import ttk

from gui.styles import PAD
from shelter import AdoptionRecord

LOG_COLUMNS = ("animal", "adopter", "how")
LOG_HEADINGS = {
    "animal":  "Animal",
    "adopter": "Adopted By",
    "how":     "How",
}
LOG_WIDTHS = {
    "animal":  180,
    "adopter": 140,
    "how":     110,
}
LOG_ROWS_SHOWN = 4
HOW_LABELS = {
    True:  "From waiting list",
    False: "Walk-in",
}


class AdoptionLogView(ttk.LabelFrame):
    """A card-styled Treeview of adoptions, newest first."""

    def __init__(self, parent):
        """Render the log panel.

        :param parent: Tk parent widget.
        """
        super().__init__(parent, text="  Adoption Log  ", style="Card.TLabelframe")
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
            columns=LOG_COLUMNS,
            show="headings",
            style="Kennel.Treeview",
            selectmode="none",
            height=LOG_ROWS_SHOWN,
        )
        for col in LOG_COLUMNS:
            tree.heading(col, text=LOG_HEADINGS[col], anchor="w")
            tree.column(col, width=LOG_WIDTHS[col], anchor="w")
        return tree

    def refresh(self, adoptions: list[AdoptionRecord]) -> None:
        """Redraw the log from the shelter's records, newest first."""
        self._tree.delete(*self._tree.get_children())
        for record in reversed(adoptions):
            animal = f"{record.animal_type} '{record.animal_name}'"
            how = HOW_LABELS[record.from_waiting_list]
            self._tree.insert("", "end", values=(animal, record.adopter, how))
