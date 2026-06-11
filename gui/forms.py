"""Animal forms: the intake form and the edit-animal modal.

Both build animals through the same validation helpers, so the rules
(non-empty name, age range, wingspan range) live once. ANIMAL_SPECS maps
each type to its unique third field (label, kind, attribute, constructor).
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from animals import Animal, Bird, Cat, Dog
from gui.styles import FONTS, PAD, PALETTE

ANIMAL_SPECS: dict[str, dict] = {
    "Dog":  {"third_label": "Breed",             "third_kind": "text",
             "attr": "breed",     "ctor": Dog},
    "Cat":  {"third_label": "Fur Color",         "third_kind": "text",
             "attr": "fur_color", "ctor": Cat},
    "Bird": {"third_label": "Wingspan (inches)", "third_kind": "float",
             "attr": "wingspan",  "ctor": Bird},
}

AGE_MIN, AGE_MAX = 0, 80
WINGSPAN_MIN, WINGSPAN_MAX = 1.0, 400.0


def validated_name(raw: str) -> str:
    """Return a non-empty trimmed name or raise ValueError."""
    name = raw.strip()
    if not name:
        raise ValueError("Name cannot be empty.")
    return name


def validated_age(raw: str) -> int:
    """Return an integer age in range or raise ValueError."""
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise ValueError("Age must be a whole number.") from exc
    if not AGE_MIN <= value <= AGE_MAX:
        raise ValueError(f"Age must be between {AGE_MIN} and {AGE_MAX}.")
    return value


def validated_third(animal_type: str, raw: str):
    """Return the validated type-specific field value (text or float)."""
    spec = ANIMAL_SPECS[animal_type]
    raw = raw.strip()
    if not raw:
        raise ValueError(f"{spec['third_label']} cannot be empty.")
    if spec["third_kind"] == "text":
        return raw
    return _validated_wingspan(raw)


def _validated_wingspan(raw: str) -> float:
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


def build_animal(animal_type: str, name: str, age: str, third: str) -> Animal:
    """Validate raw field strings and construct the matching animal."""
    return ANIMAL_SPECS[animal_type]["ctor"](
        validated_name(name),
        validated_age(age),
        validated_third(animal_type, third),
    )


class AnimalForm(ttk.LabelFrame):
    """A card-styled form for building a single animal."""

    def __init__(self, parent, on_submit: Callable[[Animal], None]):
        """Render the form.

        :param parent: Tk parent widget.
        :param on_submit: Callback invoked with the new animal instance.
        """
        super().__init__(parent, text="  Add an Animal  ", style="Card.TLabelframe")
        self._on_submit = on_submit
        self._type_var = tk.StringVar(value=next(iter(ANIMAL_SPECS)))
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
        tk.Label(
            self,
            textvariable=self._error_var,
            bg=PALETTE["panel"],
            fg=PALETTE["danger"],
            font=FONTS["small"],
            anchor="w",
            justify="left",
        ).grid(row=row, column=0, columnspan=2, sticky="ew", padx=PAD)
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
            animal = build_animal(
                self._type_var.get(),
                self._name_var.get(),
                self._age_var.get(),
                self._third_var.get(),
            )
        except ValueError as exc:
            self._error_var.set(str(exc))
            return
        self._error_var.set("")
        self._on_submit(animal)
        self._reset()

    def _reset(self) -> None:
        """Clear the form for the next entry."""
        self._name_var.set("")
        self._age_var.set("")
        self._third_var.set("")


class EditAnimalModal(tk.Toplevel):
    """A modal for correcting an animal's details (type stays fixed)."""

    def __init__(self, parent, animal: Animal, on_save: Callable[[Animal], None]):
        """Build the dialog pre-filled with the animal's current values.

        :param parent: The widget the dialog was opened from.
        :param animal: The animal being corrected.
        :param on_save: Callback invoked with the corrected replacement.
        """
        super().__init__(parent)
        self._animal_type = type(animal).__name__
        self._on_save = on_save
        spec = ANIMAL_SPECS[self._animal_type]
        self.title(f"Edit {self._animal_type} '{animal.name}'")
        self.configure(bg=PALETTE["panel"])
        self.resizable(False, False)
        self._name_var = tk.StringVar(value=animal.name)
        self._age_var = tk.StringVar(value=str(animal.age))
        self._third_var = tk.StringVar(value=str(getattr(animal, spec["attr"])))
        self._error_var = tk.StringVar()
        self._build(spec["third_label"])
        self.bind("<Escape>", lambda _: self.destroy())
        self.transient(parent.winfo_toplevel())
        try:
            self.grab_set()
        except tk.TclError:
            pass  # window not yet viewable (e.g. headless tests)

    def _build(self, third_label: str) -> None:
        """Construct the entry rows, error label, and action buttons."""
        self.columnconfigure(1, weight=1)
        rows = (
            ("Name", self._name_var),
            ("Age (years)", self._age_var),
            (third_label, self._third_var),
        )
        for row, (label, var) in enumerate(rows):
            ttk.Label(self, text=label, style="Field.TLabel").grid(
                row=row, column=0, sticky="w", padx=PAD, pady=PAD
            )
            ttk.Entry(self, textvariable=var).grid(
                row=row, column=1, sticky="ew", padx=PAD, pady=PAD
            )
        tk.Label(
            self,
            textvariable=self._error_var,
            bg=PALETTE["panel"],
            fg=PALETTE["danger"],
            font=FONTS["small"],
            anchor="w",
        ).grid(row=3, column=0, columnspan=2, sticky="ew", padx=PAD)
        ttk.Button(
            self, text="Save", style="Accent.TButton", command=self._save
        ).grid(row=4, column=0, sticky="ew", padx=PAD, pady=PAD)
        ttk.Button(
            self, text="Cancel", style="Danger.TButton", command=self.destroy
        ).grid(row=4, column=1, sticky="ew", padx=PAD, pady=PAD)

    def _save(self) -> None:
        """Validate the fields, hand back the corrected animal, close."""
        try:
            corrected = build_animal(
                self._animal_type,
                self._name_var.get(),
                self._age_var.get(),
                self._third_var.get(),
            )
        except ValueError as exc:
            self._error_var.set(str(exc))
            return
        self._on_save(corrected)
        self.destroy()
