"""Shelter class — owns a capacity-limited collection of kennels.

Rules enforced here:
  - The constructor sets the kennel capacity; once reached, no new
    kennels can be created.
  - Incoming animals always reuse an empty kennel when one exists;
    a new kennel is only built when none are empty.
  - Adoption removes the animal but keeps the kennel for reuse.
  - Adopters asking for an animal type not currently housed are
    placed on a per-type waiting list (FIFO).
  - An arriving animal whose type has waiting adopters goes straight
    to the first person in line instead of into a kennel.
"""
from typing import NamedTuple

from animals import ANIMAL_TYPES, Animal
from kennel import Kennel
from kennel.kennel import validate_animal

# Case-insensitive lookup table: 'dog' -> 'Dog'. Plain data structure,
# derived from the registry so new animal types need no changes here.
_TYPE_LOOKUP: dict[str, str] = {name.casefold(): name for name in ANIMAL_TYPES}


class IntakeResult(NamedTuple):
    """Outcome of an intake — exactly one field is set.

    kennel_number: 1-based kennel the animal was housed in, or None.
    adopter: waitlisted adopter who took the animal on arrival, or None.
    """

    kennel_number: int | None
    adopter: str | None


class AdoptionRecord(NamedTuple):
    """One completed adoption, kept in the shelter's log."""

    animal_type: str
    animal_name: str
    adopter: str
    on_arrival: bool


