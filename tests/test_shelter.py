"""Unit tests for the Shelter class."""
import unittest

from animals import Bird, Cat, Dog
from shelter import Shelter


class TestShelterConstruction(unittest.TestCase):
    """Tests for the constructor and capacity rule."""

    def test_constructor_sets_capacity(self):
        """The constructor stores the kennel capacity."""
        self.assertEqual(Shelter(5).capacity, 5)

    def test_constructor_starts_empty(self):
        """A new shelter has no kennels, reservations, or adoptions."""
        shelter = Shelter(5)
        self.assertEqual(shelter.kennels, [])
        self.assertEqual(shelter.reservations, [])
        self.assertEqual(shelter.adoptions, [])

    def test_constructor_rejects_non_positive_capacity(self):
        """Zero or negative capacities raise ValueError."""
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                Shelter(bad)

    def test_constructor_rejects_non_integer_capacity(self):
        """Non-integer capacities raise ValueError."""
        for bad in ("5", 2.5, True, None):
            with self.assertRaises(ValueError):
                Shelter(bad)


class TestShelterIntake(unittest.TestCase):
    """Tests for adding animals and kennel reuse."""

    def test_add_animal_builds_kennel_when_none_empty(self):
        """A kennel is created when an animal arrives and none are empty."""
        shelter = Shelter(3)
        result = shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        self.assertEqual(result.kennel_number, 1)
        self.assertIsNone(result.reserved_for)
        self.assertEqual(len(shelter.kennels), 1)

    def test_add_animal_reuses_empty_kennel(self):
        """An empty kennel is filled before a new kennel is built."""
        shelter = Shelter(3)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        shelter.adopt("Dog", "Avery")
        result = shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        self.assertEqual(result.kennel_number, 1)
        self.assertEqual(len(shelter.kennels), 1)

    def test_add_animal_rejected_at_capacity(self):
        """Once capacity is reached and all kennels are full, intake fails."""
        shelter = Shelter(1)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        with self.assertRaises(ValueError):
            shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))

    def test_add_animal_rejects_invalid_type(self):
        """Objects that are not registered animals raise TypeError."""
        with self.assertRaises(TypeError):
            Shelter(1).add_animal("not an animal")


class TestWalkInAdoption(unittest.TestCase):
    """Tests for immediate walk-in adoptions and the waiting list."""

    def setUp(self):
        """Create a shelter housing one dog and one bird."""
        self.shelter = Shelter(3)
        self.dog = Dog("Charlie", 7, "Golden Retriever")
        self.shelter.add_animal(self.dog)
        self.shelter.add_animal(Bird("Tweety", 1, 6.5))

    def test_adopt_returns_and_removes_the_animal(self):
        """Adopting an available type returns it and frees the kennel."""
        self.assertIs(self.shelter.adopt("Dog", "Avery"), self.dog)
        self.assertTrue(self.shelter.kennels[0].is_empty())
        self.assertEqual(len(self.shelter.kennels), 2)

    def test_walk_in_adoption_is_logged_immediately(self):
        """A walk-in adoption is recorded as not from the waiting list."""
        self.shelter.adopt("Dog", "Avery")
        record = self.shelter.adoptions[0]
        self.assertEqual(record.adopter, "Avery")
        self.assertFalse(record.from_waiting_list)

    def test_adopt_is_case_insensitive(self):
        """Type matching uses a lookup table, not exact casing."""
        self.assertIs(self.shelter.adopt("dog", "Avery"), self.dog)

    def test_adopt_missing_type_joins_waiting_list(self):
        """Requesting an absent type waitlists the adopter and returns None."""
        self.assertIsNone(self.shelter.adopt("Cat", "Blake"))
        self.assertEqual(self.shelter.waiting_list["Cat"], ["Blake"])

    def test_reserved_animal_is_not_offered_to_walk_ins(self):
        """A reserved animal cannot be taken by a later walk-in."""
        self.shelter.adopt("Cat", "Blake")              # waitlisted
        self.shelter.add_animal(Cat("Luna", 5, "Tabby"))  # reserved for Blake
        self.assertIsNone(self.shelter.adopt("Cat", "Casey"))
        self.assertEqual(self.shelter.waiting_list["Cat"], ["Casey"])

    def test_adopt_rejects_unknown_type(self):
        """An unregistered animal type raises ValueError."""
        with self.assertRaises(ValueError):
            self.shelter.adopt("Dragon", "Avery")

    def test_adopt_rejects_blank_adopter(self):
        """A blank adopter name raises ValueError."""
        with self.assertRaises(ValueError):
            self.shelter.adopt("Dog", "   ")


