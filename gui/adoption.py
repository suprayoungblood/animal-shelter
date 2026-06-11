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
    the count of waiting adopters; clicking the row opens a modal where
    the names can be viewed, corrected, or removed.
    """

    def __init__(
        self,
        parent,
        on_rename: Callable[[str, int, str], None],
        on_remove: Callable[[str, int], None],
    ):
        """Render the waiting list panel.

        :param parent: Tk parent widget.
        :param on_rename: Callback (animal_type, 1-based position, new_name).
        :param on_remove: Callback (animal_type, 1-based position).
        """
        super().__init__(parent, text="  Waiting List  ", style="Card.TLabelframe")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._on_rename = on_rename
        self._on_remove = on_remove
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
            label = f"{count} waiting — click to manage"
            self._tree.insert("", "end", values=(animal_type, label))

    def _open_adopters_modal(self, event) -> str:
        """Open a modal managing the clicked type's waiting adopters."""
        item = self._tree.identify_row(event.y)
        if item:
            animal_type = self._tree.item(item, "values")[0]
            adopters = self._waiting.get(animal_type)
            if adopters:
                AdoptersModal(
                    self, animal_type, adopters, self._on_rename, self._on_remove
                )
        return "break"


class AdoptersModal(tk.Toplevel):
    """A modal dialog to view, rename, or remove one type's waiters.

    Each adopter gets an editable entry (position preserved) and a
    Remove button. Save Changes applies every edited name at once.
    """

    def __init__(
        self,
        parent,
        animal_type: str,
        adopters: list[str],
        on_rename: Callable[[str, int, str], None],
        on_remove: Callable[[str, int], None],
    ):
        """Build and show the dialog centered over the main window.

        :param parent: The widget the dialog was opened from.
        :param animal_type: The animal type whose waiters are shown.
        :param adopters: Adopter names in first-come, first-served order.
        :param on_rename: Callback (animal_type, 1-based position, new_name).
        :param on_remove: Callback (animal_type, 1-based position).
        """
        super().__init__(parent)
        self._animal_type = animal_type
        self._original = list(adopters)
        self._on_rename = on_rename
        self._on_remove = on_remove
        self._name_vars: list[tk.StringVar] = []
        self._error_var = tk.StringVar()
        self.title(f"{animal_type} Waiting List")
        self.configure(bg=PALETTE["panel"])
        self.resizable(False, False)
        self._build()
        self._center_over(parent.winfo_toplevel())
        self.transient(parent.winfo_toplevel())
        self.bind("<Escape>", lambda _: self.destroy())
        try:
            self.grab_set()
        except tk.TclError:
            pass  # window not yet viewable (e.g. headless tests)

    def _build(self) -> None:
        """Construct the header, editable name rows, and action buttons."""
        self.columnconfigure(1, weight=1)
        tk.Label(
            self,
            text=f"Waiting for a {self._animal_type}",
            bg=PALETTE["panel"],
            fg=PALETTE["accent"],
            font=FONTS["h2"],
            anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky="ew", padx=PAD, pady=(PAD, 4))
        for position, name in enumerate(self._original, start=1):
            self._build_name_row(position, name)
        footer = len(self._original) + 1
        tk.Label(
            self,
            textvariable=self._error_var,
            bg=PALETTE["panel"],
            fg=PALETTE["danger"],
            font=FONTS["small"],
            anchor="w",
        ).grid(row=footer, column=0, columnspan=3, sticky="ew", padx=PAD)
        ttk.Button(
            self, text="Save Changes", style="Accent.TButton", command=self._save
        ).grid(row=footer + 1, column=0, columnspan=2, sticky="ew",
               padx=(PAD, 4), pady=PAD)
        ttk.Button(
            self, text="Close", style="Danger.TButton", command=self.destroy
        ).grid(row=footer + 1, column=2, sticky="ew", padx=(4, PAD), pady=PAD)

    def _build_name_row(self, position: int, name: str) -> None:
        """Render one adopter: position, editable entry, Remove button."""
        var = tk.StringVar(value=name)
        self._name_vars.append(var)
        tk.Label(
            self,
            text=f"{position}.",
            bg=PALETTE["panel"],
            fg=PALETTE["text"],
            font=FONTS["body"],
        ).grid(row=position, column=0, sticky="w", padx=(PAD, 4), pady=2)
        ttk.Entry(self, textvariable=var).grid(
            row=position, column=1, sticky="ew", pady=2
        )
        ttk.Button(
            self,
            text="Remove",
            style="Danger.TButton",
            command=lambda p=position: self._remove(p),
        ).grid(row=position, column=2, sticky="ew", padx=(4, PAD), pady=2)

    def _save(self) -> None:
        """Apply every changed name in place, then close."""
        for position, (var, original) in enumerate(
            zip(self._name_vars, self._original), start=1
        ):
            new_name = var.get().strip()
            if new_name and new_name != original:
                try:
                    self._on_rename(self._animal_type, position, new_name)
                except ValueError as exc:
                    self._error_var.set(str(exc))
                    return
        self.destroy()

    def _remove(self, position: int) -> None:
        """Remove the adopter at a 1-based position, then close."""
        self._on_remove(self._animal_type, position)
        self.destroy()

    def _center_over(self, window: tk.Misc) -> None:
        """Position the dialog over the center of the given window."""
        self.update_idletasks()
        x = window.winfo_rootx() + (window.winfo_width() - self.winfo_width()) // 2
        y = window.winfo_rooty() + (window.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
