"""Kennel class — holds a single Animal (Dog, Cat, or Bird).

Containment, not inheritance: a Kennel HAS-AN Animal. Because every
animal type inherits from Animal, validation is a single isinstance
check — new Animal subclasses work here automatically.
"""
from animals import ANIMAL_TYPES, Animal


def validate_animal(animal: Animal) -> None:
    """Raise TypeError unless the object is an Animal subclass instance."""
    if not isinstance(animal, Animal):
        allowed = ", ".join(ANIMAL_TYPES)
        raise TypeError(f"Kennel only accepts Animal instances ({allowed}).")


class Kennel:
    """A kennel that contains at most one animal."""

    def __init__(self, animal: Animal | None = None):
        """Overloaded constructor via default argument.

        :param animal: An Animal instance (or None for an empty kennel).
        :raises TypeError: If the provided object is not an Animal.
        """
        if animal is not None:
            validate_animal(animal)
        self.animal = animal

    def is_empty(self) -> bool:
        """Return True when no animal occupies the kennel."""
        return self.animal is None

    def add_animal(self, animal: Animal) -> None:
        """Place an animal in the kennel — but only if it is empty.

        Enforces the rule that a kennel cannot hold more than one animal.

        :param animal: An Animal instance.
        :raises TypeError: If the object is not an Animal.
        :raises ValueError: If the kennel already contains an animal.
        """
        validate_animal(animal)
        if not self.is_empty():
            raise ValueError("Cannot add more than one animal to the kennel.")
        self.animal = animal

    def remove_animal(self) -> Animal:
        """Remove and return the occupant (used when an animal is adopted).

        :return: The animal that was in the kennel.
        :raises ValueError: If the kennel is already empty.
        """
        if self.is_empty():
            raise ValueError("Cannot remove an animal from an empty kennel.")
        animal, self.animal = self.animal, None
        return animal

    def get_animal_type(self) -> str:
        """Return the type name of the contained animal using __name__.

        :return: 'Dog', 'Cat', 'Bird', or 'Empty' when no animal is set.
        """
        if self.is_empty():
            return "Empty"
        return type(self.animal).__name__

    def __str__(self) -> str:
        """Overloaded string representation of the kennel and its occupant."""
        if self.is_empty():
            return "Kennel Animal: Empty"
        return f"Kennel Animal: {self.animal}"
