"""Shelter package — capacity-limited kennels with reservations and waiting lists."""
from shelter.records import (
    AdoptionRecord,
    AnimalInfo,
    IntakeResult,
    PendingRequest,
    Reservation,
)
from shelter.shelter import Shelter

__all__ = [
    "Shelter",
    "AdoptionRecord",
    "AnimalInfo",
    "IntakeResult",
    "PendingRequest",
    "Reservation",
]