class TestReservations(unittest.TestCase):
    """Tests for auto-reservation and the pending-pickup workflow."""

    def setUp(self):
        """Create a shelter with one adopter waiting for a Cat."""
        self.shelter = Shelter(3)
        self.shelter.adopt("Cat", "Blake")

    def test_arrival_reserves_for_first_waiter(self):
        """A matching arrival is housed and reserved, not adopted yet."""
        result = self.shelter.add_animal(Cat("Luna", 5, "Tabby"))
        self.assertEqual(result.reserved_for, "Blake")
        self.assertEqual(len(self.shelter.kennels), 1)
        self.assertEqual(self.shelter.waiting_list["Cat"], [])
        self.assertEqual(self.shelter.adoptions, [])

    def test_pending_requests_lists_the_reservation(self):
        """The pending list reports the held animal and its adopter."""
        self.shelter.add_animal(Cat("Luna", 5, "Tabby"))
        pending = self.shelter.pending_requests()
        self.assertEqual(len(pending), 1)
        self.assertEqual(
            (pending[0].animal_name, pending[0].adopter, pending[0].from_waiting_list),
            ("Luna", "Blake", True),
        )

    def test_confirm_pickup_completes_and_frees_kennel(self):
        """Confirming a pickup logs the adoption and empties the kennel."""
        self.shelter.add_animal(Cat("Luna", 5, "Tabby"))
        record = self.shelter.confirm_pickup(1)
        self.assertEqual(record.adopter, "Blake")
        self.assertTrue(record.from_waiting_list)
        self.assertTrue(self.shelter.kennels[0].is_empty())
        self.assertEqual(self.shelter.pending_requests(), [])

    def test_confirm_without_reservation_raises(self):
        """Confirming a kennel with no reservation raises ValueError."""
        self.shelter.adopt("Dog", "Avery")  # waitlist, no animal housed
        self.shelter.waiting_list["Dog"].clear()
        self.shelter.add_animal(Dog("Rex", 3, "Beagle"))  # housed, no reservation
        with self.assertRaises(ValueError):
            self.shelter.confirm_pickup(1)

    def test_cancel_returns_animal_to_available(self):
        """Cancelling clears the reservation and reopens the animal."""
        self.shelter.add_animal(Cat("Luna", 5, "Tabby"))
        self.assertEqual(self.shelter.cancel_reservation(1), "Blake")
        self.assertEqual(self.shelter.pending_requests(), [])
        self.assertIsNotNone(self.shelter.adopt("Cat", "Casey"))

    def test_cancel_rematches_next_waiter(self):
        """After a cancel, the next person in line is auto-reserved."""
        self.shelter.adopt("Cat", "Casey")  # Blake then Casey waiting
        self.shelter.add_animal(Cat("Luna", 5, "Tabby"))  # reserved for Blake
        self.shelter.cancel_reservation(1)
        pending = self.shelter.pending_requests()
        self.assertEqual(pending[0].adopter, "Casey")


class TestAnimalInfo(unittest.TestCase):
    """Tests for the get_animal_info lookup."""

    def setUp(self):
        """Create a shelter with one housed dog."""
        self.shelter = Shelter(3)
        self.shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))

    def test_available_animal_info(self):
        """An unreserved animal reports Available with its description."""
        info = self.shelter.get_animal_info(1)
        self.assertEqual(info.status, "Available")
        self.assertIsNone(info.reserved_for)
        self.assertIn("Charlie", info.description)

    def test_reserved_animal_info(self):
        """A reserved animal reports Reserved and the adopter."""
        self.shelter.adopt("Cat", "Blake")
        self.shelter.add_animal(Cat("Luna", 5, "Tabby"))
        info = self.shelter.get_animal_info(2)
        self.assertEqual(info.status, "Reserved")
        self.assertEqual(info.reserved_for, "Blake")

    def test_invalid_kennel_raises(self):
        """An out-of-range kennel number raises ValueError."""
        with self.assertRaises(ValueError):
            self.shelter.get_animal_info(99)


