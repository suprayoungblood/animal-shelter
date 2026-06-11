"""Main driver — demonstrates the Animal Shelter requirements.

Shows:
  1. Dog, Cat, and Bird inheriting name/age and __str__ from Animal.
  2. Creating a Kennel, adding an animal, and the one-animal rule.
  3. The Shelter constructor setting a kennel capacity.
  4. A new kennel being built when an animal arrives and none are empty.
  5. New animals reusing an empty kennel before a new one is built.
  6. The capacity limit rejecting intakes once every kennel is occupied.
  7. Adoption removing the animal while the kennel stays in the shelter.
  8. Adopters joining a waiting list when their type is unavailable.
  9. An arriving animal going straight to the first waitlisted adopter.

Run with:
    python3 demo.py
"""
from animals import Animal, Bird, Cat, Dog
from kennel import Kennel
from shelter import Shelter

DEMO_CAPACITY = 3


def demonstrate_inheritance() -> None:
    """Create one of each animal and show the shared Animal base class."""
    print("=== Creating animals (each IS-AN Animal) ===")
    for animal in (
        Dog("Charlie", 7, "Golden Retriever"),
        Cat("Luna", 5, "Orange Tabby"),
        Bird("Tweety", 1, 6.5),
    ):
        is_animal = isinstance(animal, Animal)
        print(f"{animal}   (isinstance of Animal -> {is_animal})")


def demonstrate_kennel() -> None:
    """Create a Kennel, add an animal, and show the one-animal rule."""
    print("\n=== A Kennel holds exactly one animal ===")
    kennel = Kennel()
    kennel.add_animal(Dog("Rex", 3, "Beagle"))
    print(f"{kennel}   (GetAnimalType -> {kennel.get_animal_type()})")
    try:
        kennel.add_animal(Cat("Misty", 2, "Gray"))
    except ValueError as exc:
        print(f"Second animal rejected as expected: {exc}")


def main() -> None:
    """Run the demonstration."""
    demonstrate_inheritance()
    demonstrate_kennel()

    print(f"\n=== Creating a shelter with capacity {DEMO_CAPACITY} ===")
    shelter = Shelter(DEMO_CAPACITY)
    print(shelter)

    print("\n=== Intakes build new kennels only when none are empty ===")
    for animal in (
        Dog("Charlie", 7, "Golden Retriever"),
        Cat("Luna", 5, "Orange Tabby"),
        Bird("Tweety", 1, 6.5),
    ):
        result = shelter.add_animal(animal)
        print(f"{animal} -> kennel #{result.kennel_number}   ({shelter})")

    print("\n=== At capacity: a fourth animal is rejected ===")
    try:
        shelter.add_animal(Dog("Rex", 3, "Beagle"))
    except ValueError as exc:
        print(f"Rejected as expected: {exc}")

    print("\n=== Adoption frees the animal but keeps the kennel ===")
    adopted = shelter.adopt("Cat", "Avery")
    print(f"Avery adopted: {adopted}   ({shelter})")

    print("\n=== The freed kennel is reused before any new one is built ===")
    result = shelter.add_animal(Dog("Rex", 3, "Beagle"))
    print(f"Rex placed in reused kennel #{result.kennel_number}   ({shelter})")

    print("\n=== No Cat available, so the adopter joins the waiting list ===")
    adopted = shelter.adopt("Cat", "Blake")
    print(f"Adoption result: {adopted}")
    print(f"Cat waiting list: {shelter.waiting_list['Cat']}")

    print("\n=== An arriving Cat goes straight to the waitlisted adopter ===")
    result = shelter.add_animal(Cat("Milo", 2, "Gray"))
    print(f"Milo adopted on arrival by: {result.adopter}   ({shelter})")
    print(f"Cat waiting list: {shelter.waiting_list['Cat']}")


if __name__ == "__main__":
    main()
