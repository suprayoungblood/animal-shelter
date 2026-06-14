"""Shelter class — owns a capacity-limited collection of kennels.

Rules enforced here:
  - The constructor sets the kennel capacity; once reached, no new
    kennels can be created.
  - Incoming animals always reuse an empty kennel when one exists;
    a new kennel is only built when none are empty.
  - A walk-in adoption removes an available animal immediately; else the
    adopter joins a per-type waiting list (FIFO). A new animal whose type
    has waiting adopters is auto-reserved for the first in line and held
    as a pending pickup until confirmed.
"""
from datetime import datetime

from animals import ANIMAL_TYPES, Animal
from kennel import Kennel
from kennel.kennel import validate_animal
from shelter.records import (
    AdoptionRecord,
    AnimalInfo,
    IntakeResult,
    PendingRequest,
    Reservation,
)

# Case-insensitive lookup table: 'dog' -> 'Dog'. Plain data structure,
# derived from the registry so new animal types need no changes here.
_TYPE_LOOKUP: dict[str, str] = {name.casefold(): name for name in ANIMAL_TYPES}


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
        self.reservations: list[Reservation] = []
        self.adoptions: list[AdoptionRecord] = []

    def is_full(self) -> bool:
        """Return True when no more kennels can be added."""
        return len(self.kennels) >= self.capacity

    def occupied_count(self) -> int:
        """Return how many kennels currently hold an animal."""
        return sum(1 for kennel in self.kennels if not kennel.is_empty())

    def add_animal(self, animal: Animal) -> IntakeResult:
        """Take in an animal and house it, reusing an empty kennel first.

        If adopters are waiting for this type, the animal is auto-reserved
        for the first in line and held as a pending pickup.

        :raises TypeError: If the object is not a registered animal type.
        :raises ValueError: If every kennel is occupied and the shelter is full.
        """
        validate_animal(animal)
        kennel = self._find_empty_kennel() or self._build_kennel()
        kennel.add_animal(animal)
        number = self.kennels.index(kennel) + 1
        reserved_for = self._auto_match(number, type(animal).__name__)
        return IntakeResult(number, reserved_for)

    def adopt(self, animal_type: str, adopter: str) -> Animal | None:
        """Walk-in adoption: take an available animal of a type out now.

        Reserved animals are not offered. When none are available, the
        adopter joins the waiting list. Returns the adopted animal, or
        None if the adopter was waitlisted (type matching is case-insensitive).

        :raises ValueError: If the type is unknown or the adopter name is blank.
        """
        normalized = self._normalize_type(animal_type)
        adopter = self._validated_adopter(adopter)
        kennel = self._find_available_kennel_holding(normalized)
        if kennel is None:
            self.waiting_list[normalized].append(adopter)
            return None
        animal = kennel.remove_animal()
        self._record_adoption(animal, adopter, from_waiting_list=False)
        return animal

    def pending_requests(self) -> list[PendingRequest]:
        """Return every reservation awaiting pickup, with live animal info."""
        requests = []
        for reservation in self.reservations:
            animal = self.kennels[reservation.kennel_number - 1].animal
            requests.append(
                PendingRequest(
                    reservation.kennel_number,
                    type(animal).__name__,
                    animal.name,
                    reservation.adopter,
                    reservation.from_waiting_list,
                )
            )
        return requests

    def confirm_pickup(self, kennel_number: int) -> AdoptionRecord:
        """Finalize a pending reservation and log the completed adoption.

        :raises ValueError: If the kennel has no pending reservation.
        """
        reservation = self._require_reservation(kennel_number)
        animal = self._kennel_at(kennel_number).remove_animal()
        self.reservations.remove(reservation)
        self._record_adoption(
            animal, reservation.adopter, from_waiting_list=reservation.from_waiting_list
        )
        return self.adoptions[-1]

    def cancel_reservation(self, kennel_number: int) -> str:
        """Cancel a pending pickup; the animal becomes available again.

        The freed animal is immediately re-matched to the next person
        waiting for its type, if any, so no one in line is skipped.
        Raises ValueError if the kennel has no pending reservation.
        """
        reservation = self._require_reservation(kennel_number)
        self.reservations.remove(reservation)
        animal_type = self._kennel_at(kennel_number).get_animal_type()
        self._auto_match(kennel_number, animal_type)
        return reservation.adopter

    def get_animal_info(self, kennel_number: int) -> AnimalInfo:
        """Return a snapshot of one kennel (raises ValueError if invalid)."""
        kennel = self._kennel_at(kennel_number)
        if kennel.is_empty():
            return AnimalInfo(kennel_number, "Empty", None, "Empty")
        reservation = self._reservation_for(kennel_number)
        return AnimalInfo(
            kennel_number,
            "Reserved" if reservation else "Available",
            reservation.adopter if reservation else None,
            str(kennel.animal),
        )

    def replace_animal(self, kennel_number: int, animal: Animal) -> Animal:
        """Swap a kennel's occupant for a corrected one (data fix).

        Not an adoption: nothing is logged and any reservation is kept.

        :raises TypeError: If the replacement is not an Animal.
        :raises ValueError: If the kennel number is invalid or empty.
        """
        validate_animal(animal)
        kennel = self._kennel_at(kennel_number)
        replaced = kennel.remove_animal()
        kennel.add_animal(animal)
        return replaced

    def remove_animal(self, kennel_number: int) -> Animal:
        """Remove an animal added by mistake (data fix, not an adoption).

        Any pending reservation on the kennel is dropped.

        :raises ValueError: If the kennel number is invalid or already empty.
        """
        animal = self._kennel_at(kennel_number).remove_animal()
        reservation = self._reservation_for(kennel_number)
        if reservation is not None:
            self.reservations.remove(reservation)
        return animal

    def rename_waiting_adopter(
        self, animal_type: str, position: int, new_name: str
    ) -> None:
        """Correct a waitlisted adopter's name, keeping their place in line."""
        names = self.waiting_list[self._normalize_type(animal_type)]
        names[self._validated_position(names, position)] = (
            self._validated_adopter(new_name)
        )

    def remove_waiting_adopter(self, animal_type: str, position: int) -> str:
        """Remove an adopter from a waiting list (withdrawal or mistake)."""
        names = self.waiting_list[self._normalize_type(animal_type)]
        return names.pop(self._validated_position(names, position))

    def _auto_match(self, kennel_number: int, animal_type: str) -> str | None:
        """Reserve a kennel for the next waiting adopter, if any."""
        adopter = self._pop_waiting_adopter(animal_type)
        if adopter is not None:
            self.reservations.append(Reservation(kennel_number, adopter, True))
        return adopter

    def _pop_waiting_adopter(self, animal_type: str) -> str | None:
        """Dequeue the first adopter waiting for this type, if any."""
        waiting = self.waiting_list[animal_type]
        return waiting.pop(0) if waiting else None

    def _record_adoption(
        self, animal: Animal, adopter: str, from_waiting_list: bool
    ) -> None:
        """Append a completed adoption to the shelter's log, time-stamped now."""
        self.adoptions.append(
            AdoptionRecord(
                type(animal).__name__, animal.name, adopter,
                from_waiting_list, datetime.now(),
            )
        )

    def _reserved_numbers(self) -> set[int]:
        """Return the 1-based numbers of all currently reserved kennels."""
        return {reservation.kennel_number for reservation in self.reservations}

    def _reservation_for(self, kennel_number: int) -> Reservation | None:
        """Return the reservation on a kennel, or None."""
        return next(
            (r for r in self.reservations if r.kennel_number == kennel_number),
            None,
        )

    def _require_reservation(self, kennel_number: int) -> Reservation:
        """Return the reservation on a kennel or raise ValueError."""
        self._kennel_at(kennel_number)
        reservation = self._reservation_for(kennel_number)
        if reservation is None:
            raise ValueError(f"Kennel #{kennel_number} has no pending request.")
        return reservation

    def _find_empty_kennel(self) -> Kennel | None:
        """Return the first empty kennel, or None when all are occupied."""
        return next((kennel for kennel in self.kennels if kennel.is_empty()), None)

    def _find_available_kennel_holding(self, animal_type: str) -> Kennel | None:
        """Return the first unreserved kennel housing the type, or None."""
        reserved = self._reserved_numbers()
        for number, kennel in enumerate(self.kennels, start=1):
            if number not in reserved and kennel.get_animal_type() == animal_type:
                return kennel
        return None

    def _build_kennel(self) -> Kennel:
        """Add a new empty kennel, enforcing the capacity limit."""
        if self.is_full():
            raise ValueError(
                f"Shelter is at capacity ({self.capacity} kennels); "
                "no new kennels can be added."
            )
        kennel = Kennel()
        self.kennels.append(kennel)
        return kennel

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
            raise ValueError(f"Position must be between 1 and {len(names)}.")
        return position - 1

    @staticmethod
    def _normalize_type(animal_type: str) -> str:
        """Map user input to a canonical type name or raise ValueError."""
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
        pending = len(self.reservations)
        suffix = f", {pending} pending pickup(s)" if pending else ""
        return (
            f"Shelter: {self.occupied_count()} animals in "
            f"{len(self.kennels)}/{self.capacity} kennels{suffix}"
        )
