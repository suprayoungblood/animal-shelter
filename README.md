# Animal Shelter Simulator

A small object-oriented Python program. An **Animal** base class holds the
attributes every animal shares (`name`, `age`, `__str__`); **Dog**, **Cat**,
and **Bird** inherit from it and add one unique attribute each. A **Kennel**
holds at most one animal, and a **Shelter** manages a capacity-limited
collection of kennels plus a per-type adoption **waiting list**. Both
relationship kinds are used where they belong: **inheritance ("is-a")** for
Dog/Cat/Bird → Animal, and **containment ("has-a")** for Shelter → Kennels →
animal.

It ships with two ways to run it (a console app and a desktop GUI) and a full
**unit-test suite**.

---

## Requirements → where they live

Use this table to find any assignment requirement in the code.

| Requirement | Implemented in |
| --- | --- |
| **Shelter added to the model** | `shelter/shelter.py`, diagram in `uml/class_diagram.md` |
| **Constructor sets the capacity** (max kennels) | `Shelter.__init__(capacity)` |
| **No new kennels once capacity is reached** | `Shelter._build_kennel()` raises `ValueError` when full |
| **Kennel built only when an animal arrives and none are empty** | `Shelter.add_animal()` |
| **New animals always reuse an empty kennel first** | `Shelter._find_empty_kennel()` checked before building |
| **Adoption removes the animal from its kennel** (kennel stays) | `Shelter.adopt()` → `Kennel.remove_animal()` |
| **Waiting list when the requested type isn't housed** | `Shelter.adopt()` appends to `Shelter.waiting_list` |
| Arriving animals auto-reserve for the first waiter (FIFO) | `Shelter.add_animal()` → `_auto_match()` |
| **Unit test for the Shelter object** | `tests/test_shelter.py` |
| **Main driver: add / adopt / waitlist / get info / process / exit** | `cli.py` six-option menu |
| **Animal base class** (shared `name`, `age`, `__str__`) | `animals/animal.py` |
| **Dog / Cat / Bird inherit from Animal** (one unique attribute each) | `animals/dog.py`, `animals/cat.py`, `animals/bird.py` |
| **Kennel uses the new Animal-based types** | `kennel/kennel.py` — `isinstance(animal, Animal)` |
| **UML shows inheritance connectors** | `uml/class_diagram.md` — `Animal <\|-- Dog/Cat/Bird` |
| Overloaded constructor / `__str__` (all classes) | `__init__` defaults and `__str__` in each class |
| **Kennel** holds at most one animal | `kennel/kennel.py` — `add_animal()` raises if occupied |
| **GetAnimalType** using `__name__` | `Kennel.get_animal_type()` → `type(self.animal).__name__` |
| Unit tests | `tests/` — 64 tests across animals, kennel, and shelter |
| Main driver | `main.py` (GUI) and `cli.py` (console) |

---

## The classes

### Animal and its subclasses (`animals/`)
`Animal` is the base class: it stores `name` and `age` and provides the
shared `__str__`. Dog, Cat, and Bird extend it, each adding exactly one
attribute and extending `__str__` via `super()`:

```python
Animal(name, age)            # base — shared attributes and __str__
Dog(name, age, breed)        # Dog IS-AN Animal
Cat(name, age, fur_color)    # Cat IS-AN Animal
Bird(name, age, wingspan)    # Bird IS-AN Animal
```

The package also exposes `ANIMAL_TYPES`, a registry dict that the shelter,
CLI, and GUI all derive their type lists from — adding a new Animal subclass
is a one-line change.

### Kennel (`kennel/kennel.py`)
A container that holds **at most one** animal.

- `Kennel()` starts empty; `Kennel(dog)` starts occupied. Non-animals raise `TypeError`.
- `add_animal(animal)` — only works on an empty kennel; otherwise `ValueError`.
- `remove_animal()` — hands back the occupant (used for adoption) and empties the kennel.
- `get_animal_type()` — the animal's class name via `__name__`, or `"Empty"`.

### Shelter (`shelter/shelter.py`)
Owns the kennels and enforces every shelter rule:

- **`Shelter(capacity)`** — the constructor fixes how many kennels the shelter
  can ever hold; invalid capacities raise `ValueError`.
- **`add_animal(animal)`** — houses the animal in the **first empty kennel**,
  building a new one only when none are empty and only while under capacity.
  If adopters are **waiting for this type**, the animal is auto-reserved for
  the first in line and held as a pending pickup. Returns an `IntakeResult`
  with the kennel number and any reserved-for name.
- **`adopt(animal_type, adopter)`** — a walk-in adoption: removes an
  **available** animal of that type and returns it (the kennel stays for
  reuse). Reserved animals are not offered. If none is available, the adopter
  joins that type's **waiting list** (FIFO). Type matching is case-insensitive.
- **`pending_requests()` / `confirm_pickup()` / `cancel_reservation()`** — the
  pending-pickup workflow. Confirming logs the adoption and frees the kennel;
  cancelling reopens the animal and re-matches the next person in line.
- **`adoptions`** — every confirmed adoption (walk-in or from the waiting
  list) is recorded as an `AdoptionRecord`, giving both UIs an adoption log.
- **Corrections** — `replace_animal()` and `remove_animal()` fix data-entry
  mistakes without touching the adoption log, and `rename_waiting_adopter()` /
  `remove_waiting_adopter()` edit the waiting list while preserving line order.

