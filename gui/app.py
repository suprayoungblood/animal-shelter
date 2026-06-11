"""Main Tk window — composes the intake form, adoption form, kennel list,
waiting list, and status bar around a single Shelter instance."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui.adoption import AdoptionForm, WaitingListView
from gui.forms import AnimalForm
from gui.kennel_list import KennelList
from gui.styles import FONTS, PAD, PALETTE, WINDOW_SIZE, apply_theme
from shelter import Shelter

APP_TITLE = "Animal Shelter Manager"
SHELTER_CAPACITY = 10


class AnimalShelterApp(tk.Tk):
    """Top-level Tk application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(880, 620)
        apply_theme(self)
        self._shelter = Shelter(SHELTER_CAPACITY)
        self._status_var = tk.StringVar(value="Ready.")
        self._build_layout()
        self._refresh()

    def _build_layout(self) -> None:
        """Assemble header, two-column body, and status bar."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_header().grid(row=0, column=0, sticky="ew", padx=PAD, pady=(PAD, 0))
        self._build_body().grid(row=1, column=0, sticky="nsew", padx=PAD, pady=PAD)
        self._build_status().grid(row=2, column=0, sticky="ew")

    def _build_header(self) -> ttk.Frame:
        """Header band with title and capacity subtitle."""
        frame = ttk.Frame(self, style="App.TFrame")
        ttk.Label(frame, text=APP_TITLE, style="Title.TLabel").pack(anchor="w")
        subtitle = (
            f"Capacity: {SHELTER_CAPACITY} kennels — animals reuse empty "
            "kennels; adopters wait when their type is unavailable."
        )
        ttk.Label(frame, text=subtitle, style="Subtitle.TLabel").pack(anchor="w")
        return frame

    def _build_body(self) -> ttk.Frame:
        """Two-column body: forms on the left, lists on the right."""
        body = ttk.Frame(self, style="App.TFrame")
        body.columnconfigure(0, weight=0, minsize=320)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        self._build_forms(body).grid(row=0, column=0, sticky="nsew", padx=(0, PAD))
        self._build_lists(body).grid(row=0, column=1, sticky="nsew")
        return body

    def _build_forms(self, parent: ttk.Frame) -> ttk.Frame:
        """Left column: animal intake form above the adoption form."""
        column = ttk.Frame(parent, style="App.TFrame")
        column.columnconfigure(0, weight=1)
        form = AnimalForm(column, on_submit=self._handle_add)
        adoption = AdoptionForm(column, on_adopt=self._handle_adopt)
        form.grid(row=0, column=0, sticky="new", pady=(0, PAD))
        adoption.grid(row=1, column=0, sticky="new")
        return column

    def _build_lists(self, parent: ttk.Frame) -> ttk.Frame:
        """Right column: kennel list above the waiting list."""
        column = ttk.Frame(parent, style="App.TFrame")
        column.columnconfigure(0, weight=1)
        column.rowconfigure(0, weight=1)
        self._kennel_list = KennelList(column)
        self._waiting_view = WaitingListView(column)
        self._kennel_list.grid(row=0, column=0, sticky="nsew", pady=(0, PAD))
        self._waiting_view.grid(row=1, column=0, sticky="ew")
        return column

    def _build_status(self) -> tk.Label:
        """Status bar pinned to the bottom of the window."""
        return tk.Label(
            self,
            textvariable=self._status_var,
            bg=PALETTE["panel_alt"],
            fg=PALETTE["text"],
            font=FONTS["small"],
            anchor="w",
            padx=PAD,
            pady=6,
        )

    def _refresh(self) -> None:
        """Redraw both lists from the shelter's current state."""
        self._kennel_list.refresh(self._shelter.kennels)
        self._waiting_view.refresh(self._shelter.waiting_list)

    def _handle_add(self, animal) -> None:
        """House the new animal in the shelter and refresh the lists."""
        try:
            number = self._shelter.add_animal(animal)
        except ValueError as exc:
            self._status_var.set(str(exc))
            return
        self._refresh()
        self._status_var.set(
            f"Added {type(animal).__name__} '{animal.name}' to kennel "
            f"#{number}. {self._shelter}"
        )

    def _handle_adopt(self, animal_type: str, adopter: str) -> None:
        """Adopt an animal of the requested type or waitlist the adopter."""
        animal = self._shelter.adopt(animal_type, adopter)
        self._refresh()
        if animal is None:
            self._status_var.set(
                f"No {animal_type} available — '{adopter.strip()}' added to "
                f"the {animal_type} waiting list."
            )
            return
        self._status_var.set(
            f"'{adopter.strip()}' adopted {animal_type} '{animal.name}'. "
            f"{self._shelter}"
        )


def launch() -> None:
    """Create and run the Tk main loop."""
    AnimalShelterApp().mainloop()