class TestCorrections(unittest.TestCase):
    """Tests for fixing data-entry mistakes (not adoptions)."""

    def setUp(self):
        """Create a shelter housing one dog, with one waiting adopter."""
        self.shelter = Shelter(3)
        self.shelter.add_animal(Dog("Charlei", 7, "Golden Retriever"))
        self.shelter.adopt("Cat", "Blkae")

    def test_replace_animal_swaps_in_place(self):
        """replace_animal corrects the occupant and keeps the kennel."""
        fixed = Dog("Charlie", 7, "Golden Retriever")
        replaced = self.shelter.replace_animal(1, fixed)
        self.assertEqual(replaced.name, "Charlei")
        self.assertIs(self.shelter.kennels[0].animal, fixed)

    def test_replace_animal_is_not_logged(self):
        """A correction never appears in the adoption log."""
        self.shelter.replace_animal(1, Dog("Charlie", 7, "Golden Retriever"))
        self.assertEqual(self.shelter.adoptions, [])

    def test_remove_animal_frees_kennel_without_logging(self):
        """remove_animal empties the kennel and skips the adoption log."""
        removed = self.shelter.remove_animal(1)
        self.assertEqual(removed.name, "Charlei")
        self.assertTrue(self.shelter.kennels[0].is_empty())
        self.assertEqual(self.shelter.adoptions, [])

    def test_remove_animal_drops_reservation(self):
        """Removing a reserved animal also drops its pending reservation."""
        self.shelter.add_animal(Cat("Luna", 5, "Tabby"))  # reserved for Blkae
        self.shelter.remove_animal(2)
        self.assertEqual(self.shelter.pending_requests(), [])

    def test_invalid_kennel_numbers_raise(self):
        """Out-of-range or non-integer kennel numbers raise ValueError."""
        for bad in (0, 2, -1, "1", True):
            with self.assertRaises(ValueError):
                self.shelter.remove_animal(bad)

    def test_rename_waiting_adopter_keeps_position(self):
        """Renaming corrects the name without changing line order."""
        self.shelter.adopt("Cat", "Casey")
        self.shelter.rename_waiting_adopter("Cat", 1, "Blake")
        self.assertEqual(self.shelter.waiting_list["Cat"], ["Blake", "Casey"])

    def test_remove_waiting_adopter(self):
        """Removing returns the name and shortens the line."""
        removed = self.shelter.remove_waiting_adopter("Cat", 1)
        self.assertEqual(removed, "Blkae")
        self.assertEqual(self.shelter.waiting_list["Cat"], [])

    def test_invalid_waiting_positions_raise(self):
        """Out-of-range positions and blank names raise ValueError."""
        with self.assertRaises(ValueError):
            self.shelter.remove_waiting_adopter("Cat", 2)
        with self.assertRaises(ValueError):
            self.shelter.rename_waiting_adopter("Cat", 1, "   ")


class TestShelterReporting(unittest.TestCase):
    """Tests for occupancy reporting helpers."""

    def test_occupied_count_ignores_empty_kennels(self):
        """occupied_count only counts kennels holding an animal."""
        shelter = Shelter(3)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        shelter.adopt("Cat", "Avery")
        self.assertEqual(shelter.occupied_count(), 1)

    def test_str_summarizes_occupancy(self):
        """__str__ reports animals, kennels, and capacity."""
        shelter = Shelter(3)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        self.assertEqual(str(shelter), "Shelter: 1 animals in 1/3 kennels")

    def test_str_notes_pending_pickups(self):
        """__str__ mentions pending pickups when reservations exist."""
        shelter = Shelter(3)
        shelter.adopt("Dog", "Avery")
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        self.assertIn("1 pending pickup", str(shelter))


if __name__ == "__main__":
    unittest.main()