---

## How to run

### 1. Console app (the main driver)

```bash
python3 cli.py
```

Prompts for the shelter capacity, then shows the six-option menu: Add Animal,
Remove Animal (Adoption), Get Animal Information, Process Adoption Requests,
View Adopters Waiting List, and Exit. Walk-in adoptions complete immediately;
when an animal someone is waiting for arrives, it is held as a pending pickup
that you finalize under "Process Adoption Requests."

### 2. Desktop GUI

The GUI needs a Python build that includes **Tk**. The Homebrew `python3` on
macOS usually does **not**; the official **python.org** build does.

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 main.py
```

…or any `python3` for which `python3 -c "import tkinter"` succeeds. The window
has the intake and adoption forms on the left, with the kennel list, waiting
list, and adoption log on the right — every panel resizes with the window. The
kennel list shows each animal's status (Available / Reserved → adopter); the
Process Requests button confirms or cancels pending pickups. Double-click a
kennel row (or Edit Selected) to correct an animal; Remove Selected deletes a
mistaken entry. Clicking a waiting-list row opens a dialog where the adopters
in line can be viewed, renamed, or removed.

---

## Running the unit tests

```bash
python3 -m unittest discover -s tests -v
```

**64 tests, all passing.** They verify:

- each animal constructor, default arguments, and `__str__` format
- the one-animal-per-kennel rule, `remove_animal()`, and `is_empty()`
- the shelter capacity rule (set in the constructor, enforced on intake)
- empty kennels being reused before new ones are built
- adoption returning the animal while keeping the kennel
- waitlisting (including FIFO order) when a type isn't available
- arriving animals being auto-reserved for the first waitlisted adopter, and
  the confirm/cancel pending-pickup workflow (including re-matching on cancel)
- `get_animal_info` reporting Available / Reserved / Empty status
- invalid capacities, unknown types, and blank adopter names being rejected
- corrections (replace/remove animal, rename/remove waiting adopter) working
  in place and never touching the adoption log
- Dog, Cat, and Bird each inherit from Animal (and Kennel deliberately does not)

---

## Project structure

```
Animal/
├── README.md
├── main.py                 # Entry point — launches the GUI
├── cli.py                  # Interactive console version
├── animals/
│   ├── animal.py           # Animal base class (name, age, __str__)
│   ├── dog.py              # Dog  IS-AN Animal (+ breed)
│   ├── cat.py              # Cat  IS-AN Animal (+ fur color)
│   └── bird.py             # Bird IS-AN Animal (+ wingspan)
├── kennel/
│   └── kennel.py           # Kennel container (has-a animal)
├── shelter/
│   ├── shelter.py          # Shelter — capacity, reuse, adoption, reservations, waitlist
│   └── records.py          # Plain result records (IntakeResult, PendingRequest, ...)
├── tests/
│   ├── test_animals.py     # Unit tests for Animal + Dog / Cat / Bird
│   ├── test_kennel.py      # Unit tests for Kennel + the one-animal rule
│   └── test_shelter.py     # Unit tests for capacity, reuse, adoption, waitlist
├── gui/                    # Tkinter desktop front end
│   ├── app.py              # Main window
│   ├── forms.py            # Animal intake form + edit-animal dialog
│   ├── adoption.py         # Adoption form + waiting list panel + adopters dialog
│   ├── adoption_log.py     # History of completed adoptions
│   ├── kennel_list.py      # Kennel list with status + correction controls
│   ├── requests.py         # Pending-pickup (Process Adoption Requests) dialog
│   └── styles.py           # Colors / fonts / theme
├── ui/console.py           # Console formatting helpers used by cli.py
├── uml/class_diagram.md    # UML class diagram (inheritance + containment)
└── scripts/                # Helper scripts for generating screenshots
```

---

## Key design points (good talking points)

- **Inheritance and containment, each where it belongs** — Dog/Cat/Bird ARE
  Animals (shared `name`/`age`/`__str__` live once in the base class), while
  Shelter HAS Kennels and a Kennel HAS-AN Animal (aggregation in the UML).
- **Validation by base class** — Kennel and Shelter accept anything that
  `isinstance`-checks as an `Animal`, so new subclasses work untouched.
- **The capacity rule lives in one place** — only `Shelter._build_kennel()`
  can create kennels, so the limit can't be bypassed.
- **Kennel reuse before construction** — `add_animal()` checks for an empty
  kennel first, so adopted-out kennels are recycled.
- **Overloaded constructors via default arguments** — the Pythonic equivalent
  of constructor overloading.
- **Dynamic type registry** — `ANIMAL_TYPES` is the single source of truth for
  valid animal types; nothing hard-codes `"Dog"`/`"Cat"`/`"Bird"` lists.
- **Standard library only** — no third-party runtime dependencies.

---

## Difficulties encountered (for the write-up / video)

- Python doesn't support traditional constructor overloading, so I used
  **default parameters** to get the same effect.
- The Homebrew Python on macOS has no Tk, so the GUI must be launched with the
  **python.org Framework build** (`/Library/Frameworks/...`).
- Deciding where each rule belongs: the **one-animal rule** stays in `Kennel`,
  while **capacity, reuse, adoption, and waitlisting** belong to `Shelter` —
  keeping each class responsible for exactly its own invariants.
