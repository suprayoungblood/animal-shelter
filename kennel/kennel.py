"""Kennel class — holds a single animal (Dog, Cat, or Bird).

Containment, not inheritance: a Kennel HAS-A animal.
"""
from animals import ANIMAL_TYPES, Bird, Cat, Dog

AllowedAnimal = Dog | Cat | Bird
ALLOWED_CLASSES = tuple(ANIMAL_TYPES.values())


def _validate_animal(animal: AllowedAnimal) -> None:
    """Raise TypeError unless the object is a registered animal type."""
    if not isinstance(animal, ALLOWED_CLASSES):
        allowed = ", ".join(ANIMAL_TYPES)
        raise TypeError(f"Kennel only accepts {allowed} instances.")


class Kennel:
    """A kennel that contains at most one animal."""

    def __init__(self, animal: AllowedAnimal | None = None):
        """Overloaded constructor via default argument.

        :param animal: A Dog, Cat, or Bird instance (or None for an empty kennel).
        :raises TypeError: If the provided object is not a Dog, Cat, or Bird.
        """
        if animal is not None:
            _validate_animal(animal)
        self.animal = animal

    def is_empty(self) -> bool:
        """Return True when no animal occupies the kennel."""
        return self.animal is None

    def add_animal(self, animal: AllowedAnimal) -> None:
        """Place an animal in the kennel — but only if it is empty.

        Enforces the rule that a kennel cannot hold more than one animal.

        :param animal: A Dog, Cat, or Bird instance.
        :raises TypeError: If the object is not a Dog, Cat, or Bird.
        :raises ValueError: If the kennel already contains an animal.
        """
        _validate_animal(animal)
        if not self.is_empty():
            raise ValueError("Cannot add more than one animal to the kennel.")
        self.animal = animal

    def remove_animal(self) -> AllowedAnimal:
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
