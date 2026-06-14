"""Plain data records returned by the Shelter.

Kept as immutable NamedTuples so callers (the CLI and GUI) get
self-documenting results without depending on Shelter internals.
"""
from typing import NamedTuple


class IntakeResult(NamedTuple):
    """Outcome of taking in an animal.

    kennel_number: 1-based kennel the animal was housed in.
    reserved_for: adopter the animal was auto-reserved for (a waitlist
        match), or None when it is simply available.
    """

    kennel_number: int
    reserved_for: str | None


class PendingRequest(NamedTuple):
    """A reservation awaiting pickup confirmation."""

    kennel_number: int
    animal_type: str
    animal_name: str
    adopter: str
    from_waiting_list: bool


class AnimalInfo(NamedTuple):
    """A snapshot of one kennel's occupant and status."""

    kennel_number: int
    status: str            # "Available", "Reserved", or "Empty"
    reserved_for: str | None
    description: str        # str(animal) or "Empty"


class AdoptionRecord(NamedTuple):
    """One completed adoption, kept in the shelter's log."""

    animal_type: str
    animal_name: str
    adopter: str
    from_waiting_list: bool


class Reservation(NamedTuple):
    """An animal held in its kennel for a named adopter until pickup."""

    kennel_number: int
    adopter: str
    from_waiting_list: bool
