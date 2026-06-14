"""Main Tk window — composes the intake form, adoption form, kennel list,
waiting list, and status bar around a single Shelter instance."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui.adoption import AdoptionForm, WaitingListView
from gui.adoption_log import AdoptionLogView
from gui.forms import AnimalForm, EditAnimalModal
from gui.kennel_list import KennelList
from gui.requests import PendingRequestsModal
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
        self.minsize(720, 540)
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
        """Two-column body: forms on the left, lists on the right.

        Both columns carry grid weights so every panel grows and shrinks
        with the window.
        """
        body = ttk.Frame(self, style="App.TFrame")
        body.columnconfigure(0, weight=1, minsize=300)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)
        self._build_forms(body).grid(row=0, column=0, sticky="nsew", padx=(0, PAD))
        self._build_lists(body).grid(row=0, column=1, sticky="nsew")
        return body

    def _build_forms(self, parent: ttk.Frame) -> ttk.Frame:
        """Left column: animal intake form above the adoption form."""
        column = ttk.Frame(parent, style="App.TFrame")
        column.columnconfigure(0, weight=1)
        column.rowconfigure(2, weight=1)
        form = AnimalForm(column, on_submit=self._handle_add)
        adoption = AdoptionForm(column, on_adopt=self._handle_adopt)
        form.grid(row=0, column=0, sticky="new", pady=(0, PAD))
        adoption.grid(row=1, column=0, sticky="new")
        return column

    def _build_lists(self, parent: ttk.Frame) -> ttk.Frame:
        """Right column: kennels, waiting list, and adoption log stacked."""
        column = ttk.Frame(parent, style="App.TFrame")
        column.columnconfigure(0, weight=1)
        column.rowconfigure(0, weight=3)
        column.rowconfigure(1, weight=1)
        column.rowconfigure(2, weight=1)
        self._kennel_list = KennelList(
            column,
            on_edit=self._handle_edit,
            on_remove=self._handle_remove,
            on_process=self._handle_process_requests,
        )
        self._waiting_view = WaitingListView(
            column,
            on_rename=self._handle_waiting_rename,
            on_remove=self._handle_waiting_remove,
        )
        self._log_view = AdoptionLogView(column)
        self._kennel_list.grid(row=0, column=0, sticky="nsew", pady=(0, PAD))
        self._waiting_view.grid(row=1, column=0, sticky="nsew", pady=(0, PAD))
        self._log_view.grid(row=2, column=0, sticky="nsew")
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
        """Redraw every list from the shelter's current state."""
        self._kennel_list.refresh(self._shelter)
        self._waiting_view.refresh(self._shelter.waiting_list)
        self._log_view.refresh(self._shelter.adoptions)

    def _handle_add(self, animal) -> None:
        """Take in the new animal and refresh the lists."""
        try:
            result = self._shelter.add_animal(animal)
        except ValueError as exc:
            self._status_var.set(str(exc))
            return
        self._refresh()
        animal_type = type(animal).__name__
        if result.reserved_for is not None:
            self._status_var.set(
                f"{animal_type} '{animal.name}' housed in kennel "
                f"#{result.kennel_number} and reserved for "
                f"'{result.reserved_for}' (pending pickup). {self._shelter}"
            )
            return
        self._status_var.set(
            f"Added {animal_type} '{animal.name}' to kennel "
            f"#{result.kennel_number}. {self._shelter}"
        )

    def _handle_edit(self, kennel_number: int) -> None:
        """Open the edit modal for the selected kennel's animal."""
        kennel = self._shelter.kennels[kennel_number - 1]
        if kennel.is_empty():
            self._status_var.set(f"Kennel #{kennel_number} is empty.")
            return
        EditAnimalModal(
            self,
            kennel.animal,
            on_save=lambda fixed: self._apply_edit(kennel_number, fixed),
        )

    def _apply_edit(self, kennel_number: int, corrected) -> None:
        """Swap in the corrected animal and refresh."""
        replaced = self._shelter.replace_animal(kennel_number, corrected)
        self._refresh()
        self._status_var.set(
            f"Updated kennel #{kennel_number}: '{replaced.name}' is now "
            f"'{corrected.name}'."
        )

    def _handle_remove(self, kennel_number: int) -> None:
        """Remove a mistakenly added animal (not logged as an adoption)."""
        kennel = self._shelter.kennels[kennel_number - 1]
        if kennel.is_empty():
            self._status_var.set(f"Kennel #{kennel_number} is already empty.")
            return
        removed = self._shelter.remove_animal(kennel_number)
        self._refresh()
        self._status_var.set(
            f"Removed {type(removed).__name__} '{removed.name}' from kennel "
            f"#{kennel_number} (data fix, not an adoption)."
        )

    def _handle_process_requests(self) -> None:
        """Open the pending-pickup workflow."""
        PendingRequestsModal(
            self,
            self._shelter.pending_requests(),
            on_confirm=self._confirm_pickup,
            on_cancel=self._cancel_reservation,
        )

    def _confirm_pickup(self, kennel_number: int) -> None:
        """Finalize a pending pickup and refresh."""
        record = self._shelter.confirm_pickup(kennel_number)
        self._refresh()
        self._status_var.set(
            f"{record.animal_type} '{record.animal_name}' picked up by "
            f"{record.adopter}. Kennel #{kennel_number} is now free."
        )

    def _cancel_reservation(self, kennel_number: int) -> None:
        """Cancel a pending pickup and refresh."""
        adopter = self._shelter.cancel_reservation(kennel_number)
        self._refresh()
        self._status_var.set(
            f"Reservation for '{adopter}' on kennel #{kennel_number} cancelled."
        )

    def _handle_waiting_rename(
        self, animal_type: str, position: int, new_name: str
    ) -> None:
        """Correct a waitlisted adopter's name."""
        self._shelter.rename_waiting_adopter(animal_type, position, new_name)
        self._refresh()
        self._status_var.set(
            f"Renamed {animal_type} waiting list position {position} "
            f"to '{new_name}'."
        )

    def _handle_waiting_remove(self, animal_type: str, position: int) -> None:
        """Remove an adopter from a waiting list."""
        removed = self._shelter.remove_waiting_adopter(animal_type, position)
        self._refresh()
        self._status_var.set(
            f"Removed '{removed}' from the {animal_type} waiting list."
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