class Shelter:
    """An animal shelter holding up to `capacity` kennels."""

    def __init__(self, capacity: int):
        """Create a shelter with a fixed kennel capacity.

        :param capacity: Maximum number of kennels the shelter can hold.
        :raises ValueError: If capacity is not a positive whole number.
        """
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
            raise ValueError("Shelter capacity must be a positive whole number.")
        self.capacity = capacity
        self.kennels: list[Kennel] = []
        self.waiting_list: dict[str, list[str]] = {name: [] for name in ANIMAL_TYPES}
        self.adoptions: list[AdoptionRecord] = []

    def is_full(self) -> bool:
        """Return True when no more kennels can be added."""
        return len(self.kennels) >= self.capacity

    def occupied_count(self) -> int:
        """Return how many kennels currently hold an animal."""
        return sum(1 for kennel in self.kennels if not kennel.is_empty())

    def add_animal(self, animal: Animal) -> IntakeResult:
        """Take in an animal: fulfill the waiting list or house it.

        If adopters are waiting for this animal's type, the first in line
        adopts it immediately and no kennel is used. Otherwise the animal
        goes into an empty kennel, building a new one only when none are
        empty.

        :param animal: A Dog, Cat, or Bird instance.
        :return: IntakeResult with either the kennel number or the adopter.
        :raises TypeError: If the object is not a registered animal type.
        :raises ValueError: If every kennel is occupied and the shelter
            is at capacity.
        """
        validate_animal(animal)
        adopter = self._pop_waiting_adopter(type(animal).__name__)
        if adopter is not None:
            self._record_adoption(animal, adopter, on_arrival=True)
            return IntakeResult(kennel_number=None, adopter=adopter)
        kennel = self._find_empty_kennel() or self._build_kennel()
        kennel.add_animal(animal)
        return IntakeResult(self.kennels.index(kennel) + 1, None)

    def _pop_waiting_adopter(self, animal_type: str) -> str | None:
        """Dequeue the first adopter waiting for this type, if any."""
        waiting = self.waiting_list[animal_type]
        return waiting.pop(0) if waiting else None

    def _record_adoption(
        self, animal: Animal, adopter: str, on_arrival: bool
    ) -> None:
        """Append a completed adoption to the shelter's log."""
        self.adoptions.append(
            AdoptionRecord(type(animal).__name__, animal.name, adopter, on_arrival)
        )

    def adopt(self, animal_type: str, adopter: str) -> Animal | None:
        """Adopt an animal of the requested type out of the shelter.

        The kennel stays in the shelter for reuse. When no animal of the
        requested type is housed, the adopter joins that type's waiting list.

        :param animal_type: Requested type name (case-insensitive).
        :param adopter: Name of the person adopting.
        :return: The adopted animal, or None if the adopter was waitlisted.
        :raises ValueError: If the type is unknown or the adopter name is blank.
        """
        normalized = self._normalize_type(animal_type)
        adopter = self._validated_adopter(adopter)
        kennel = self._find_kennel_holding(normalized)
        if kennel is None:
            self.waiting_list[normalized].append(adopter)
            return None
        animal = kennel.remove_animal()
        self._record_adoption(animal, adopter, on_arrival=False)
        return animal

    def replace_animal(self, kennel_number: int, animal: Animal) -> Animal:
        """Swap a kennel's occupant for a corrected one (data fix).

        Not an adoption: nothing is logged and the kennel stays occupied.

        :param kennel_number: 1-based kennel holding the animal to fix.
        :param animal: The corrected replacement animal.
        :return: The animal that was replaced.
        :raises TypeError: If the replacement is not an Animal.
        :raises ValueError: If the kennel number is invalid or the kennel
            is empty.
        """
        validate_animal(animal)
        kennel = self._kennel_at(kennel_number)
        replaced = kennel.remove_animal()
        kennel.add_animal(animal)
        return replaced

    def remove_animal(self, kennel_number: int) -> Animal:
        """Remove an animal added by mistake (data fix, not an adoption).

        Nothing is logged; the kennel stays in the shelter for reuse.

        :param kennel_number: 1-based kennel to empty.
        :return: The removed animal.
        :raises ValueError: If the kennel number is invalid or the kennel
            is already empty.
        """
        return self._kennel_at(kennel_number).remove_animal()

    def rename_waiting_adopter(
        self, animal_type: str, position: int, new_name: str
    ) -> None:
        """Correct a waitlisted adopter's name, keeping their place in line.

        :param animal_type: The waiting list to edit (case-insensitive).
        :param position: 1-based place in line.
        :param new_name: The corrected adopter name.
        :raises ValueError: If the type, position, or name is invalid.
        """
        names = self.waiting_list[self._normalize_type(animal_type)]
        names[self._validated_position(names, position)] = (
            self._validated_adopter(new_name)
        )

    def remove_waiting_adopter(self, animal_type: str, position: int) -> str:
        """Remove an adopter from a waiting list (withdrawal or mistake).

        :param animal_type: The waiting list to edit (case-insensitive).
        :param position: 1-based place in line.
        :return: The removed adopter's name.
        :raises ValueError: If the type or position is invalid.
        """
        names = self.waiting_list[self._normalize_type(animal_type)]
        return names.pop(self._validated_position(names, position))

    def _kennel_at(self, kennel_number: int) -> Kennel:
        """Return the kennel for a 1-based number or raise ValueError."""
        if (
            not isinstance(kennel_number, int)
            or isinstance(kennel_number, bool)
            or not 1 <= kennel_number <= len(self.kennels)
        ):
            raise ValueError(
                f"Kennel number must be between 1 and {len(self.kennels)}."
            )
        return self.kennels[kennel_number - 1]

    @staticmethod
    def _validated_position(names: list[str], position: int) -> int:
        """Convert a 1-based position to an index or raise ValueError."""
        if (
            not isinstance(position, int)
            or isinstance(position, bool)
            or not 1 <= position <= len(names)
        ):
            raise ValueError(
                f"Position must be between 1 and {len(names)}."
            )
        return position - 1

    def _find_empty_kennel(self) -> Kennel | None:
        """Return the first empty kennel, or None when all are occupied."""
        return next((kennel for kennel in self.kennels if kennel.is_empty()), None)

    def _find_kennel_holding(self, animal_type: str) -> Kennel | None:
        """Return the first kennel housing the given type, or None."""
        return next(
            (k for k in self.kennels if k.get_animal_type() == animal_type),
            None,
        )

    def _build_kennel(self) -> Kennel:
        """Add a new empty kennel, enforcing the capacity limit.

        :raises ValueError: If the shelter already holds `capacity` kennels.
        """
        if self.is_full():
            raise ValueError(
                f"Shelter is at capacity ({self.capacity} kennels); "
                "no new kennels can be added."
            )
        kennel = Kennel()
        self.kennels.append(kennel)
        return kennel

    @staticmethod
    def _normalize_type(animal_type: str) -> str:
        """Map user input to a canonical type name via the lookup table.

        :raises ValueError: If the type is not a registered animal type.
        """
        normalized = _TYPE_LOOKUP.get(str(animal_type).strip().casefold())
        if normalized is None:
            allowed = ", ".join(ANIMAL_TYPES)
            raise ValueError(f"Unknown animal type. Choose one of: {allowed}.")
        return normalized

    @staticmethod
    def _validated_adopter(adopter: str) -> str:
        """Return a trimmed adopter name or raise ValueError when blank."""
        adopter = str(adopter).strip()
        if not adopter:
            raise ValueError("Adopter name cannot be empty.")
        return adopter

    def __str__(self) -> str:
        """Overloaded string representation summarizing occupancy."""
        return (
            f"Shelter: {self.occupied_count()} animals in "
            f"{len(self.kennels)}/{self.capacity} kennels"
        )
