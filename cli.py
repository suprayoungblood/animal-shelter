"""Animal Shelter — console entry point (the main driver).

Menu-driven console app matching the assignment's six options:
  1. Add Animal
  2. Remove Animal (Adoption)
  3. Get Animal Information
  4. Process Adoption Requests (if new animals arrive)
  5. View Adopters Waiting List
  6. Exit
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


def prompt_animal_type() -> str:
    """Prompt for one of the registered animal types. Atomic helper."""
    type_menu = {str(i): name for i, name in enumerate(ANIMAL_TYPES, start=1)}
    return type_menu[prompt_choice("Which animal type?", type_menu)]


def add_animal(shelter: Shelter) -> None:
    """Option 1: build an animal and take it into the shelter."""
    title("Add Animal")
    animal_type = prompt_animal_type()
    animal = ANIMAL_BUILDERS[animal_type]()
    result = shelter.add_animal(animal)
    if result.reserved_for is not None:
        success(
            f"{animal_type} '{animal.name}' housed in kennel "
            f"#{result.kennel_number} and reserved for waiting adopter "
            f"'{result.reserved_for}' (pending pickup)."
        )
    else:
        success(
            f"{animal_type} '{animal.name}' housed in kennel "
            f"#{result.kennel_number}."
        )
    info(str(shelter))


def adopt_animal(shelter: Shelter) -> None:
    """Option 2: walk-in adoption, or join the waiting list if unavailable."""
    title("Remove Animal (Adoption)")
    animal_type = prompt_animal_type()
    adopter = prompt_text("Adopter name")
    animal = shelter.adopt(animal_type, adopter)
    if animal is None:
        info(
            f"No {animal_type} is available right now. '{adopter}' was "
            f"added to the {animal_type} waiting list."
        )
        return
    success(f"'{adopter}' adopted {animal_type} '{animal.name}'. Kennel freed.")


def get_animal_information(shelter: Shelter) -> None:
    """Option 3: show every kennel's occupant and status."""
    title("Get Animal Information")
    info(str(shelter))
    if not shelter.kennels:
        info("No animals in the shelter yet.")
        return
    for number in range(1, len(shelter.kennels) + 1):
        snapshot = shelter.get_animal_info(number)
        held = f" (reserved for {snapshot.reserved_for})" if snapshot.reserved_for else ""
        print(f"  #{snapshot.kennel_number} | {snapshot.status}{held}")
        print(f"       {snapshot.description}")
        divider()


def process_adoption_requests(shelter: Shelter) -> None:
    """Option 4: confirm or cancel pending pickups from the waiting list."""
    title("Process Adoption Requests")
    pending = shelter.pending_requests()
    if not pending:
        info("No pending adoption requests.")
        return
    for request in pending:
        print(
            f"  Kennel #{request.kennel_number}: {request.animal_type} "
            f"'{request.animal_name}' reserved for {request.adopter}"
        )
    divider()
    number = prompt_int(
        "Kennel number to process", minimum=1, maximum=len(shelter.kennels)
    )
    action = prompt_choice(
        "Action", {"1": "Confirm pickup", "2": "Cancel reservation"}
    )
    if action == "1":
        record = shelter.confirm_pickup(number)
        success(
            f"{record.animal_type} '{record.animal_name}' picked up by "
            f"{record.adopter}. Kennel #{number} is now free."
        )
        return
    adopter = shelter.cancel_reservation(number)
    info(f"Reservation for '{adopter}' on kennel #{number} cancelled.")


def view_waiting_list(shelter: Shelter) -> None:
    """Option 5: print every animal type's waiting list."""
    title("Adopters Waiting List")
    for animal_type, adopters in shelter.waiting_list.items():
        names = ", ".join(adopters) if adopters else "(none waiting)"
        print(f"  {animal_type}: {names}")
    divider()


MENU = {
    "1": "Add Animal",
    "2": "Remove Animal (Adoption)",
    "3": "Get Animal Information",
    "4": "Process Adoption Requests",
    "5": "View Adopters Waiting List",
    "6": "Exit",
}

ACTIONS: dict[str, Callable[[Shelter], None]] = {
    "1": add_animal,
    "2": adopt_animal,
    "3": get_animal_information,
    "4": process_adoption_requests,
    "5": view_waiting_list,
}


def show_menu(shelter: Shelter) -> str:
    """Render the main menu and return the user's choice."""
    clear_screen()
    banner("ANIMAL SHELTER MANAGER")
    info(str(shelter))
    return prompt_choice("Shelter Menu", MENU)


def create_shelter() -> Shelter:
    """Prompt for a capacity and construct the Shelter."""
    banner("ANIMAL SHELTER MANAGER")
    info("First, set how many kennels this shelter can hold.")
    capacity = prompt_int(
        "Enter shelter capacity",
        minimum=CAPACITY_MIN,
        maximum=CAPACITY_MAX,
    )
    return Shelter(capacity)


def run() -> None:
    """Application loop."""
    shelter = create_shelter()
    while True:
        choice = show_menu(shelter)
        if choice == "6":
            success("Goodbye!")
            return
        try:
            ACTIONS[choice](shelter)
        except (TypeError, ValueError) as exc:
            error(str(exc))
        pause()


if __name__ == "__main__":
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print()
        info("Session ended.")
