# Animal Shelter Simulator

A small object-oriented Python program. It defines three independent animal
classes — **Dog**, **Cat**, and **Bird** — a **Kennel** that holds at most one
animal, and a **Shelter** that manages a capacity-limited collection of
kennels plus a per-type adoption **waiting list**. Every relationship is
**containment ("has-a")**, *not* inheritance: the Shelter *has* kennels and a
Kennel *has an* animal. There is **no inheritance anywhere** in the program.

It ships with two ways to run it (a console demo and a desktop GUI) and a full
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
| Arriving animals fulfill the waiting list (FIFO) | `Shelter.add_animal()` → `_pop_waiting_adopter()` |
| **Dog / Cat / Bird** (Name, Age, Breed / Fur Color / Wingspan) | `animals/dog.py`, `animals/cat.py`, `animals/bird.py` |
| Overloaded constructor / `__str__` (all classes) | `__init__` defaults and `__str__` in each class |
| **Kennel** holds at most one animal | `kennel/kennel.py` — `add_animal()` raises if occupied |
| **GetAnimalType** using `__name__` | `Kennel.get_animal_type()` → `type(self.animal).__name__` |
| Unit tests | `tests/` — 50 tests across animals, kennel, and shelter |
| Main driver | `demo.py` (console) and `main.py` (GUI) |

---

## The classes

### Dog / Cat / Bird (`animals/`)
Three standalone classes, one attribute set each:

```python
Dog(name, age, breed)
Cat(name, age, fur_color)
Bird(name, age, wingspan)
```

The package also exposes `ANIMAL_TYPES`, a registry dict that the kennel,
shelter, CLI, and GUI all derive their type lists from — adding a new animal
class is a one-line change.

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
- **`add_animal(animal)`** — if adopters are **waiting for this type**, the
  first in line adopts the animal immediately (no kennel used). Otherwise it
  goes into the **first empty kennel**; only if none are empty does the
  shelter build a new kennel, and only while under capacity. At capacity with
  no empty kennels, intake is rejected. Returns an `IntakeResult` naming
  either the kennel number or the adopter.
- **`adopt(animal_type, adopter)`** — removes the animal from its kennel and
  returns it; **the kennel stays** in the shelter for reuse. If no animal of
  that type is housed, the adopter joins that type's **waiting list** (FIFO)
  and `None` is returned. Type matching is case-insensitive via a lookup table.
- **`adoptions`** — every completed adoption (from a kennel or on arrival) is
  recorded as an `AdoptionRecord`, giving both UIs an adoption log.

---

## How to run

### 1. Console demo (simplest — proves every requirement)

```bash
python3 demo.py
```

It walks through, in order: setting the capacity, kennels being built on
demand, intake rejection at capacity, adoption freeing an animal while keeping
the kennel, the freed kennel being reused, and an adopter joining the waiting
list.

### 2. Interactive console app

```bash
python3 cli.py
```

Menu-driven: set the shelter capacity, add Dogs/Cats/Birds, view all kennels
(occupied and empty), adopt by type, and view the waiting list and adoption log.

### 3. Desktop GUI

The GUI needs a Python build that includes **Tk**. The Homebrew `python3` on
macOS usually does **not**; the official **python.org** build does.

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 main.py
```

…or any `python3` for which `python3 -c "import tkinter"` succeeds. The window
has the intake and adoption forms on the left, with the kennel list, waiting
list, and adoption log on the right — every panel resizes with the window.
Clicking a waiting-list row opens a dialog naming the adopters in line.

---

## Running the unit tests

```bash
python3 -m unittest discover -s tests -v
```

**50 tests, all passing.** They verify:

- each animal constructor, default arguments, and `__str__` format
- the one-animal-per-kennel rule, `remove_animal()`, and `is_empty()`
- the shelter capacity rule (set in the constructor, enforced on intake)
- empty kennels being reused before new ones are built
- adoption returning the animal while keeping the kennel
- waitlisting (including FIFO order) when a type isn't available
- arriving animals being adopted on arrival by the first waitlisted adopter
- invalid capacities, unknown types, and blank adopter names being rejected
- no class uses inheritance

---

## Project structure

```
Animal/
├── README.md
├── demo.py                 # Main driver — console demonstration of all requirements
├── main.py                 # Entry point — launches the GUI
├── cli.py                  # Interactive console version
├── animals/
│   ├── dog.py              # Dog  (Name, Age, Breed)
│   ├── cat.py              # Cat  (Name, Age, Fur Color)
│   └── bird.py             # Bird (Name, Age, Wingspan)
├── kennel/
│   └── kennel.py           # Kennel container (has-a animal)
├── shelter/
│   └── shelter.py          # Shelter — capacity, kennel reuse, adoption, waiting list
├── tests/
│   ├── test_animals.py     # Unit tests for Dog / Cat / Bird
│   ├── test_kennel.py      # Unit tests for Kennel + the one-animal rule
│   └── test_shelter.py     # Unit tests for capacity, reuse, adoption, waitlist
├── gui/                    # Tkinter desktop front end
│   ├── app.py              # Main window
│   ├── forms.py            # Animal intake form
│   ├── adoption.py         # Adoption form + waiting list panel + adopters dialog
│   ├── adoption_log.py     # History of completed adoptions
│   ├── kennel_list.py      # List of all kennels
│   └── styles.py           # Colors / fonts / theme
├── ui/console.py           # Console formatting helpers used by cli.py
├── uml/class_diagram.md    # UML class diagram (containment, no inheritance)
└── scripts/                # Helper scripts for generating screenshots
```

---

## Key design points (good talking points)

- **No inheritance** — every relationship is containment (has-a), shown with
  aggregation in the UML: Shelter HAS Kennels, a Kennel HAS-A animal.
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
