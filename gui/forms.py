"""Animal creation form widget.

Picks the animal type (Dog / Cat / Bird) and shows the matching third field
(Breed / Fur Color / Wingspan). All input is validated before the animal is
constructed.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from animals import Bird, Cat, Dog
from gui.styles import FONTS, PAD, PALETTE

ANIMAL_SPECS: dict[str, dict] = {
    "Dog":  {"third_label": "Breed",            "third_kind": "text",  "ctor": Dog},
    "Cat":  {"third_label": "Fur Color",        "third_kind": "text",  "ctor": Cat},
    "Bird": {"third_label": "Wingspan (inches)", "third_kind": "float", "ctor": Bird},
}

AGE_MIN, AGE_MAX = 0, 80
WINGSPAN_MIN, WINGSPAN_MAX = 1.0, 400.0


class AnimalForm(ttk.LabelFrame):
    """A card-styled form for building a single animal."""

    def __init__(self, parent, on_submit: Callable[[object], None]):
        """Render the form.

        :param parent: Tk parent widget.
        :param on_submit: Callback invoked with the new animal instance.
        """
        super().__init__(parent, text="  Add an Animal  ", style="Card.TLabelframe")
        self._on_submit = on_submit
        self._type_var = tk.StringVar(value="Dog")
        self._name_var = tk.StringVar()
        self._age_var = tk.StringVar()
        self._third_var = tk.StringVar()
        self._build()
        self._type_var.trace_add("write", lambda *_: self._refresh_third_label())
        self._refresh_third_label()

    def _build(self) -> None:
        """Construct all child widgets."""
        self.columnconfigure(1, weight=1)
        self._row_type(0)
        self._row_entry(1, "Name", self._name_var)
        self._row_entry(2, "Age (years)", self._age_var)
        self._third_label = self._row_entry(3, "Breed", self._third_var)
        self._row_submit(4)

    def _row_type(self, row: int) -> None:
        """Render the animal type dropdown row."""
        ttk.Label(self, text="Type", style="Field.TLabel").grid(
            row=row, column=0, sticky="w", padx=PAD, pady=PAD
        )
        combo = ttk.Combobox(
            self,
            textvariable=self._type_var,
            values=list(ANIMAL_SPECS.keys()),
            state="readonly",
        )
        combo.grid(row=row, column=1, sticky="ew", padx=PAD, pady=PAD)

    def _row_entry(self, row: int, label: str, var: tk.StringVar) -> ttk.Label:
        """Render a labeled entry row and return the label widget."""
        lbl = ttk.Label(self, text=label, style="Field.TLabel")
        lbl.grid(row=row, column=0, sticky="w", padx=PAD, pady=PAD)
        ttk.Entry(self, textvariable=var).grid(
            row=row, column=1, sticky="ew", padx=PAD, pady=PAD
        )
        return lbl

    def _row_submit(self, row: int) -> None:
        """Render the submit button and inline error label."""
        self._error_var = tk.StringVar()
        error_lbl = tk.Label(
            self,
            textvariable=self._error_var,
            bg=PALETTE["panel"],
            fg=PALETTE["danger"],
            font=FONTS["small"],
            anchor="w",
            justify="left",
        )
        error_lbl.grid(row=row, column=0, columnspan=2, sticky="ew", padx=PAD)
        ttk.Button(
            self,
            text="Add to Shelter",
            style="Accent.TButton",
            command=self._submit,
        ).grid(row=row + 1, column=0, columnspan=2, sticky="ew", padx=PAD, pady=PAD)

    def _refresh_third_label(self) -> None:
        """Update the third field's label when the type changes."""
        spec = ANIMAL_SPECS[self._type_var.get()]
        self._third_label.configure(text=spec["third_label"])

    def _submit(self) -> None:
        """Validate inputs and invoke the on_submit callback."""
        try:
            animal = self._build_animal()
        except ValueError as exc:
            self._error_var.set(str(exc))
            return
        self._error_var.set("")
        self._on_submit(animal)
        self._reset()

    def _build_animal(self) -> object:
        """Validate fields and construct the matching animal. Atomic."""
        name = self._validated_name()
        age = self._validated_age()
        third = self._validated_third()
        spec = ANIMAL_SPECS[self._type_var.get()]
        return spec["ctor"](name, age, third)

    def _validated_name(self) -> str:
        """Return a non-empty trimmed name or raise ValueError."""
        name = self._name_var.get().strip()
        if not name:
            raise ValueError("Name cannot be empty.")
        return name

    def _validated_age(self) -> int:
        """Return an integer age in range or raise ValueError."""
        raw = self._age_var.get().strip()
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError("Age must be a whole number.") from exc
        if not AGE_MIN <= value <= AGE_MAX:
            raise ValueError(f"Age must be between {AGE_MIN} and {AGE_MAX}.")
        return value

    def _validated_third(self):
        """Return the validated third field value (text or float)."""
        spec = ANIMAL_SPECS[self._type_var.get()]
        raw = self._third_var.get().strip()
        if not raw:
            raise ValueError(f"{spec['third_label']} cannot be empty.")
        if spec["third_kind"] == "text":
            return raw
        return self._validated_wingspan(raw)

    def _validated_wingspan(self, raw: str) -> float:
        """Parse and range-check a wingspan value."""
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError("Wingspan must be a number.") from exc
        if not WINGSPAN_MIN <= value <= WINGSPAN_MAX:
            raise ValueError(
                f"Wingspan must be between {WINGSPAN_MIN} and {WINGSPAN_MAX}."
            )
        return value

    def _reset(self) -> None:
        """Clear the form for the next entry."""
        self._name_var.set("")
        self._age_var.set("")
        self._third_var.set("")
