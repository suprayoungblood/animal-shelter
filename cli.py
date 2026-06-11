"""Animal Shelter — console entry point.

Interactive console app:
  - Create a Dog, Cat, or Bird and add it to the shelter
  - Animals reuse empty kennels; new kennels are built up to capacity
  - View all kennels (occupied and empty)
  - Adopt an animal by type; missing types place the adopter on a waiting list
  - View the waiting list
"""
from typing import Callable

from animals import ANIMAL_TYPES, Bird, Cat, Dog
from shelter import Shelter
from ui import (
    banner,
    clear_screen,
    divider,
    error,
    info,
    pause,
    prompt_choice,
    prompt_float,
    prompt_int,
    prompt_text,
    success,
    title,
)

CAPACITY_MIN, CAPACITY_MAX = 1, 100


def build_dog() -> Dog:
    """Collect input and return a populated Dog. Atomic factory."""
    name = prompt_text("Dog name")
    age = prompt_int("Age in years", minimum=0, maximum=30)
    breed = prompt_text("Breed")
    return Dog(name, age, breed)


def build_cat() -> Cat:
    """Collect input and return a populated Cat. Atomic factory."""
    name = prompt_text("Cat name")
    age = prompt_int("Age in years", minimum=0, maximum=30)
    fur_color = prompt_text("Fur color")
    return Cat(name, age, fur_color)


def build_bird() -> Bird:
    """Collect input and return a populated Bird. Atomic factory."""
    name = prompt_text("Bird name")
    age = prompt_int("Age in years", minimum=0, maximum=80)
    wingspan = prompt_float("Wingspan in inches", minimum=1.0, maximum=400.0)
    return Bird(name, age, wingspan)


ANIMAL_BUILDERS: dict[str, Callable[[], object]] = {
    "Dog": build_dog,
    "Cat": build_cat,
    "Bird": build_bird,
}


def add_animal(shelter: Shelter, animal_type: str) -> None:
    """Build an animal and take it into the shelter."""
    title(f"New {animal_type} Intake")
    animal = ANIMAL_BUILDERS[animal_type]()
    result = shelter.add_animal(animal)
    if result.adopter is not None:
        success(
            f"{animal_type} '{animal.name}' adopted on arrival by "
            f"waitlisted adopter '{result.adopter}'."
        )
    else:
        success(
            f"{animal_type} '{animal.name}' placed in kennel "
            f"#{result.kennel_number}."
        )
    info(str(shelter))


def view_kennels(shelter: Shelter) -> None:
    """Print every kennel and the type of animal it holds."""
    title("All Kennels")
    info(str(shelter))
    if not shelter.kennels:
        info("No kennels yet. Add an animal from the main menu.")
        return
    for index, kennel in enumerate(shelter.kennels, start=1):
        print(f"  #{index} | Animal Type: {kennel.get_animal_type()}")
        print(f"       {kennel}")
        divider()


def prompt_animal_type() -> str:
    """Prompt for one of the registered animal types. Atomic helper."""
    type_menu = {str(i): name for i, name in enumerate(ANIMAL_TYPES, start=1)}
    return type_menu[prompt_choice("Which animal type?", type_menu)]


def adopt_animal(shelter: Shelter) -> None:
    """Adopt an animal by type, or waitlist the adopter when unavailable."""
    title("Adopt an Animal")
    animal_type = prompt_animal_type()
    adopter = prompt_text("Adopter name")
    animal = shelter.adopt(animal_type, adopter)
    if animal is None:
        info(
            f"No {animal_type} is in the shelter right now. "
            f"'{adopter}' was added to the {animal_type} waiting list."
        )
        return
    success(f"'{adopter}' adopted {animal_type} '{animal.name}'. Kennel freed.")


def view_waiting_list(shelter: Shelter) -> None:
    """Print every animal type's waiting list."""
    title("Waiting List")
    for animal_type, adopters in shelter.waiting_list.items():
        names = ", ".join(adopters) if adopters else "(empty)"
        print(f"  {animal_type}: {names}")
    divider()


def build_actions() -> dict[str, tuple[str, Callable[[Shelter], None]]]:
    """Assemble the menu key -> (label, action) table dynamically."""
    actions: dict[str, tuple[str, Callable[[Shelter], None]]] = {}
    for animal_type in ANIMAL_BUILDERS:
        key = str(len(actions) + 1)
        actions[key] = (
            f"Add a {animal_type} to the shelter",
            lambda s, t=animal_type: add_animal(s, t),
        )
    for label, action in (
        ("View all kennels", view_kennels),
        ("Adopt an animal", adopt_animal),
        ("View waiting list", view_waiting_list),
    ):
        actions[str(len(actions) + 1)] = (label, action)
    return actions


ACTIONS = build_actions()
MENU = {key: label for key, (label, _) in ACTIONS.items()} | {"q": "Quit"}


def show_menu(shelter: Shelter) -> str:
    """Render the main menu and return the user's choice."""
    clear_screen()
    banner("ANIMAL SHELTER MANAGER")
    info(str(shelter))
    return prompt_choice("Main Menu", MENU)


def create_shelter() -> Shelter:
    """Prompt for a capacity and construct the Shelter."""
    banner("ANIMAL SHELTER MANAGER")
    info("First, set how many kennels this shelter can hold.")
    capacity = prompt_int(
        "Shelter capacity (max kennels)",
        minimum=CAPACITY_MIN,
        maximum=CAPACITY_MAX,
    )
    return Shelter(capacity)


def run() -> None:
    """Application loop."""
    shelter = create_shelter()
    while True:
        choice = show_menu(shelter)
        if choice == "q":
            success("Goodbye!")
            return
        try:
            ACTIONS[choice][1](shelter)
        except (TypeError, ValueError) as exc:
            error(str(exc))
        pause()


if __name__ == "__main__":
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print()
        info("Session ended.")
